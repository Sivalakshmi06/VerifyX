import re

class ScamDetector:
    """
    Detect common scam patterns in messages
    Identifies phishing, financial scams, lottery scams, etc.
    """
    
    def __init__(self):
        # Common scam patterns
        self.scam_patterns = {
            'phishing': {
                'keywords': [
                    'verify your account', 'suspended account', 'unusual activity',
                    'confirm your identity', 'update payment', 'click here immediately',
                    'account will be closed', 'verify within 24 hours', 'security alert'
                ],
                'type': 'Phishing Attempt',
                'description': 'This appears to be a phishing scam trying to steal your personal information or login credentials.'
            },
            'financial_scam': {
                'keywords': [
                    'you have won', 'claim your prize', 'lottery winner', 'inheritance',
                    'transfer money', 'wire transfer', 'bank details', 'account number',
                    'send money', 'processing fee', 'tax payment', 'release funds'
                ],
                'type': 'Financial Scam',
                'description': 'This appears to be a financial scam attempting to trick you into sending money or sharing banking details.'
            },
            'urgency_scam': {
                'keywords': [
                    'act now', 'limited time', 'expires today', 'urgent action required',
                    'immediate response', 'last chance', 'offer ends', 'hurry',
                    'don\'t miss out', 'time sensitive'
                ],
                'type': 'Urgency-Based Scam',
                'description': 'This message uses urgency tactics to pressure you into making quick decisions without thinking.'
            },
            'impersonation': {
                'keywords': [
                    'from: bank', 'from: paypal', 'from: amazon', 'from: irs',
                    'from: government', 'official notice', 'tax department',
                    'customer service', 'support team', 'security team'
                ],
                'type': 'Impersonation Scam',
                'description': 'This message may be impersonating a legitimate organization to gain your trust.'
            },
            'romance_scam': {
                'keywords': [
                    'love you', 'soulmate', 'destiny', 'need money', 'emergency',
                    'hospital', 'stranded', 'help me', 'send funds', 'western union'
                ],
                'type': 'Romance/Relationship Scam',
                'description': 'This appears to be a romance scam using emotional manipulation to request money.'
            },
            'job_scam': {
                'keywords': [
                    'work from home', 'easy money', 'no experience needed',
                    'earn $$$', 'guaranteed income', 'investment opportunity',
                    'make money fast', 'passive income', 'get rich'
                ],
                'type': 'Job/Investment Scam',
                'description': 'This appears to be a fraudulent job offer or investment scheme.'
            },
            'tech_support_scam': {
                'keywords': [
                    'virus detected', 'computer infected', 'call this number',
                    'tech support', 'microsoft support', 'apple support',
                    'system error', 'security breach', 'malware found'
                ],
                'type': 'Tech Support Scam',
                'description': 'This appears to be a fake tech support scam trying to gain access to your computer.'
            }
        }
        
        # Red flag indicators
        self.red_flags = [
            ('requests personal information', r'(social security|ssn|password|pin|credit card|bank account)'),
            ('suspicious links', r'(bit\.ly|tinyurl|goo\.gl|shortened url|click here)'),
            ('poor grammar/spelling', r'([A-Z]{5,}|!!!+|\?\?\?+)'),
            ('requests immediate action', r'(now|immediately|urgent|asap|today|within \d+ hours)'),
            ('promises unrealistic rewards', r'(\$\d{3,}|won|prize|lottery|inheritance)'),
            ('threatens negative consequences', r'(suspend|close|terminate|legal action|arrest)'),
            ('requests payment via unusual methods', r'(gift card|bitcoin|cryptocurrency|wire transfer|western union)'),
            ('sender email mismatch', r'(@[a-z0-9-]+\.(tk|ml|ga|cf|gq))'),  # Suspicious TLDs
        ]
    
    def detect(self, text):
        """
        Analyze text for scam indicators
        
        Args:
            text: Input text to analyze
        
        Returns:
            dict with scam detection results
        """
        text_lower = text.lower()
        
        # Check for scam patterns
        detected_scams = []
        scam_scores = {}
        
        for scam_type, pattern_data in self.scam_patterns.items():
            matches = sum(1 for keyword in pattern_data['keywords'] if keyword in text_lower)
            if matches > 0:
                score = min(matches * 20, 100)  # Each match adds 20%, max 100%
                scam_scores[scam_type] = {
                    'score': score,
                    'matches': matches,
                    'type': pattern_data['type'],
                    'description': pattern_data['description']
                }
                detected_scams.append(scam_type)
        
        # Check for red flags
        red_flags_found = []
        for flag_name, pattern in self.red_flags:
            if re.search(pattern, text_lower, re.IGNORECASE):
                red_flags_found.append(flag_name)
        
        # Determine if it's a scam
        is_scam = len(detected_scams) > 0 or len(red_flags_found) >= 3
        
        # Calculate overall scam confidence
        if scam_scores:
            max_score = max(data['score'] for data in scam_scores.values())
            scam_confidence = min(max_score + (len(red_flags_found) * 10), 100)
        else:
            scam_confidence = len(red_flags_found) * 15
        
        # Get primary scam type
        if scam_scores:
            primary_scam = max(scam_scores.items(), key=lambda x: x[1]['score'])
            scam_type = primary_scam[1]['type']
            scam_explanation = primary_scam[1]['description']
        else:
            scam_type = "Suspicious Message"
            scam_explanation = "This message contains multiple warning signs commonly found in scams."
        
        # Generate detailed indicators
        scam_indicators = []
        if detected_scams:
            scam_indicators.append(f"Matches {len(detected_scams)} known scam pattern(s)")
        scam_indicators.extend(red_flags_found)
        
        return {
            'is_scam': is_scam,
            'scam_confidence': scam_confidence,
            'scam_type': scam_type if is_scam else None,
            'scam_explanation': scam_explanation if is_scam else None,
            'scam_indicators': scam_indicators if is_scam else [],
            'detected_patterns': detected_scams,
            'red_flags_count': len(red_flags_found)
        }
    
    def get_safety_tips(self, scam_type):
        """
        Get safety tips based on detected scam type
        """
        tips = {
            'phishing': [
                "Never click on suspicious links in emails or messages",
                "Verify sender's email address carefully",
                "Contact the organization directly using official channels",
                "Don't provide personal information via email"
            ],
            'financial_scam': [
                "Never send money to unknown people",
                "Be skeptical of 'too good to be true' offers",
                "Verify lottery/prize claims with official sources",
                "Don't share banking details via email or text"
            ],
            'urgency_scam': [
                "Take time to think before acting",
                "Legitimate organizations don't pressure immediate action",
                "Verify claims independently",
                "Consult with trusted friends or family"
            ],
            'impersonation': [
                "Verify the sender through official channels",
                "Check for official email domains",
                "Call the organization using publicly listed numbers",
                "Don't trust caller ID alone"
            ],
            'romance_scam': [
                "Never send money to someone you haven't met",
                "Be cautious of online relationships that move quickly",
                "Verify identity through video calls",
                "Research the person's background"
            ],
            'job_scam': [
                "Research the company thoroughly",
                "Never pay upfront fees for jobs",
                "Be skeptical of unrealistic income promises",
                "Verify job offers through official company websites"
            ],
            'tech_support_scam': [
                "Never call numbers from pop-up warnings",
                "Legitimate companies don't cold-call about viruses",
                "Don't give remote access to your computer",
                "Use official support channels only"
            ]
        }
        
        return tips.get(scam_type, [
            "Be cautious and verify information",
            "Don't share personal information",
            "Report suspicious messages",
            "Trust your instincts"
        ])
