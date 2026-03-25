"""
OCR Text Extractor for Images
Primary: EasyOCR (pure Python, no external install needed)
Fallback: pytesseract (if Tesseract is installed)
Supports English and Tamil
"""

import cv2
import numpy as np
from PIL import Image
import io

EASYOCR_AVAILABLE = False
TESSERACT_AVAILABLE = False

# Check pytesseract
try:
    import pytesseract
    import os
    # Set path for Windows
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
    print("[OCR] Tesseract OCR available")
except Exception:
    print("[OCR] Tesseract not installed")

# Check easyocr availability (lazy — don't import at module level to avoid DLL crash in Flask reloader)
try:
    import importlib.util
    if importlib.util.find_spec("easyocr") is not None:
        EASYOCR_AVAILABLE = True
        print("[OCR] EasyOCR package found (will load on first use)")
except Exception:
    pass


class OCRExtractor:
    def __init__(self):
        self._reader_en = None
        self._reader_ta = None

    def _get_reader(self, languages):
        """Lazy-load EasyOCR reader for given language set"""
        if not EASYOCR_AVAILABLE:
            return None
        try:
            import easyocr  # lazy import — avoids DLL crash in Flask reloader
            if 'ta' in languages or 'tam' in languages:
                if self._reader_ta is None:
                    print("[OCR] Loading EasyOCR Tamil+English reader...")
                    self._reader_ta = easyocr.Reader(['en', 'ta'], gpu=False, verbose=False)
                return self._reader_ta
            else:
                if self._reader_en is None:
                    print("[OCR] Loading EasyOCR English reader...")
                    self._reader_en = easyocr.Reader(['en'], gpu=False, verbose=False)
                return self._reader_en
        except Exception as e:
            print(f"[OCR] Failed to load EasyOCR reader: {e}")
            return None

    def extract_text(self, image_file, languages=['eng']):
        """
        Extract text from image.
        Tries EasyOCR first, then pytesseract, then returns error.
        """
        try:
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_np = np.array(image)

            processed = self._preprocess_image(image_np)

            # --- Try EasyOCR ---
            if EASYOCR_AVAILABLE:
                text = self._extract_with_easyocr(processed, image_np)
                if text.strip():
                    detected_lang = self._detect_language(text)
                    print(f"[OCR] EasyOCR extracted: {text[:100]}")
                    return {
                        'text': text.strip(),
                        'confidence': 0.88,
                        'detected_language': detected_lang,
                        'word_count': len(text.split()),
                        'engine': 'easyocr'
                    }

            # --- Try pytesseract ---
            if TESSERACT_AVAILABLE:
                text = self._extract_with_tesseract(processed, languages)
                if text.strip():
                    detected_lang = self._detect_language(text)
                    print(f"[OCR] Tesseract extracted: {text[:100]}")
                    return {
                        'text': text.strip(),
                        'confidence': 0.85,
                        'detected_language': detected_lang,
                        'word_count': len(text.split()),
                        'engine': 'tesseract'
                    }

            return {
                'text': '',
                'confidence': 0.0,
                'error': 'No text could be extracted from the image. Please ensure the image contains clear, readable text.'
            }

        except Exception as e:
            print(f"[OCR ERROR] {e}")
            return {'text': '', 'confidence': 0.0, 'error': str(e)}

    def _extract_with_easyocr(self, processed_np, original_np):
        """Run EasyOCR on the image"""
        try:
            # EasyOCR works best on the original (not binarized) image
            reader = self._get_reader(['en'])
            if reader is None:
                return ''

            # Try original image first
            results = reader.readtext(original_np, detail=0, paragraph=True)
            text = '\n'.join(results)

            # If nothing found, try preprocessed
            if not text.strip():
                results = reader.readtext(processed_np, detail=0, paragraph=True)
                text = '\n'.join(results)

            return text
        except Exception as e:
            print(f"[OCR] EasyOCR error: {e}")
            return ''

    def _extract_with_tesseract(self, processed_np, languages):
        """Run pytesseract on the image"""
        try:
            lang_map = {'eng': 'eng', 'tam': 'tam', 'en': 'eng', 'ta': 'tam'}
            tess_langs = [lang_map.get(l, l) for l in languages]
            lang_string = '+'.join(tess_langs)
            pil_img = Image.fromarray(processed_np)
            return pytesseract.image_to_string(pil_img, lang=lang_string)
        except Exception as e:
            print(f"[OCR] Tesseract error: {e}")
            return ''

    def _preprocess_image(self, image_np):
        """Preprocess for better OCR — resize, grayscale, threshold"""
        h, w = image_np.shape[:2]
        # Scale up small images (OCR works better on larger text)
        if w < 600:
            scale = 600 / w
            image_np = cv2.resize(image_np, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        elif w > 1200:
            scale = 1200 / w
            image_np = cv2.resize(image_np, (int(w * scale), int(h * scale)))

        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # Adaptive threshold works better for screenshots with varied backgrounds
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return thresh

    def _detect_language(self, text):
        if not text:
            return 'unknown'
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        if tamil_chars > english_chars:
            return 'tamil'
        elif english_chars > 0:
            return 'english'
        return 'unknown'

    def extract_and_classify(self, image_file, text_classifier):
        """Extract text from image and classify as fake/real"""
        ocr_result = self.extract_text(image_file)
        if not ocr_result.get('text'):
            return {'success': False, 'message': 'No text found in image', 'ocr_result': ocr_result}

        classification = text_classifier.predict(
            ocr_result['text'],
            ocr_result.get('detected_language', 'en')
        )
        return {
            'success': True,
            'ocr_result': ocr_result,
            'classification': classification,
            'extracted_text': ocr_result['text']
        }
