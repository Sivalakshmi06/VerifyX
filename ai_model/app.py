from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import model handlers
from models.text_classifier import TextClassifier
from models.image_detector import ImageDetector
from models.emotion_analyzer import EmotionAnalyzer
from models.ocr_extractor import OCRExtractor
from models.news_verifier import NewsVerifier
from models.url_verifier import URLVerifier
from models.news_aggregator import NewsAggregator
from models.news_matcher import NewsMatcher
from models.tamil_news_matcher import TamilNewsMatcher
from models.tamil_classifier import TamilClassifier

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize models
text_classifier = TextClassifier()
image_detector = ImageDetector()
emotion_analyzer = EmotionAnalyzer()
ocr_extractor = OCRExtractor()
news_verifier = NewsVerifier()
url_verifier = URLVerifier()
news_aggregator = NewsAggregator()
news_matcher = NewsMatcher()
tamil_news_matcher = TamilNewsMatcher()
tamil_classifier = TamilClassifier()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'AI API is running'
    })

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """
    Analyze text for fake news detection.
    Tamil path  → tamil_classifier.py (9 Tamil newspapers + fake signal detection)
    English path → news_aggregator RSS + TF-IDF similarity + ML fallback
    Rule: if not found in trusted sources with strong match → FAKE
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        url  = data.get('url', '')
        language = data.get('language', 'en')

        url_info = None

        # ── Fetch URL content if provided ──
        if url:
            url_result = url_verifier.fetch_url_content(url)
            if url_result['success']:
                url_text = url_result['text']
                text = f"{text}\n{url_text}" if text else url_text
                url_info = {
                    'title':      url_result['title'],
                    'domain':     url_result['domain'],
                    'is_trusted': url_verifier.is_trusted_source(url_result['domain'])
                }
                # Auto-detect Tamil from domain
                tamil_domains = ['dinathanthi.com', 'dinamalar.com', 'dinakaran.com',
                                 'dailythanthi.com', 'vikatan.com', 'puthiyathalaimurai.com',
                                 'polimernews.com', 'maalaimalar.com']
                if any(d in url.lower() for d in tamil_domains):
                    language = 'ta'
                tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
                if tamil_chars > 10:
                    language = 'ta'
            else:
                return jsonify({'success': False, 'message': url_result['error']}), 400

        if not text:
            return jsonify({'success': False, 'message': 'Text or URL is required'}), 400

        # Auto-detect Tamil from plain text
        if language == 'en':
            tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
            if tamil_chars > 5:
                language = 'ta'
                print(f"[AUTO-DETECT] Tamil detected ({tamil_chars} chars)")

        print(f"[DETECT] lang={language}, text_len={len(text)}")

        # ════════════════════════════════════════
        # TAMIL PATH
        # ════════════════════════════════════════
        if language == 'ta':
            # Trusted URL override
            if url_info and url_info['is_trusted']:
                final_prediction = 'real'
                final_confidence = 0.91
                source_verdict   = f"நம்பகமான ஆதாரம்: {url_info['domain']}"
                explanation      = f"✅ இந்த செய்தி உண்மையானது. {source_verdict} Confidence: {final_confidence*100:.1f}%."
                matched_articles = []
                matched_sources  = [url_info['domain']]
                source_match_count = 1
                top_match_score    = 90
            else:
                tamil_result = tamil_classifier.classify(text)
                final_prediction   = tamil_result['prediction']
                final_confidence   = tamil_result['confidence']
                source_verdict     = tamil_result['verdict_english']
                matched_articles   = tamil_result['source_matches']
                matched_sources    = tamil_result['matched_sources']
                source_match_count = tamil_result['strong_match_count']
                top_match_score    = tamil_result['top_score']

                if final_prediction == 'real':
                    explanation = f"✅ இந்த செய்தி உண்மையானது. {tamil_result['verdict_tamil']} Confidence: {final_confidence*100:.1f}%."
                else:
                    explanation = f"❌ இந்த செய்தி போலியானது அல்லது சரிபார்க்கப்படவில்லை. {tamil_result['verdict_tamil']} Confidence: {final_confidence*100:.1f}%."

            reliability_score = min(95, 35 + source_match_count * 12 + int(top_match_score * 0.3))
            source_articles_count = len(matched_articles)

        # ════════════════════════════════════════
        # ENGLISH PATH
        # ════════════════════════════════════════
        else:
            source_articles = news_aggregator.get_all_articles_flat(
                max_articles_per_source=20, language='en'
            )
            matched_articles = news_matcher.find_similar_articles(
                text, source_articles, max_results=8, min_similarity=0.05
            )

            source_match_count = len(matched_articles)
            top_match_score    = matched_articles[0]['similarity_score'] if matched_articles else 0
            matched_sources    = list({a['source'] for a in matched_articles})
            source_articles_count = len(source_articles)

            print(f"[EN] matches={source_match_count}, top_score={top_match_score:.1f}")

            # Trusted URL → always real
            if url_info and url_info['is_trusted']:
                final_prediction = 'real'
                final_confidence = 0.91
                source_verdict   = f"Content from verified trusted source: {url_info['domain']}."

            # Strong match (2+ sources OR top score ≥ 35) → REAL
            elif source_match_count >= 2 or top_match_score >= 35:
                final_prediction = 'real'
                final_confidence = min(0.92, 0.65 + source_match_count * 0.05 + top_match_score * 0.001)
                source_verdict   = f"Verified in {source_match_count} trusted source(s): {', '.join(matched_sources[:3])}."

            # Single match OR top score ≥ 15 → run ML to confirm
            elif source_match_count >= 1 or top_match_score >= 15:
                ml_result = text_classifier.predict(text, language)
                if ml_result['prediction'] == 'real' and ml_result['confidence'] >= 0.60:
                    final_prediction = 'real'
                    final_confidence = min(0.80, 0.52 + top_match_score * 0.004)
                    source_verdict   = f"Matched {source_match_count} source(s) and ML confirms real. Sources: {', '.join(matched_sources[:2])}."
                else:
                    final_prediction = 'fake'
                    final_confidence = 0.65
                    source_verdict   = f"Weak source match. ML model classifies as unverified."

            # No match at all → FAKE
            else:
                ml_result = text_classifier.predict(text, language)
                if ml_result['prediction'] == 'fake':
                    final_confidence = min(0.87, 0.68 + ml_result['confidence'] * 0.15)
                    source_verdict   = f"Not found in trusted sources. ML also classifies as fake."
                else:
                    final_confidence = 0.72
                    source_verdict   = f"Not found in any of the {len(source_articles)} trusted news articles checked."
                final_prediction = 'fake'

            if final_prediction == 'real':
                explanation = f"✅ This news is classified as REAL. {source_verdict} Confidence: {final_confidence*100:.1f}%."
            else:
                explanation = f"❌ This news is classified as FAKE/UNVERIFIED. {source_verdict} Confidence: {final_confidence*100:.1f}%."

            reliability_score = min(95, 30 + source_match_count * 12 + int(top_match_score * 0.4))
            if url_info and url_info['is_trusted']:
                reliability_score = 92

        # ── Source reliability block ──
        source_reliability = {
            'score': reliability_score,
            'level': 'High' if reliability_score >= 70 else ('Medium' if reliability_score >= 45 else 'Low'),
            'description': source_verdict,
            'factors': [
                f"Matched {source_match_count} trusted source(s)",
                f"Top match score: {top_match_score:.1f}%",
                f"Sources checked: {source_articles_count} articles from trusted outlets"
            ] + ([f"Matched: {', '.join(matched_sources[:3])}"] if matched_sources else ["No matching articles found"])
        }

        # Wikipedia verification
        try:
            wikipedia_verification = url_verifier.verify_with_wikipedia(text[:500])
        except Exception:
            wikipedia_verification = {'found': False, 'message': 'Wikipedia verification unavailable', 'articles': []}

        response_data = {
            'success':           True,
            'prediction':        final_prediction,
            'confidence':        round(final_confidence, 3),
            'suspicious_words':  [],
            'detected_language': language,
            'explanation':       explanation,
            'source_reliability': source_reliability,
            'verification': {
                'status':          'Verified' if final_prediction == 'real' else 'Not Verified',
                'score':           reliability_score,
                'message':         source_verdict,
                'matches':         matched_articles[:3],
                'sources_checked': matched_sources
            },
            'wikipedia_verification': wikipedia_verification,
            'source_matches':    matched_articles
        }

        if url_info:
            response_data['url_info'] = url_info

        return jsonify(response_data)

    except Exception as e:
        print(f"Text analysis error: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error analyzing text', 'error': str(e)}), 500

@app.route('/api/analyze/image', methods=['POST'])
def analyze_image():
    """
    Detect deepfake in uploaded image or video
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Image or video file is required'
            }), 400
        
        image_file = request.files['image']
        file_type = request.form.get('fileType', 'image')
        
        # Perform deepfake detection
        result = image_detector.predict(image_file, file_type)
        
        response = {
            'success': True,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'is_deepfake': result['is_deepfake'],
            'heatmap_url': result.get('heatmap_url', ''),
            'method': result.get('method', 'heuristic')
        }
        if 'analysis_details' in result:
            response['analysis_details'] = result['analysis_details']
        return jsonify(response)
    
    except Exception as e:
        print(f"Image/Video analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error analyzing media',
            'error': str(e)
        }), 500

