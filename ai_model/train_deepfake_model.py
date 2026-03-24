"""
Train deepfake feature classifier from the real_vs_fake dataset.
Extracts 13 signal features per image, trains logistic regression,
saves weights to models/deepfake_features.npz

Dataset expected at:
  ai_model/datasets/deepfake_images/real_vs_fake/real-vs-fake/test/real/
  ai_model/datasets/deepfake_images/real_vs_fake/real-vs-fake/test/fake/
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageChops
import io
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

DATASET_REAL = 'datasets/deepfake_images/real_vs_fake/real-vs-fake/test/real'
DATASET_FAKE = 'datasets/deepfake_images/real_vs_fake/real-vs-fake/test/fake'
OUTPUT_PATH  = 'models/deepfake_features.npz'

# How many images to use per class (balance dataset, cap for speed)
MAX_PER_CLASS = 4000


def extract_features(img_path):
    """Extract 13 numerical features from a single image."""
    try:
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            return None
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (256, 256))
        gray    = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)

        # ── 1. Laplacian variance (sharpness) ──
        lap_var = float(cv2.Laplacian(gray, cv2.CV_32F).var())

        # ── 2. ELA mean at q95 ──
        pil = Image.fromarray(img_rgb)
        buf = io.BytesIO(); pil.save(buf, 'JPEG', quality=95); buf.seek(0)
        ela95 = np.array(ImageChops.difference(
            pil.convert('RGB'), Image.open(buf).convert('RGB')
        )).astype(np.float32)
        ela95_mean = float(ela95.mean())
        ela95_std  = float(ela95.std())

        # ── 3. ELA mean at q75 ──
        buf2 = io.BytesIO(); pil.save(buf2, 'JPEG', quality=75); buf2.seek(0)
        ela75 = np.array(ImageChops.difference(
            pil.convert('RGB'), Image.open(buf2).convert('RGB')
        )).astype(np.float32)
        ela75_mean = float(ela75.mean())
        ela75_std  = float(ela75.std())

        # ── 4. Chroma variance ──
        r = img_rgb[:,:,0].astype(np.float32)
        g = img_rgb[:,:,1].astype(np.float32)
        b = img_rgb[:,:,2].astype(np.float32)
        lum = 0.299*r + 0.587*g + 0.114*b
        chroma_var = float(np.var(r-lum) + np.var(g-lum) + np.var(b-lum))

        # ── 5. Noise floor ──
        med       = cv2.medianBlur(gray.astype(np.uint8), 3).astype(np.float32)
        noise_std = float(np.std(gray - med))
        noise_mean = float(np.mean(np.abs(gray - med)))

        # ── 6. DCT high-freq coefficient variation ──
        resized = cv2.resize(gray, (64, 64))
        block_highs = [float(np.sum(np.abs(cv2.dct(resized[i:i+8, j:j+8])[4:, 4:])))
                       for i in range(0,64,8) for j in range(0,64,8)]
        dct_cv   = float(np.std(block_highs) / (np.mean(block_highs) + 1e-6))
        dct_mean = float(np.mean(block_highs))

        # ── 7. Local Binary Pattern variance (texture) ──
        gray8 = gray.astype(np.uint8)
        lbp_var = float(np.var(gray8 - cv2.GaussianBlur(gray8, (5,5), 0)))

        # ── 8. Color channel correlation (GAN images tend to have higher correlation) ──
        rg_corr = float(np.corrcoef(r.flatten(), g.flatten())[0,1])
        rb_corr = float(np.corrcoef(r.flatten(), b.flatten())[0,1])

        return [
            lap_var, ela95_mean, ela95_std,
            ela75_mean, ela75_std,
            chroma_var, noise_std, noise_mean,
            dct_cv, dct_mean, lbp_var,
            rg_corr, rb_corr
        ]
    except Exception as e:
        return None


def load_images_from_dir(directory, label, max_count):
    files = [f for f in os.listdir(directory)
             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    files = files[:max_count]
    features, labels = [], []
    for i, fname in enumerate(files):
        path = os.path.join(directory, fname)
        feat = extract_features(path)
        if feat is not None:
            features.append(feat)
            labels.append(label)
        if (i+1) % 200 == 0:
            print(f"  [{label_name(label)}] {i+1}/{len(files)} processed...")
    return features, labels


def label_name(l):
    return 'REAL' if l == 0 else 'FAKE'


def main():
    print("=" * 60)
    print("DEEPFAKE FEATURE CLASSIFIER TRAINING")
    print("=" * 60)

    if not os.path.exists(DATASET_REAL) or not os.path.exists(DATASET_FAKE):
        print(f"[ERROR] Dataset not found.")
        print(f"  Expected: {DATASET_REAL}")
        print(f"  Expected: {DATASET_FAKE}")
        return

    real_count = len(os.listdir(DATASET_REAL))
    fake_count = len(os.listdir(DATASET_FAKE))
    print(f"[INFO] Real images available: {real_count}")
    print(f"[INFO] Fake images available: {fake_count}")
    print(f"[INFO] Using up to {MAX_PER_CLASS} per class")

    print("\n[STEP 1] Extracting features from REAL images...")
    real_feats, real_labels = load_images_from_dir(DATASET_REAL, 0, MAX_PER_CLASS)
    print(f"  Done: {len(real_feats)} real feature vectors")

    print("\n[STEP 2] Extracting features from FAKE images...")
    fake_feats, fake_labels = load_images_from_dir(DATASET_FAKE, 1, MAX_PER_CLASS)
    print(f"  Done: {len(fake_feats)} fake feature vectors")

    X = np.array(real_feats + fake_feats, dtype=np.float32)
    y = np.array(real_labels + fake_labels, dtype=np.int32)
    print(f"\n[INFO] Total samples: {len(X)} (real={len(real_feats)}, fake={len(fake_feats)})")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Normalize
    scaler = StandardScaler()
    X_train_n = scaler.fit_transform(X_train)
    X_test_n  = scaler.transform(X_test)

    print("\n[STEP 3] Training Logistic Regression classifier...")
    clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    clf.fit(X_train_n, y_train)

    y_pred = clf.predict(X_test_n)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[RESULTS] Test Accuracy: {acc*100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))

    # Save weights
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    np.savez(
        OUTPUT_PATH,
        w         = clf.coef_[0].astype(np.float32),
        b         = np.array([clf.intercept_[0]], dtype=np.float32),
        feat_mean = scaler.mean_.astype(np.float32),
        feat_std  = scaler.scale_.astype(np.float32),
    )
    print(f"\n[SAVED] Feature classifier → {OUTPUT_PATH}")
    print("[DONE] Training complete.")


if __name__ == '__main__':
    main()
