import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from models.image_detector import ImageDetector
from PIL import Image
import numpy as np, io, glob

det = ImageDetector()

real_imgs = glob.glob('datasets/deepfake_images/real_vs_fake/real-vs-fake/test/real/*.jpg')[:4]
fake_imgs = glob.glob('datasets/deepfake_images/real_vs_fake/real-vs-fake/test/fake/*.jpg')[:4]

def test(paths, label):
    print("\n=== " + label + " ===")
    for path in paths:
        with open(path, 'rb') as f:
            buf = f.read()
        img_np = np.array(Image.open(io.BytesIO(buf)).convert('RGB'))
        is_df, conf, details = det._analyze_visual_features(img_np, buf)
        s = details['scores']
        w = details['weighted_score']
        print("  " + os.path.basename(path) + " -> deepfake=" + str(is_df) + " conf=" + str(round(conf,2)) + " weighted=" + str(w))
        print("    sharp=" + str(s.get('sharpness','?')) + " ela=" + str(s.get('ela','?')) + " color=" + str(s.get('color','?')))

test(real_imgs, "REAL IMAGES")
test(fake_imgs, "AI/FAKE IMAGES")