@app.route('/api/analyze/emotion', methods=['POST'])
def analyze_emotion():
    """
    Analyze emotional manipulation in text
    Detects: Fear, Anger, Political Bias, Religious Triggers, and Scams
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'success': False,
                'message': 'Text is required'
            }), 400
        
        # Perform emotion analysis with scam detection
        result = emotion_analyzer.analyze(text)
        
        return jsonify({
            'success': True,
            **result
        })
    
    except Exception as e:
        print(f"Emotion analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error analyzing emotions',
            'error': str(e)
        }), 500

@app.route('/api/analyze/emotion-image', methods=['POST'])
def analyze_emotion_image():
    """
    Analyze emotional manipulation from screenshot/image
    Extracts text using OCR then performs emotion and scam analysis
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Image file is required'
            }), 400
        
        image_file = request.files['image']
        additional_text = request.form.get('additionalText', '')
        
        print(f"[DEBUG] Processing image: {image_file.filename}")
        
        # Extract text from image using OCR
        ocr_result = ocr_extractor.extract_text(image_file)
        
        print(f"[DEBUG] OCR result: {ocr_result}")
        
        # Check if OCR failed
        if 'error' in ocr_result and not ocr_result.get('text'):
            return jsonify({
                'success': False,
                'message': 'Failed to extract text from image',
                'error': ocr_result.get('error', 'OCR failed')
            }), 400
        
        extracted_text = ocr_result.get('text', '')
        
        # Combine extracted text with additional text if provided
        full_text = f"{extracted_text}\n{additional_text}".strip()
        
        if not full_text:
            return jsonify({
                'success': False,
                'message': 'No text found in image. Please ensure the image contains readable text.'
            }), 400
        
        print(f"[DEBUG] Analyzing text: {full_text[:100]}...")
        
        # Perform emotion analysis with scam detection
        result = emotion_analyzer.analyze(full_text)
        
        # Add OCR information to result
        result['extracted_text'] = extracted_text
        result['ocr_confidence'] = ocr_result.get('confidence', 0)
        
        return jsonify({
            'success': True,
            **result
        })
    
    except Exception as e:
        print(f"Emotion image analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error analyzing image',
            'error': str(e)
        }), 500

