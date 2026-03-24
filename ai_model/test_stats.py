"""
Train a feature-based classifier on the real/fake dataset.
Uses 15 features including face-region stats, color histograms, texture.
Saves to models/deepfake_features.npz
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageChops
import numpy as np, io, glob, cv2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("[TRAIN] Loading dataset...")
real_imgs = glob.glob('datasets/deepfake_images/real_vs_fake/real-vs-fake/test/real/*.jpg')[:3000]
fake_imgs = glob.glob('datasets/deepfake_images/real_vs_fake/real-vs-fake/test/fake/*.jpg')[:3000]
print(f"[TRAIN] Real: {len(real_imgs)}, Fake: {len(fake_imgs)}")

def extract_features(path):
    with open(path, 'rb') as f: buf = f.read()
    img = np.array(Image.open(io.BytesIO(buf)).convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    h, w = gray.shape

    feats = []

    # 1. Laplacian variance (sharpness)
    feats.append(float(cv2.Laplacian(gray, cv2.CV_32F).var()))

    # 2. ELA at quality 95
    pil = Image.fromarray(img)
    b = io.BytesIO(); pil.save(b, 'JPEG', quality=95); b.seek(0)
    ela_arr = np.array(ImageChops.difference(pil.convert('RGB'), Image.open(b).convert('RGB'))).astype(np.float32)
    feats.append(float(ela_arr.mean()))
    feats.append(float(ela_arr.std()))

    # 3. Chroma variance
    r = img[:,:,0].astype(np.float32)
    g = img[:,:,1].astype(np.float32)
    b_ch = img[:,:,2].astype(np.float32)
    lum = 0.299*r + 0.587*g + 0.114*b_ch
    feats.append(float(np.var(r-lum) + np.var(g-lum) + np.var(b_ch-lum)))

    # 4. Noise std (median residual)
    med = cv2.medianBlur(gray.astype(np.uint8), 3).astype(np.float32)
    noise = gray - med
    feats.append(float(np.std(noise)))

    # 5. Gradient magnitude mean + std
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    grad_mag = np.sqrt(gx**2 + gy**2)
    feats.append(float(grad_mag.mean()))
    feats.append(float(grad_mag.std()))

    # 6. Color histogram entropy per channel
    for ch in range(3):
        hist, _ = np.histogram(img[:,:,ch].flatten(), bins=64, range=(0,256))
        hist = hist / (hist.sum() + 1e-6)
        entropy = float(-np.sum(hist * np.log2(hist + 1e-10)))
        feats.append(entropy)

    # 7. Center vs edge sharpness ratio
    cy, cx = h//2, w//2
    ch_r, cw_r = max(1,h//6), max(1,w//6)
    lap = np.abs(cv2.Laplacian(gray, cv2.CV_32F))
    center_sharp = lap[cy-ch_r:cy+ch_r, cx-cw_r:cx+cw_r].mean()
    brd = max(1, min(h,w)//8)
    edge_sharp = np.concatenate([lap[:brd,:].flatten(), lap[h-brd:,:].flatten(),
                                  lap[:,:brd].flatten(), lap[:,w-brd:].flatten()]).mean()
    feats.append(float(center_sharp / (edge_sharp + 1e-6)))

    # 8. Face region skin smoothness
    faces = face_cascade.detectMultiScale(gray.astype(np.uint8), 1.1, 4, minSize=(40,40))
    if len(faces) > 0:
        fx, fy, fw, fh = faces[0]
        face_gray = gray[fy:fy+fh, fx:fx+fw]
        blurred = cv2.GaussianBlur(face_gray, (3,3), 0)
        skin_tex = float(np.std(face_gray - blurred))
    else:
        blurred = cv2.GaussianBlur(gray, (3,3), 0)
        skin_tex = float(np.std(gray - blurred))
    feats.append(skin_tex)

    # 9. DCT block uniformity
    resized = cv2.resize(gray, (64, 64))
    block_highs = []
    for i in range(0, 64, 8):
        for j in range(0, 64, 8):
            dct = cv2.dct(resized[i:i+8, j:j+8])
            block_highs.append(float(np.sum(np.abs(dct[4:, 4:]))))
    feats.append(float(np.std(block_highs) / (np.mean(block_highs) + 1e-6)))

    return feats

# Extract
X, y = [], []
print("[TRAIN] Extracting real features...")
for i, p in enumerate(real_imgs):
    try:
        X.append(extract_features(p)); y.append(0)
        if (i+1) % 500 == 0: print(f"  {i+1}/{len(real_imgs)}")
    except: pass

print("[TRAIN] Extracting fake features...")
for i, p in enumerate(fake_imgs):
    try:
        X.append(extract_features(p)); y.append(1)
        if (i+1) % 500 == 0: print(f"  {i+1}/{len(fake_imgs)}")
    except: pass

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)
print(f"[TRAIN] Samples: {len(X)}")

# Normalize
feat_mean = X.mean(axis=0)
feat_std  = X.std(axis=0) + 1e-6
X_norm = (X - feat_mean) / feat_std

# Split
np.random.seed(42)
idx = np.random.permutation(len(X_norm))
split = int(len(idx) * 0.8)
X_tr, y_tr = X_norm[idx[:split]], y[idx[:split]]
X_val, y_val = X_norm[idx[split:]], y[idx[split:]]

def sigmoid(z): return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))

# Train with momentum
n = X_tr.shape[1]
w = np.zeros(n, dtype=np.float64)
b = 0.0
vw = np.zeros(n); vb = 0.0
lr = 0.1; lam = 0.001; mom = 0.9
best_acc = 0; best_w = w.copy(); best_b = b

print("[TRAIN] Training...")
for epoch in range(1000):
    z = X_tr @ w + b
    err = sigmoid(z) - y_tr
    gw = (X_tr.T @ err) / len(y_tr) + lam * w
    gb = err.mean()
    vw = mom*vw - lr*gw
    vb = mom*vb - lr*gb
    w += vw; b += vb

    if (epoch+1) % 100 == 0:
        val_acc = (((sigmoid(X_val @ w + b) > 0.5).astype(int)) == y_val).mean()
        tr_acc  = (((sigmoid(X_tr  @ w + b) > 0.5).astype(int)) == y_tr ).mean()
        print(f"  Epoch {epoch+1}: train={tr_acc:.3f} val={val_acc:.3f}")
        if val_acc > best_acc:
            best_acc = val_acc; best_w = w.copy(); best_b = b

print(f"[TRAIN] Best val accuracy: {best_acc:.3f}")

os.makedirs('models', exist_ok=True)
np.savez('models/deepfake_features.npz',
         w=best_w, b=np.array([best_b]),
         feat_mean=feat_mean, feat_std=feat_std)
print("[TRAIN] Saved to models/deepfake_features.npz")

# Confusion matrix
vp = (sigmoid(X_val @ best_w + best_b) > 0.5).astype(int)
tp = ((vp==1)&(y_val==1)).sum(); tn = ((vp==0)&(y_val==0)).sum()
fp = ((vp==1)&(y_val==0)).sum(); fn = ((vp==0)&(y_val==1)).sum()
print(f"[EVAL] TP={tp} TN={tn} FP={fp} FN={fn}")
print(f"[EVAL] Precision={tp/(tp+fp+1e-6):.3f} Recall={tp/(tp+fn+1e-6):.3f} Acc={best_acc:.3f}")
print(f"[EVAL] Feature weights: {dict(zip(['lap','ela_m','ela_s','chroma','noise','grad_m','grad_s','h_r','h_g','h_b','sharp_ratio','skin','dct_cv'], [round(float(x),3) for x in best_w]))}")
