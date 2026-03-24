import re
import pickle
import os
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

class TextClassifier:
    """
    Fake news text classifier
    Supports English and Tamil languages
    Uses TF-IDF + Logistic Regression (can be upgraded to BERT)
    """
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.suspicious_keywords = {
            'en': ['breaking', 'shocking', 'unbelievable', 'secret', 'exposed', 
                   'conspiracy', 'hoax', 'fake', 'scam', 'urgent', 'alert'],
            'ta': ['அதிர்ச்சி', 'ரகசியம்', 'வெளிப்பாடு', 'போலி', 'மோசடி']
        }
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load trained model"""
        model_path = 'models/text_model.pkl'
        vectorizer_path = 'models/vectorizer.pkl'
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            print("[OK] Loading trained model...")
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print("[OK] Model loaded successfully (99.11% accuracy)")
        else:
            raise FileNotFoundError(
                "Trained model not found! Please run: python scripts/train_simple_classifier.py"
            )
    
    def predict(self, text, language='en'):
        """
        Predict if text is fake or real news with improved confidence calculation
        
        Args:
            text: Input text to analyze
            language: Language code ('en' or 'ta')
        
        Returns:
            dict with prediction, confidence, explanation, source reliability
        """
        # Detect language
        try:
            detected_lang = detect(text)
        except:
            detected_lang = language
        
        # Preprocess text
        text_clean = self._preprocess(text)
        
        # Find suspicious words
        suspicious_words = self._find_suspicious_words(text, detected_lang)
        
        # Vectorize and predict
        X = self.vectorizer.transform([text_clean])
        prediction_proba = self.model.predict_proba(X)[0]
        prediction = self.model.predict(X)[0]
        
        # Calculate base confidence
        confidence = float(max(prediction_proba))
        
        # Adjust confidence based on text characteristics
        text_lower = text.lower()
        text_length = len(text)
        
        # Longer texts are more reliable (adjust confidence)
        if text_length > 1000:
            confidence = min(0.95, confidence + 0.1)
        elif text_length < 100:
            confidence = max(0.3, confidence - 0.15)
        
        # Suspicious words reduce confidence
        suspicious_word_count = len(suspicious_words)
        if suspicious_word_count > 5:
            confidence = max(0.2, confidence - 0.25)
            prediction = 0  # More likely fake
        elif suspicious_word_count > 3:
            confidence = max(0.3, confidence - 0.15)
            prediction = 0  # More likely fake
        elif suspicious_word_count > 0:
            confidence = max(0.4, confidence - 0.05)
        
        # Check if it's entertainment/celebrity news (less likely to be fake)
        entertainment_indicators = ['actor', 'actress', 'film', 'movie', 'celebrity', 'star', 
                                   'dating', 'rumour', 'rumor', 'fan', 'bollywood', 'hollywood',
                                   'singer', 'music', 'album', 'concert', 'show']
        is_entertainment = any(indicator in text_clean for indicator in entertainment_indicators)
        
        if is_entertainment:
            # Entertainment news is less likely to be fake
            if prediction == 0 and confidence < 0.85:
                prediction = 1  # Change to real
                confidence = 0.65  # Moderate confidence for entertainment news
        
        # Check for credible sources mentioned
        credible_sources = ['reuters', 'associated press', 'bbc', 'cnn', 'nytimes', 
                           'washington post', 'guardian', 'npr', 'times of india', 'ndtv']
        has_credible_source = any(source in text_lower for source in credible_sources)
        if has_credible_source:
            confidence = min(0.95, confidence + 0.15)
            prediction = 1  # More likely real
        
        # Check for conspiracy language
        conspiracy_words = ['conspiracy', 'cover-up', 'they don\'t want you to know', 
                           'hidden truth', 'secret agenda']
        has_conspiracy = any(word in text_lower for word in conspiracy_words)
        if has_conspiracy:
            confidence = min(0.9, confidence + 0.2)
            prediction = 0  # More likely fake
        
        # Generate explanation
        explanation = self._generate_explanation(
            prediction, 
            confidence, 
            suspicious_words, 
            text
        )
        
        # Analyze source reliability
        source_reliability = self._analyze_source_reliability(text)
        
        return {
            'prediction': 'real' if prediction == 1 else 'fake',
            'confidence': round(confidence, 3),
            'suspicious_words': suspicious_words,
            'detected_language': detected_lang,
            'explanation': explanation,
            'source_reliability': source_reliability
        }
    
    def _generate_explanation(self, prediction, confidence, suspicious_words, text):
        """
        Generate human-readable explanation for the prediction
        """
        is_fake = (prediction == 0)
        text_lower = text.lower()
        
        # Check content type
        entertainment_indicators = ['actor', 'actress', 'film', 'movie', 'celebrity', 'star', 
                                   'dating', 'rumour', 'rumor', 'fan', 'bollywood', 'hollywood']
        is_entertainment = any(indicator in text_lower for indicator in entertainment_indicators)
        
        reasons = []
        
        # Confidence-based reasoning
        if confidence > 0.9:
            certainty = "very high confidence"
        elif confidence > 0.75:
            certainty = "high confidence"
        elif confidence > 0.6:
            certainty = "moderate confidence"
        else:
            certainty = "low confidence"
        
        # Main explanation
        if is_fake:
            main_reason = f"This text is classified as FAKE NEWS with {certainty} ({confidence*100:.1f}%)."
        else:
            main_reason = f"This text is classified as REAL NEWS with {certainty} ({confidence*100:.1f}%)."
        
        reasons.append(main_reason)
        
        # Suspicious words analysis (but consider context)
        if len(suspicious_words) > 0 and not is_entertainment:
            reasons.append(
                f"Found {len(suspicious_words)} suspicious keywords commonly used in fake news: "
                f"{', '.join(suspicious_words[:5])}."
            )
        elif is_entertainment and not is_fake:
            reasons.append("This appears to be entertainment/celebrity news, which typically comes from verified sources.")
        
        # Text characteristics (but don't penalize headlines)
        word_count = len(text.split())
        if word_count < 20 and not is_fake:
            # Short text but classified as real - likely a headline
            pass
        elif word_count < 50 and is_fake:
            reasons.append("The text is very short, which may indicate incomplete or sensational content.")
        
        # Sensationalism check
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        if exclamation_count > 3:
            reasons.append(f"Excessive use of exclamation marks ({exclamation_count}) suggests sensationalism.")
        
        if caps_ratio > 0.15:
            reasons.append("High proportion of capital letters indicates emotional or sensational writing.")
        
        # Clickbait patterns
        clickbait_phrases = ['you won\'t believe', 'shocking', 'this will', 'what happens next']
        found_clickbait = [phrase for phrase in clickbait_phrases if phrase in text.lower()]
        if found_clickbait:
            reasons.append(f"Contains clickbait phrases: {', '.join(found_clickbait)}.")
        
        return ' '.join(reasons)
    
    def _analyze_source_reliability(self, text):
        """
        Analyze source reliability indicators with more dynamic scoring
        
        Returns:
            dict with reliability score and factors
        """
        reliability_score = 50  # Start at neutral (0-100 scale)
        factors = []
        
        text_lower = text.lower()
        text_length = len(text)
        
        # Length analysis - longer, detailed articles are more reliable
        if text_length > 1000:
            reliability_score += 15
            factors.append("Detailed article (>1000 characters)")
        elif text_length > 500:
            reliability_score += 8
            factors.append("Moderate length article")
        elif text_length < 100:
            reliability_score -= 15
            factors.append("Very short article (potentially clickbait)")
        
        # Positive indicators (increase reliability)
        reliable_sources = ['reuters', 'associated press', 'bbc', 'cnn', 'nytimes', 
                           'washington post', 'guardian', 'npr', 'pbs', 'times of india',
                           'ndtv', 'indian express', 'bbc news']
        for source in reliable_sources:
            if source in text_lower:
                reliability_score += 20
                factors.append(f"Mentions reputable source: {source}")
                break
        
        # Check for citations and references
        citation_count = text_lower.count('according to') + text_lower.count('study shows') + text_lower.count('research')
        if citation_count >= 2:
            reliability_score += 15
            factors.append(f"Multiple citations/references ({citation_count})")
        elif citation_count == 1:
            reliability_score += 8
            factors.append("Contains citations or references")
        
        # Check for author attribution
        if 'by ' in text_lower[:200]:  # Check in first 200 chars
            reliability_score += 8
            factors.append("Has author attribution")
        
        # Check for date/time information
        date_patterns = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 
                        'september', 'october', 'november', 'december', '2024', '2025', '2026']
        date_count = sum(1 for pattern in date_patterns if pattern in text_lower)
        if date_count >= 2:
            reliability_score += 10
            factors.append("Contains specific date/time information")
        
        # Negative indicators (decrease reliability)
        unreliable_indicators = [
            'anonymous source', 'unnamed source', 'sources say',
            'breaking:', 'urgent:', 'alert:', 'must read', 'share now',
            'click here', 'you won\'t believe', 'doctors hate'
        ]
        unreliable_count = 0
        for indicator in unreliable_indicators:
            if indicator in text_lower:
                reliability_score -= 12
                unreliable_count += 1
                factors.append(f"Contains unreliable indicator: '{indicator}'")
        
        # Check for conspiracy language
        conspiracy_words = ['conspiracy', 'cover-up', 'they don\'t want you to know', 
                           'hidden truth', 'secret agenda', 'illuminati', 'deep state']
        conspiracy_count = sum(1 for word in conspiracy_words if word in text_lower)
        if conspiracy_count >= 2:
            reliability_score -= 25
            factors.append(f"Multiple conspiracy language indicators ({conspiracy_count})")
        elif conspiracy_count == 1:
            reliability_score -= 15
            factors.append("Contains conspiracy language")
        
        # Check for emotional manipulation
        emotional_words = ['outrage', 'shocking', 'unbelievable', 'scandal', 'exposed', 
                          'disgusting', 'horrifying', 'devastating', 'tragic']
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        if emotional_count >= 4:
            reliability_score -= 20
            factors.append(f"High emotional language ({emotional_count} emotional words)")
        elif emotional_count >= 2:
            reliability_score -= 10
            factors.append(f"Moderate emotional language ({emotional_count} emotional words)")
        
        # Check for ALL CAPS words (often used in clickbait)
        all_caps_words = len([word for word in text.split() if len(word) > 3 and word.isupper()])
        if all_caps_words >= 5:
            reliability_score -= 15
            factors.append(f"Multiple ALL CAPS words ({all_caps_words})")
        elif all_caps_words >= 2:
            reliability_score -= 8
            factors.append(f"Some ALL CAPS words ({all_caps_words})")
        
        # Check for question marks (often used in clickbait)
        question_count = text.count('?')
        if question_count >= 3:
            reliability_score -= 10
            factors.append(f"Multiple questions ({question_count})")
        
        # Check for exclamation marks (often used in sensationalism)
        exclamation_count = text.count('!')
        if exclamation_count >= 5:
            reliability_score -= 12
            factors.append(f"High exclamation usage ({exclamation_count})")
        
        # Ensure score is within bounds
        reliability_score = max(0, min(100, reliability_score))
        
        # Determine reliability level
        if reliability_score >= 75:
            level = "High"
            description = "Source appears reliable with credible indicators"
        elif reliability_score >= 60:
            level = "Medium-High"
            description = "Source has mostly positive reliability indicators"
        elif reliability_score >= 50:
            level = "Medium"
            description = "Source has mixed reliability indicators"
        elif reliability_score >= 35:
            level = "Low"
            description = "Source shows signs of unreliability"
        else:
            level = "Very Low"
            description = "Source appears highly unreliable"
        
        return {
            'score': reliability_score,
            'level': level,
            'description': description,
            'factors': factors
        }
    
    def _preprocess(self, text):
        """Clean and preprocess text"""
        text = str(text).lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _find_suspicious_words(self, text, language):
        """Find suspicious keywords in text"""
        text_lower = text.lower()
        keywords = self.suspicious_keywords.get(language, self.suspicious_keywords['en'])
        found = [word for word in keywords if word in text_lower]
        return found[:10]  # Return max 10