@app.route('/api/analyze/image-text', methods=['POST'])
def analyze_image_text():
    """
    Extract text from image using OCR and classify as fake/real
    Supports English and Tamil
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Image file is required'
            }), 400
        
        image_file = request.files['image']
        
        # Extract text and classify
        result = ocr_extractor.extract_and_classify(image_file, text_classifier)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'extracted_text': result['extracted_text'],
            'ocr_confidence': result['ocr_result']['confidence'],
            'detected_language': result['ocr_result']['detected_language'],
            'word_count': result['ocr_result']['word_count'],
            'classification': result['classification']
        })
    
    except Exception as e:
        print(f"Image text analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error analyzing image text',
            'error': str(e)
        }), 500

@app.route('/api/news/search-related', methods=['POST'])
def search_related_news():
    """
    Search for related news articles from language-specific sources
    Input: text or URL, language
    Output: List of related articles with similarity scores
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        url = data.get('url', '')
        max_results = data.get('max_results', 10)
        language = data.get('language', 'en')
        
        # Get content to search
        search_text = text
        
        if url and not text:
            # Fetch content from URL
            url_result = url_verifier.fetch_url_content(url)
            if url_result['success']:
                # Auto-detect language from URL domain first
                tamil_domains = ['dinathanthi.com', 'dailythanthi.com', 'dinamalar.com', 'dinakaran.com', 'vikatan.com', 'puthiyathalaimurai.tv']
                if any(domain in url.lower() for domain in tamil_domains):
                    language = 'ta'
                    print(f"[AUTO-DETECT] Tamil source detected from URL domain")

                # For Tamil: use only title + first 300 chars (avoid nav menu noise)
                if language == 'ta':
                    search_text = f"{url_result['title']} {url_result['text'][:300]}"
                else:
                    search_text = f"{url_result['title']} {url_result['text']}"

                # Also check content for Tamil characters
                tamil_char_count = len([c for c in search_text if '\u0B80' <= c <= '\u0BFF'])
                if tamil_char_count > 10:
                    language = 'ta'
                    print(f"[AUTO-DETECT] Tamil content detected ({tamil_char_count} Tamil characters)")
                    if not any(domain in url.lower() for domain in tamil_domains):
                        search_text = f"{url_result['title']} {url_result['text'][:300]}"
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to fetch URL content'
                }), 400
        
        if not search_text:
            return jsonify({
                'success': False,
                'message': 'Text or URL is required'
            }), 400
        
        print(f"[NEWS] Searching for related {language} news: {search_text[:100]}...")
        
        # Use dedicated Tamil classifier for Tamil news
        if language == 'ta':
            tamil_result = tamil_classifier.classify(search_text)
            related_articles = tamil_result.get('source_matches', [])
        else:
            related_articles = news_matcher.find_similar_articles(
                search_text,
                news_aggregator.get_all_articles_flat(max_articles_per_source=10, language=language),
                max_results=max_results,
                min_similarity=0.1
            )
        
        return jsonify({
            'success': True,
            'query': search_text[:200],
            'related_articles': related_articles,
            'total_found': len(related_articles),
            'language': language
        })
    
    except Exception as e:
        print(f"Related news search error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error searching for related news',
            'error': str(e)
        }), 500

