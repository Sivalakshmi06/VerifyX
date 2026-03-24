"""
Train a lightweight feature-based classifier on the real/fake dataset.
Saves model weights to models/deepfake_features.npz
Uses: lap_var, ela_mean, chroma_var, noise_std, grad_mag
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageChops
import numpy as np, io, glob, cv2

print("[TRAIN] Loading dataset...")

real_imgs = glob.glob('datasets/deepfake_images/real_vs_fake/real-vs-fake/test/real/*.jpg')[:2000]
fake_imgs = glob.glob('datasets/deepfake_images/real_vs_fake/real-vs-fake/test/fake/*.jpg')[:2000]

print(f"[TRAIN] Real: {len(real_imgs)}, Fake: {len(fake_imgs)}")

def extract_features(path):
    with open(path, 'rb') as f:
        buf = f.read()
    img = np.array(Image.open(io.BytesIO(buf)).convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)

    # 1. Laplacian variance
    lap_var = float(cv2.Laplacian(gray, cv2.CV_32F).var())

    # 2. ELA at quality 95
    pil = Image.fromarray(img)
    b = io.BytesIO(); pil.save(b, 'JPEG', quality=95); b.seek(0)
    ela = float(np.array(ImageChops.difference(
        pil.convert('RGB'), Image.open(b).convert('RGB')
    )).astype(np.float32).mean())

    # 3. Chroma variance
    r = img[:,:,0].astype(np.float32)
    g = img[:,:,1].astype(np.float32)
    b_ch = img[:,:,2].astype(np.float32)
    lum = 0.299*r + 0.587*g + 0.114*b_ch
    chroma = float(np.var(r-lum) + np.var(g-lum) + np.var(b_ch-lum))

    # 4. Noise std
    med = cv2.medianBlur(gray.astype(np.uint8), 3).astype(np.float32)
    noise_std = float(np.std(gray - med))

    # 5. Gradient magnitude
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    grad = float(np.mean(np.sqrt(gx**2 + gy**2)))

    # 6. High-freq ratio (detail in top 10% frequencies)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    h, w = mag.shape
    center = mag[h//2-h//10:h//2+h//10, w//2-w//10:w//2+w//10].sum()
    total = mag.sum() + 1e-6
    hf_ratio = float(1.0 - center/total)

    # 7. Local contrast std (block-level contrast variation)
    resized = cv2.resize(gray, (64, 64))
    block_contrasts = []
    for i in range(0, 64, 8):
        for j in range(0, 64, 8):
            block = resized[i:i+8, j:j+8]
            block_contrasts.append(float(block.max() - block.min()))
    lc_std = float(np.std(block_contrasts))

    return [lap_var, ela, chroma, noise_std, grad, hf_ratio, lc_std]

# Extract features
X, y = [], []
print("[TRAIN] Extracting real features...")
for i, p in enumerate(real_imgs):
    try:
        X.append(extract_features(p))
        y.append(0)  # 0 = real
        if (i+1) % 200 == 0: print(f"  {i+1}/{len(real_imgs)}")
    except: pass

print("[TRAIN] Extracting fake features...")
for i, p in enumerate(fake_imgs):
    try:
        X.append(extract_features(p))
        y.append(1)  # 1 = fake
        if (i+1) % 200 == 0: print(f"  {i+1}/{len(fake_imgs)}")
    except: pass

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)
print(f"[TRAIN] Total samples: {len(X)} (real={sum(y==0)}, fake={sum(y==1)})")

# Normalize features
feat_mean = X.mean(axis=0)
feat_std  = X.std(axis=0) + 1e-6
X_norm = (X - feat_mean) / feat_std

# Train/val split
np.random.seed(42)
idx = np.random.permutation(len(X_norm))
split = int(len(idx) * 0.8)
tr_idx, val_idx = idx[:split], idx[split:]
X_tr, y_tr = X_norm[tr_idx], y[tr_idx]
X_val, y_val = X_norm[val_idx], y[val_idx]

# Logistic regression with gradient descent
n_feat = X_tr.shape[1]
w = np.zeros(n_feat, dtype=np.float64)
b = 0.0
lr = 0.05
lam = 0.001  # L2 regularization

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))

print("[TRAIN] Training logistic regression...")
best_val_acc = 0
best_w, best_b = w.copy(), b

for epoch in range(500):
    z = X_tr @ w + b
    pred = sigmoid(z)
    err = pred - y_tr
    grad_w = (X_tr.T @ err) / len(y_tr) + lam * w
    grad_b = err.mean()
    w -= lr * grad_w
    b -= lr * grad_b

    if (epoch+1) % 50 == 0:
        val_pred = (sigmoid(X_val @ w + b) > 0.5).astype(int)
        val_acc = (val_pred == y_val).mean()
        tr_pred = (sigmoid(X_tr @ w + b) > 0.5).astype(int)
        tr_acc = (tr_pred == y_tr).mean()
        print(f"  Epoch {epoch+1}: train_acc={tr_acc:.3f} val_acc={val_acc:.3f}")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_w, best_b = w.copy(), b

print(f"[TRAIN] Best val accuracy: {best_val_acc:.3f}")

# Save
os.makedirs('models', exist_ok=True)
np.savez('models/deepfake_features.npz',
         w=best_w, b=np.array([best_b]),
         feat_mean=feat_mean, feat_std=feat_std)
print("[TRAIN] Saved to models/deepfake_features.npz")

# Final evaluation
val_pred = (sigmoid(X_val @ best_w + best_b) > 0.5).astype(int)
tp = ((val_pred==1) & (y_val==1)).sum()
tn = ((val_pred==0) & (y_val==0)).sum()
fp = ((val_pred==1) & (y_val==0)).sum()
fn = ((val_pred==0) & (y_val==1)).sum()
print(f"[EVAL] TP={tp} TN={tn} FP={fp} FN={fn}")
print(f"[EVAL] Precision={tp/(tp+fp+1e-6):.3f} Recall={tp/(tp+fn+1e-6):.3f}")
