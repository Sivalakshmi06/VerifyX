import re
from textblob import TextBlob
import nltk
from collections import Counter
from models.scam_detector import ScamDetector

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class EmotionAnalyzer:
    """
    Enhanced Emotional Manipulation Analyzer with Scam Detection
    Detects: Fear, Anger, Political Bias, Religious Triggers, and Scams
    Provides: Manipulation Type, Triggering Words, Explanation, Confidence
    """
    
    def __init__(self):
        self.scam_detector = ScamDetector()
        # Enhanced emotion keyword dictionaries with weights
        self.emotion_keywords = {
            'fear': {
                'high': ['terror', 'panic', 'deadly', 'fatal', 'disaster', 'catastrophe', 'apocalypse', 'doom', 'death', 'kill'],
                'medium': ['danger', 'threat', 'scary', 'afraid', 'warning', 'risk', 'unsafe', 'crisis', 'emergency'],
                'low': ['concern', 'worry', 'caution', 'alert', 'beware', 'careful']
            },
            'anger': {
                'high': ['hate', 'furious', 'outrage', 'rage', 'disgusting', 'horrible', 'worst', 'evil'],
                'medium': ['angry', 'mad', 'terrible', 'awful', 'bad', 'wrong', 'unfair', 'injustice'],
                'low': ['annoyed', 'upset', 'disappointed', 'frustrated', 'bothered']
            },
            'political_bias': {
                'high': ['regime', 'dictator', 'tyranny', 'oppression', 'propaganda', 'corrupt'],
                'medium': ['liberal', 'conservative', 'left', 'right', 'democrat', 'republican', 'socialist', 'communist'],
                'low': ['government', 'politics', 'policy', 'election', 'vote', 'party']
            },
            'religious_trigger': {
                'high': ['blasphemy', 'heresy', 'infidel', 'sin', 'devil', 'satan', 'hell', 'damnation', 'curse', 'unholy'],
                'medium': ['god', 'religion', 'faith', 'sacred', 'holy', 'prayer', 'worship', 'divine', 'spiritual'],
                'low': ['belief', 'church', 'temple', 'mosque', 'religious', 'scripture', 'bible', 'quran']
            }
        }
        
        # Manipulation technique patterns
        self.manipulation_patterns = {
            'urgency': ['urgent', 'immediately', 'now', 'hurry', 'quick', 'fast', 'asap', 'right now', 'today', 'don\'t delay'],
            'authority': ['experts say', 'scientists confirm', 'studies show', 'research proves', 'doctors warn', 'police', 'court', 'legal', 'law', 'official'],
            'social_proof': ['everyone', 'nobody', 'all', 'none', 'everybody knows', 'people are saying', 'most people'],
            'scarcity': ['limited', 'rare', 'exclusive', 'only', 'last chance', 'running out', 'few left', 'limited time'],
            'emotional_appeal': ['shocking', 'unbelievable', 'amazing', 'incredible', 'you won\'t believe', 'devastating', 'tragic'],
            'call_to_action': ['share', 'spread', 'tell', 'forward', 'repost', 'act now', 'must read', 'click', 'pay', 'send', 'register', 'join'],
            'absolutes': ['always', 'never', 'all', 'none', 'every', 'no one', 'everyone', 'nobody'],
            'threat': ['arrest', 'jail', 'prison', 'fine', 'penalty', 'blocked', 'suspended', 'freeze', 'cancel', 'close', 'case filed'],
            'money_promise': ['earn', 'make money', 'income', 'profit', 'guaranteed', 'easy money', 'passive income', 'get rich', 'per day', 'per week', 'per month', 'investment'],
            'work_from_home': ['work from home', 'wfh', 'remote work', 'no experience', 'easy job', 'simple task', 'quick cash', 'side hustle']
        }
    
    def analyze(self, text):
        """
        Enhanced analysis of text for emotional manipulation and scams
        
        Args:
            text: Input text to analyze
        
        Returns:
            dict with detailed emotion analysis, manipulation types, triggering words, explanation, confidence, and scam detection
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        # Detect scams first
        scam_result = self.scam_detector.detect(text)
        
        # Calculate emotion scores with weighted keywords
        emotions = {}
        emotion_triggers = {}
        
        for emotion, levels in self.emotion_keywords.items():
            score = 0
            triggers = []
            
            # High weight keywords (3 points)
            for word in levels['high']:
                if word in text_lower:
                    score += 3
                    triggers.append(word)
            
            # Medium weight keywords (2 points)
            for word in levels['medium']:
                if word in text_lower:
                    score += 2
                    triggers.append(word)
            
            # Low weight keywords (1 point)
            for word in levels['low']:
                if word in text_lower:
                    score += 1
                    triggers.append(word)
            
            # Normalize score (0-1 scale)
            max_possible = len(words) * 0.3  # Assume max 30% emotional words
            emotions[emotion] = min(score / max(max_possible, 1), 1.0)
            emotion_triggers[emotion] = triggers[:5]  # Top 5 triggers
        
        # Detect manipulation techniques
        manipulation_types = []
        manipulation_triggers = {}
        manipulation_strength = 0  # Track strength of manipulation
        
        for technique, keywords in self.manipulation_patterns.items():
            found = [word for word in keywords if word in text_lower]
            if found:
                manipulation_types.append(technique)
                manipulation_triggers[technique] = found[:3]  # Top 3 per technique
                # Add strength based on number of keywords found
                manipulation_strength += len(found)
        
        # Calculate overall manipulation score (0-1)
        # Base score on number of techniques detected
        base_manipulation = len(manipulation_types) / len(self.manipulation_patterns)
        
        # Boost score based on keyword strength (more keywords = stronger manipulation)
        keyword_boost = min(manipulation_strength / 10, 0.3)  # Max 30% boost
        
        manipulation_score = min(base_manipulation + keyword_boost, 1.0)
        
        # Sentiment analysis
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity
        sentiment_subjectivity = blob.sentiment.subjectivity
        
        # Adjust manipulation score based on extreme sentiment and subjectivity
        if abs(sentiment_polarity) > 0.7:
            manipulation_score = min(manipulation_score + 0.15, 1.0)
        if sentiment_subjectivity > 0.7:
            manipulation_score = min(manipulation_score + 0.1, 1.0)
        
        # Find dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        dominant_emotion_name = dominant_emotion[0].replace('_', ' ').title()
        dominant_emotion_score = dominant_emotion[1]
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(
            emotions, 
            manipulation_score, 
            len(words),
            sentiment_subjectivity
        )
        
        # Determine primary manipulation type
        primary_manipulation = self._determine_manipulation_type(
            emotions,
            manipulation_types,
            sentiment_polarity
        )
        
        # Generate detailed explanation
        explanation = self._generate_explanation(
            emotions,
            manipulation_types,
            dominant_emotion_name,
            sentiment_polarity,
            manipulation_score
        )
        
        # Collect all triggering words
        all_triggers = []
        for triggers in emotion_triggers.values():
            all_triggers.extend(triggers)
        for triggers in manipulation_triggers.values():
            all_triggers.extend(triggers)
        
        # Remove duplicates and limit to top 10
        unique_triggers = list(dict.fromkeys(all_triggers))[:10]
        
        result = {
            'manipulation_type': primary_manipulation,
            'confidence': round(confidence * 100, 2),
            'manipulation_score': round(manipulation_score * 100, 2),
            'emotions': {
                'fear': round(emotions.get('fear', 0) * 100, 2),
                'anger': round(emotions.get('anger', 0) * 100, 2),
                'political_bias': round(emotions.get('political_bias', 0) * 100, 2),
                'religious_trigger': round(emotions.get('religious_trigger', 0) * 100, 2)
            },
            'dominant_emotion': dominant_emotion_name,
            'dominant_emotion_score': round(dominant_emotion_score * 100, 2),
            'triggering_words': unique_triggers,
            'manipulation_techniques': manipulation_types,
            'explanation': explanation,
            'sentiment': {
                'polarity': round(sentiment_polarity, 3),
                'subjectivity': round(sentiment_subjectivity, 3),
                'label': 'Positive' if sentiment_polarity > 0.1 else 'Negative' if sentiment_polarity < -0.1 else 'Neutral'
            },
            # Add scam detection results
            'is_scam': scam_result['is_scam'],
            'scam_confidence': scam_result['scam_confidence'],
            'scam_type': scam_result['scam_type'],
            'scam_explanation': scam_result['scam_explanation'],
            'scam_indicators': scam_result['scam_indicators']
        }
        
        return result
    
    def _calculate_confidence(self, emotions, manipulation_score, word_count, subjectivity, is_scam=False):
        """Calculate confidence score based on multiple factors"""
        # Base confidence on text length
        if word_count < 20:
            base_confidence = 0.6
        elif word_count < 50:
            base_confidence = 0.75
        else:
            base_confidence = 0.85
        
        # Adjust based on emotion clarity
        max_emotion = max(emotions.values())
        if max_emotion > 0.6:
            base_confidence += 0.1
        elif max_emotion > 0.4:
            base_confidence += 0.05
        
        # Adjust based on manipulation indicators (strong indicator of scam/phishing)
        if manipulation_score > 0.7:
            base_confidence += 0.15  # High confidence for strong manipulation
        elif manipulation_score > 0.5:
            base_confidence += 0.1
        elif manipulation_score > 0.3:
            base_confidence += 0.05
        
        # CRITICAL: If scam detected, boost confidence significantly
        if is_scam:
            base_confidence += 0.2  # Extra 20% for confirmed scam
        
        # Adjust based on subjectivity (more subjective = more confident in manipulation)
        if subjectivity > 0.7:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _determine_manipulation_type(self, emotions, manipulation_techniques, sentiment):
        """Determine the primary type of manipulation"""
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = max_emotion[0]
        emotion_score = max_emotion[1]
        
        # Check for banking/phishing scam keywords first
        banking_keywords = ['bank', 'account', 'kyc', 'update', 'verify', 'confirm', 'password', 'login', 'suspended', 'blocked', 'freeze', 'transaction', 'payment', 'card', 'atm']
        phishing_keywords = ['click', 'link', 'verify', 'confirm', 'update', 'urgent', 'immediately', 'action required']
        
        # If strong emotion detected but it's a banking scam, classify as scam instead
        if emotion_score > 0.4:
            if emotion_name == 'fear':
                return 'Fear-Based Manipulation (Phishing/Scam)'
            elif emotion_name == 'anger':
                return 'Anger-Based Manipulation'
            elif emotion_name == 'political_bias':
                return 'Political Manipulation'
            elif emotion_name == 'religious_trigger':
                # Only return religious if it's actually religious content
                # Check if banking/phishing keywords are present
                return 'Religious Manipulation'
        
        # If manipulation techniques detected
        if manipulation_techniques:
            if 'urgency' in manipulation_techniques:
                return 'Urgency Manipulation (Phishing/Scam)'
            elif 'emotional_appeal' in manipulation_techniques:
                return 'Emotional Appeal'
            elif 'social_proof' in manipulation_techniques:
                return 'Social Proof Manipulation'
            elif 'authority' in manipulation_techniques:
                return 'Authority Manipulation'
        
        # Based on sentiment
        if abs(sentiment) > 0.7:
            return 'Extreme Sentiment Manipulation'
        
        return 'Low/No Manipulation Detected'
    
    def _generate_explanation(self, emotions, manipulation_techniques, dominant_emotion, sentiment, manipulation_score):
        """Generate detailed explanation of the analysis"""
        explanation_parts = []
        
        # Overall assessment
        if manipulation_score > 0.7:
            explanation_parts.append("This text shows STRONG signs of emotional manipulation.")
        elif manipulation_score > 0.4:
            explanation_parts.append("This text shows MODERATE signs of emotional manipulation.")
        elif manipulation_score > 0.2:
            explanation_parts.append("This text shows MILD signs of emotional manipulation.")
        else:
            explanation_parts.append("This text shows minimal signs of emotional manipulation.")
        
        # Dominant emotion
        max_emotion_score = max(emotions.values())
        if max_emotion_score > 0.5:
            explanation_parts.append(f"The dominant emotional trigger is {dominant_emotion} ({round(max_emotion_score * 100, 1)}%).")
        
        # Manipulation techniques
        if manipulation_techniques:
            techniques_str = ', '.join([t.replace('_', ' ').title() for t in manipulation_techniques[:3]])
            explanation_parts.append(f"Detected manipulation techniques: {techniques_str}.")
        
        # Sentiment analysis
        if sentiment > 0.5:
            explanation_parts.append("The text uses highly positive language to influence opinion.")
        elif sentiment < -0.5:
            explanation_parts.append("The text uses highly negative language to provoke emotional response.")
        
        # Specific emotion warnings
        if emotions.get('fear', 0) > 0.5:
            explanation_parts.append("High fear-inducing content detected - often used to manipulate through anxiety.")
        if emotions.get('anger', 0) > 0.5:
            explanation_parts.append("High anger-inducing content detected - designed to provoke outrage.")
        if emotions.get('political_bias', 0) > 0.5:
            explanation_parts.append("Strong political bias detected - may be pushing a specific agenda.")
        if emotions.get('religious_trigger', 0) > 0.5:
            explanation_parts.append("Religious triggers detected - may be exploiting faith-based emotions.")
        
        return ' '.join(explanation_parts)