@app.route('/api/news/trending', methods=['GET'])
def get_trending_news():
    """
    Get trending topics from all news sources
    """
    try:
        print("[NEWS] Fetching trending topics...")
        
        trending = news_aggregator.get_trending_topics(max_topics=15)
        
        return jsonify({
            'success': True,
            'trending_topics': trending
        })
    
    except Exception as e:
        print(f"Trending news error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching trending news',
            'error': str(e)
        }), 500

@app.route('/api/news/all-sources', methods=['GET'])
def get_all_news_sources():
    """
    Get latest news from all official sources
    """
    try:
        print("[NEWS] Fetching news from all sources...")
        
        all_news = news_aggregator.fetch_all_news(max_articles_per_source=5)
        
        # Format response
        sources_data = []
        for source_name, articles in all_news.items():
            sources_data.append({
                'source': source_name,
                'article_count': len(articles),
                'articles': articles[:5]  # Top 5 from each source
            })
        
        return jsonify({
            'success': True,
            'sources': sources_data,
            'total_sources': len(sources_data)
        })
    
    except Exception as e:
        print(f"All sources news error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching news from all sources',
            'error': str(e)
        }), 500

@app.route('/api/news/verify-with-sources', methods=['POST'])
def verify_with_sources():
    """
    Verify a news claim against language-specific official sources
    Returns: Matching articles, verification status, and credibility score
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        url = data.get('url', '')
        language = data.get('language', 'en')
        
        if not text and not url:
            return jsonify({
                'success': False,
                'message': 'Text or URL is required'
            }), 400
        
        # Get content to verify
        verify_text = text
        
        if url and not text:
            url_result = url_verifier.fetch_url_content(url)
            if url_result['success']:
                # Auto-detect language from URL domain
                tamil_domains = ['dinathanthi.com', 'dailythanthi.com', 'dinamalar.com', 'dinakaran.com', 'vikatan.com', 'puthiyathalaimurai.tv']
                if any(domain in url.lower() for domain in tamil_domains):
                    language = 'ta'
                    print(f"[AUTO-DETECT] Tamil source detected from URL domain")

                # For Tamil: use only title + first 300 chars of text (avoid nav menu noise)
                # For English: use title + full text
                if language == 'ta':
                    verify_text = f"{url_result['title']} {url_result['text'][:300]}"
                else:
                    verify_text = f"{url_result['title']} {url_result['text']}"

                # Also check content for Tamil characters
                tamil_char_count = len([c for c in verify_text if '\u0B80' <= c <= '\u0BFF'])
                if tamil_char_count > 10:
                    language = 'ta'
                    print(f"[AUTO-DETECT] Tamil content detected ({tamil_char_count} Tamil characters)")
                    # Re-trim for Tamil if just detected
                    if not any(domain in url.lower() for domain in tamil_domains):
                        verify_text = f"{url_result['title']} {url_result['text'][:300]}"
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to fetch URL content'
                }), 400

        print(f"[VERIFY] Verifying news against {language} sources: {verify_text[:100]}...")

        # Use dedicated Tamil classifier for Tamil news
        if language == 'ta':
            tamil_result = tamil_classifier.classify(verify_text)
            related_articles = tamil_result.get('source_matches', [])
        else:
            # Find related articles from English sources
            related_articles = news_matcher.find_similar_articles(
                verify_text,
                news_aggregator.get_all_articles_flat(max_articles_per_source=10, language=language),
                max_results=15,
                min_similarity=0.1
            )
        
        # Extract entities
        entities = news_matcher.extract_entities(verify_text)
        
        # Calculate credibility score based on matches (capped at 95)
        credibility_score = 0
        if related_articles:
            avg_similarity = sum(a.get('similarity_score', 0) for a in related_articles) / len(related_articles)
            source_diversity = len(set(a.get('source', '') for a in related_articles))
            match_factor = min(40, len(related_articles) * 4)
            credibility_score = min(95, int((avg_similarity * 0.4) + (source_diversity * 5) + match_factor))
        
        # Group articles by source
        articles_by_source = {}
        for article in related_articles:
            source = article.get('source', 'Unknown')
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        return jsonify({
            'success': True,
            'verification_status': 'verified' if related_articles else 'unverified',
            'credibility_score': credibility_score,
            'matching_articles': related_articles,
            'articles_by_source': articles_by_source,
            'entities_found': entities,
            'total_matches': len(related_articles),
            'sources_covered': len(articles_by_source),
            'language': language
        })
    
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error verifying news',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
