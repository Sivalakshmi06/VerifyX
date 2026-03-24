"""
Deepfake Image Detector
13-signal ensemble trained on real_vs_fake dataset.
Full-image analysis — face box shown on heatmap only for context.
"""
import cv2
import numpy as np
from PIL import Image, ImageChops
import io
import base64
import os
import tempfile


class ImageDetector:
    def __init__(self):
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self._feat_w = self._feat_b = self._feat_mean = self._feat_std = None
        self._use_feat_model = False
        self._load_feature_model()

    def _load_feature_model(self):
        for path in ['models/deepfake_features.npz', 'ai_model/models/deepfake_features.npz']:
            if os.path.exists(path):
                try:
                    data = np.load(path)
                    self._feat_w    = data['w']
                    self._feat_b    = float(data['b'][0])
                    self._feat_mean = data['feat_mean']
                    self._feat_std  = data['feat_std']
                    self._use_feat_model = True
                    print("[OK] Loaded feature classifier")
                    return
                except Exception as e:
                    print(f"[WARN] Feature model: {e}")
        print("[WARN] No trained feature model found — using heuristic ensemble only")

    # ── PUBLIC ──────────────────────────────────────
    def predict(self, image_file, file_type='image'):
        file_bytes = image_file.read()
        return self._analyze_video(file_bytes) if file_type == 'video' else self._analyze_image(file_bytes)

    # ── IMAGE PIPELINE ───────────────────────────────
    def _analyze_image(self, file_bytes):
        try:
            pil_img  = Image.open(io.BytesIO(file_bytes)).convert('RGB')
            image_np = np.array(pil_img)

            # Detect face (for heatmap overlay only — scoring uses full image)
            face_box = self._detect_face(image_np)

            # Full-image feature extraction + scoring
            score, raw = self._ensemble_score(image_np)
            print(f"[DETECT] ensemble={score:.3f} raw={raw}")

            # Blend with trained LR classifier if available
            if self._use_feat_model:
                lr_prob = self._lr_predict(raw)
                score   = 0.45 * score + 0.55 * lr_prob
                print(f"[DETECT] lr_prob={lr_prob:.3f} blended={score:.3f}")

            is_deepfake = score > 0.50
            dist        = abs(score - 0.50)
            confidence  = float(min(0.93, 0.55 + dist * 1.9))
            deepfake_type = self._classify_type(face_box, score)

            heatmap_b64 = self._generate_heatmap(image_np, face_box, is_deepfake)

            return {
                'prediction':       'deepfake' if is_deepfake else 'authentic',
                'confidence':       confidence,
                'is_deepfake':      bool(is_deepfake),
                'heatmap_url':      f'data:image/png;base64,{heatmap_b64}',
                'method':           'trained_ensemble',
                'analysis_details': {'deepfake_type': deepfake_type}
            }
        except Exception as e:
            import traceback; traceback.print_exc()
            return {'prediction': 'unknown', 'confidence': 0.0,
                    'is_deepfake': False, 'heatmap_url': '', 'error': str(e)}

    # ── FACE DETECTION ───────────────────────────────
    def _detect_face(self, image_np):
        gray  = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        if len(faces) > 0:
            fx, fy, fw, fh = max(faces, key=lambda f: f[2]*f[3])
            h, w = image_np.shape[:2]
            pad_x, pad_y = int(fw*0.20), int(fh*0.20)
            x1 = max(0, fx-pad_x); y1 = max(0, fy-pad_y)
            x2 = min(w, fx+fw+pad_x); y2 = min(h, fy+fh+pad_y)
            print(f"[FACE] Detected at ({x1},{y1})-({x2},{y2})")
            return (x1, y1, x2, y2)
        print("[FACE] No face detected")
        return None

    # ── FULL-IMAGE ENSEMBLE SCORE ────────────────────
    def _ensemble_score(self, image_np):
        """
        Extract 13 features from the FULL image.
        Returns (score 0=real 1=fake, raw dict).
        Calibrated thresholds from training on real_vs_fake dataset.
        """
        img_resized = cv2.resize(image_np, (256, 256))
        gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY).astype(np.float32)

        # 1. Laplacian variance
        lap_var = float(cv2.Laplacian(gray, cv2.CV_32F).var())

        # 2. ELA at q95
        pil = Image.fromarray(img_resized)
        buf = io.BytesIO(); pil.save(buf, 'JPEG', quality=95); buf.seek(0)
        ela95 = np.array(ImageChops.difference(
            pil.convert('RGB'), Image.open(buf).convert('RGB')
        )).astype(np.float32)
        ela95_mean = float(ela95.mean())
        ela95_std  = float(ela95.std())

        # 3. ELA at q75
        buf2 = io.BytesIO(); pil.save(buf2, 'JPEG', quality=75); buf2.seek(0)
        ela75 = np.array(ImageChops.difference(
            pil.convert('RGB'), Image.open(buf2).convert('RGB')
        )).astype(np.float32)
        ela75_mean = float(ela75.mean())
        ela75_std  = float(ela75.std())

        # 4. Chroma variance
        r = img_resized[:,:,0].astype(np.float32)
        g = img_resized[:,:,1].astype(np.float32)
        b = img_resized[:,:,2].astype(np.float32)
        lum = 0.299*r + 0.587*g + 0.114*b
        chroma_var = float(np.var(r-lum) + np.var(g-lum) + np.var(b-lum))

        # 5. Noise floor
        med        = cv2.medianBlur(gray.astype(np.uint8), 3).astype(np.float32)
        noise_std  = float(np.std(gray - med))
        noise_mean = float(np.mean(np.abs(gray - med)))

        # 6. DCT high-freq CV
        resized64 = cv2.resize(gray, (64, 64))
        block_highs = [float(np.sum(np.abs(cv2.dct(resized64[i:i+8, j:j+8])[4:, 4:])))
                       for i in range(0,64,8) for j in range(0,64,8)]
        dct_cv   = float(np.std(block_highs) / (np.mean(block_highs) + 1e-6))
        dct_mean = float(np.mean(block_highs))

        # 7. LBP-style texture variance
        gray8   = gray.astype(np.uint8)
        lbp_var = float(np.var(gray8 - cv2.GaussianBlur(gray8, (5,5), 0)))

        # 8. Color channel correlation
        rg_corr = float(np.corrcoef(r.flatten(), g.flatten())[0,1])
        rb_corr = float(np.corrcoef(r.flatten(), b.flatten())[0,1])

        print(f"[SIGNALS] lap={lap_var:.1f} ela95={ela95_mean:.3f} ela75={ela75_mean:.3f} "
              f"chroma={chroma_var:.1f} noise={noise_std:.3f} dct={dct_cv:.3f} "
              f"lbp={lbp_var:.1f} rg={rg_corr:.3f} rb={rb_corr:.3f}")

        raw = {
            'lap_var': lap_var, 'ela95_mean': ela95_mean, 'ela95_std': ela95_std,
            'ela75_mean': ela75_mean, 'ela75_std': ela75_std,
            'chroma_var': chroma_var, 'noise_std': noise_std, 'noise_mean': noise_mean,
            'dct_cv': dct_cv, 'dct_mean': dct_mean, 'lbp_var': lbp_var,
            'rg_corr': rg_corr, 'rb_corr': rb_corr,
        }

        # Heuristic fallback score (used when no trained model)
        # Calibrated from dataset: fake images tend to have lower ELA, lower noise, higher channel correlation
        s_ela    = float(np.clip((0.37 - ela95_mean) / 0.27, 0, 1))
        s_noise  = float(np.clip((4.2  - noise_std)  / 3.7,  0, 1))
        s_chroma = float(np.clip((998  - chroma_var) / 698,  0, 1))
        s_lap    = float(np.clip((1045 - lap_var)    / 645,  0, 1))
        s_dct    = float(np.clip((1.8  - dct_cv)     / 1.5,  0, 1))
        heuristic = s_ela*0.30 + s_noise*0.25 + s_chroma*0.15 + s_lap*0.20 + s_dct*0.10

        return float(heuristic), raw

    def _lr_predict(self, raw):
        """Run trained logistic regression on 13-feature vector."""
        feats = np.array([
            raw['lap_var'],   raw['ela95_mean'], raw['ela95_std'],
            raw['ela75_mean'],raw['ela75_std'],
            raw['chroma_var'],raw['noise_std'],  raw['noise_mean'],
            raw['dct_cv'],    raw['dct_mean'],   raw['lbp_var'],
            raw['rg_corr'],   raw['rb_corr'],
        ], dtype=np.float32)
        feats_norm = (feats - self._feat_mean) / (self._feat_std + 1e-8)
        z = float(feats_norm @ self._feat_w + self._feat_b)
        return float(1.0 / (1.0 + np.exp(-np.clip(z, -50, 50))))

    def _classify_type(self, face_box, score):
        if score <= 0.50:
            return None
        return 'Face Swap / GAN' if face_box is not None else 'GAN Generated'

    # ── HEATMAP (full image) ─────────────────────────
    def _generate_heatmap(self, image_np, face_box, is_deepfake):
        """
        Full-image ELA heatmap.
        Fake  → JET colormap (red = smooth AI regions)
        Real  → COOL colormap (natural texture variation)
        Face bounding box drawn on top for context.
        """
        try:
            original_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            # ELA at q75 on full image
            pil = Image.fromarray(image_np)
            buf = io.BytesIO(); pil.save(buf, 'JPEG', quality=75); buf.seek(0)
            ela = np.array(
                ImageChops.difference(pil.convert('RGB'), Image.open(buf).convert('RGB'))
            ).astype(np.float32)
            ela_gray = ela.mean(axis=2)

            # Gamma boost + normalize
            ela_amp  = np.power(ela_gray, 0.5)
            ela_norm = cv2.normalize(ela_amp, None, 0.0, 1.0, cv2.NORM_MINMAX)

            # Invert for fake (low ELA = smooth = suspicious = red)
            anomaly      = (1.0 - ela_norm) if is_deepfake else ela_norm
            anomaly_blur = cv2.GaussianBlur(anomaly, (15, 15), 0)
            anomaly_8u   = cv2.equalizeHist((anomaly_blur * 255).astype(np.uint8))

            # Apply colormap to full image
            if is_deepfake:
                heatmap = cv2.applyColorMap(anomaly_8u, cv2.COLORMAP_JET)
            else:
                heatmap = cv2.applyColorMap(anomaly_8u, cv2.COLORMAP_COOL)

            overlay = cv2.addWeighted(original_bgr, 0.45, heatmap, 0.55, 0)

            # Draw face bounding box on top (red=fake, green=real)
            if face_box is not None:
                x1, y1, x2, y2 = face_box
                box_color = (0, 0, 220) if is_deepfake else (0, 180, 0)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, 2)

            _, buf2 = cv2.imencode('.png', overlay)
            return base64.b64encode(buf2).decode('utf-8')

        except Exception as e:
            print(f"[ERROR] Heatmap: {e}")
            return ''

    # ── VIDEO ────────────────────────────────────────
    def _analyze_video(self, video_bytes):
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp.write(video_bytes); tmp_path = tmp.name
            cap = cv2.VideoCapture(tmp_path)
            scores = []
            frame_count = 0
            while frame_count < 10:
                ret, frame = cap.read()
                if not ret: break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                score, _ = self._ensemble_score(frame_rgb)
                scores.append(score)
                frame_count += 1
            cap.release(); os.unlink(tmp_path)
            avg = float(np.mean(scores)) if scores else 0.5
            is_deepfake = avg > 0.50
            dist = abs(avg - 0.50)
            confidence = float(min(0.92, 0.55 + dist * 1.8))
            return {
                'prediction': 'deepfake' if is_deepfake else 'authentic',
                'confidence': confidence, 'is_deepfake': bool(is_deepfake),
                'heatmap_url': '', 'frames_analyzed': frame_count,
                'analysis_details': {}
            }
        except Exception as e:
            print(f"[ERROR] Video: {e}")
            return {'prediction': 'unknown', 'confidence': 0.0,
                    'is_deepfake': False, 'heatmap_url': '', 'error': str(e)}
