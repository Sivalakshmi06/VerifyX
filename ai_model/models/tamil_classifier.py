"""
Tamil News Classifier
Verifies Tamil news against direct Tamil newspaper RSS feeds.
Sources: Dinamalar, Dinakaran, Daily Thanthi, Vikatan, Puthiya Thalaimurai,
         Polimer News, Maalai Malar, Nakkheeran, OneIndia Tamil, Samayam Tamil
"""

import re
import time
import requests
import feedparser
from typing import List, Dict, Tuple
from urllib.parse import quote_plus


class TamilClassifier:

    # ── Direct Tamil newspaper RSS feeds ──
    TAMIL_NEWSPAPER_RSS = {
        'Dinamalar':          'https://www.dinamalar.com/rss/news.xml',
        'Daily Thanthi':      'https://www.dailythanthi.com/rss/home/rss.xml',
        'Dinakaran':          'https://www.dinakaran.com/rss.asp',
        'Puthiya Thalaimurai':'https://www.puthiyathalaimurai.com/rss.xml',
        'Polimer News':       'https://www.polimernews.com/rss.xml',
        'OneIndia Tamil':     'https://tamil.oneindia.com/rss/tamil-news-fb.xml',
        'Samayam Tamil':      'https://tamil.samayam.com/rssfeed/msid-2128839640,feedtype-sjson.cms',
        'Vikatan':            'https://www.vikatan.com/rss.xml',
        'Maalai Malar':       'https://www.maalaimalar.com/rss/news.xml',
    }

    # Google News Tamil as fallback
    GOOGLE_TAMIL_RSS = {
        'Google News Tamil':       'https://news.google.com/rss?hl=ta&gl=IN&ceid=IN:ta',
        'Google News Tamil India':  'https://news.google.com/rss/headlines/section/geo/India?hl=ta&gl=IN&ceid=IN:ta',
    }

    TAMIL_STOP = {
        'என்று', 'என்ற', 'ஆனால்', 'இந்த', 'அந்த', 'இது', 'அது',
        'உள்ள', 'உள்ளது', 'செய்த', 'செய்து', 'இருந்த', 'இருந்து',
        'வந்த', 'வந்து', 'தான்', 'மட்டும்', 'கூட', 'போது', 'பின்',
        'முன்', 'மேலும்', 'அதன்', 'இதன்', 'அவர்', 'இவர்', 'அவர்கள்',
        'இவர்கள்', 'ஒரு', 'பல', 'சில', 'அனைத்து', 'எல்லா', 'மற்றும்',
        'அல்லது', 'என்னும்', 'ஆகும்', 'ஆகிய', 'என்பது', 'என்பதால்',
        'கொண்டு', 'கொண்டார்', 'கொண்டனர்', 'வருகின்றனர்', 'வருகிறது',
        'தெரிவித்தனர்', 'தெரிவித்தார்', 'நடத்தி', 'அறிவித்தனர்',
        'அறிவித்தார்', 'என்னவென்றால்', 'ஆகவே', 'எனவே', 'ஆனாலும்',
        'இதனால்', 'அதனால்', 'இதில்', 'அதில்', 'இங்கு', 'அங்கு',
    }

    ENGLISH_STOP = {
        'the','a','an','and','or','but','in','on','at','to','for','of','with',
        'by','from','is','are','was','were','be','been','have','has','had',
        'do','does','did','will','would','could','should','may','might',
        'this','that','these','those','it','its','as','if','not','no','so',
        'than','too','very','just','now','said','says','say','also','new',
        'after','before','over','about','into','news','report','latest',
        'read','more','one','two','three','today','yesterday',
    }

    # Fake news linguistic patterns in Tamil
    FAKE_PATTERNS = [
        r'வைரல்',          # viral
        r'அதிர்ச்சி',      # shocking
        r'ரகசியம்',        # secret
        r'போலி',           # fake
        r'மோசடி',          # scam/fraud
        r'நம்பமுடியாத',    # unbelievable
        r'உடனே பகிருங்கள்', # share immediately
        r'உண்மை வெளியானது', # truth revealed
        r'மறைக்கப்பட்ட',   # hidden
        r'சதி',            # conspiracy
        r'அரசு மறைக்கிறது', # govt hiding
        r'100%\s*உண்மை',   # 100% true
        r'breaking',
        r'urgent',
        r'share now',
        r'forward this',
    ]

    def __init__(self):
        self._article_cache: Dict = {}
        self._cache_time: float = 0
        self._search_cache: Dict = {}
        self._cache_ttl = 300  # 5 min

    # ──────────────────────────────────────────────
    # MAIN ENTRY POINT
    # ──────────────────────────────────────────────
    def classify(self, text: str) -> Dict:
        """
        Full Tamil fake/real classification pipeline.
        Returns verdict dict with prediction, confidence, explanation, matches.
        """
        print(f"[TAMIL-CLS] Classifying: {text[:80]}...")

        # Step 1: Fetch articles from Tamil newspapers
        articles = self._fetch_all_tamil_articles()

        # Step 2: Score articles against query
        matches = self._find_matches(text, articles)

        # Step 3: Linguistic fake signal analysis
        fake_signals = self._detect_fake_signals(text)

        # Step 4: Decide verdict
        verdict = self._decide_verdict(text, matches, fake_signals)

        print(f"[TAMIL-CLS] Verdict: {verdict['prediction']} ({verdict['confidence']*100:.1f}%)")
        return verdict

    # ──────────────────────────────────────────────
    # FETCH
    # ──────────────────────────────────────────────
    def _fetch_all_tamil_articles(self) -> List[Dict]:
        now = time.time()
        if self._cache_time and (now - self._cache_time) < self._cache_ttl and self._article_cache:
            return self._article_cache.get('articles', [])

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        all_articles = []
        fetched_sources = 0

        # Try direct newspaper RSS first
        for source, url in self.TAMIL_NEWSPAPER_RSS.items():
            try:
                resp = requests.get(url, timeout=6, headers=headers)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                count = 0
                for entry in feed.entries[:30]:
                    title = entry.get('title', '').strip()
                    if not title:
                        continue
                    summary = entry.get('summary', '')[:400]
                    all_articles.append({
                        'source': source,
                        'title': title,
                        'summary': summary or title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'is_newspaper': True,
                    })
                    count += 1
                if count > 0:
                    fetched_sources += 1
                    print(f"[TAMIL-CLS] {source}: {count} articles")
            except Exception as e:
                print(f"[TAMIL-CLS] {source} failed: {e}")

        # Always add Google News Tamil as supplement
        for source, url in self.GOOGLE_TAMIL_RSS.items():
            try:
                resp = requests.get(url, timeout=8, headers=headers)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                count = 0
                for entry in feed.entries[:25]:
                    title = entry.get('title', '').strip()
                    if not title:
                        continue
                    # Strip source suffix from Google News titles
                    display_title = title
                    display_source = source
                    if ' - ' in title:
                        parts = title.rsplit(' - ', 1)
                        if len(parts[1]) < 40:
                            display_title = parts[0].strip()
                            display_source = parts[1].strip()
                    all_articles.append({
                        'source': display_source,
                        'title': display_title,
                        'summary': entry.get('summary', '')[:400] or display_title,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'is_newspaper': False,
                    })
                    count += 1
                print(f"[TAMIL-CLS] {source}: {count} articles")
            except Exception as e:
                print(f"[TAMIL-CLS] {source} failed: {e}")

        self._article_cache = {'articles': all_articles}
        self._cache_time = now
        print(f"[TAMIL-CLS] Total articles fetched: {len(all_articles)} from {fetched_sources} direct sources")
        return all_articles

    def _fetch_search_articles(self, query: str) -> List[Dict]:
        """Google News Tamil search for specific query."""
        cache_key = query[:60]
        now = time.time()
        if cache_key in self._search_cache:
            t, arts = self._search_cache[cache_key]
            if now - t < self._cache_ttl:
                return arts

        try:
            from urllib.parse import quote_plus
            url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=ta&gl=IN&ceid=IN:ta"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, timeout=10, headers=headers)
            feed = feedparser.parse(resp.content)
            articles = []
            for entry in feed.entries[:20]:
                title = entry.get('title', '').strip()
                if not title:
                    continue
                src = 'Google News Tamil'
                if ' - ' in title:
                    parts = title.rsplit(' - ', 1)
                    if len(parts[1]) < 40:
                        title = parts[0].strip()
                        src = parts[1].strip()
                articles.append({
                    'source': src, 'title': title,
                    'summary': entry.get('summary', '')[:400] or title,
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'is_newspaper': False,
                })
            print(f"[TAMIL-CLS] Search '{query[:40]}': {len(articles)} results")
            self._search_cache[cache_key] = (now, articles)
            return articles
        except Exception as e:
            print(f"[TAMIL-CLS] Search error: {e}")
            return []

    # ──────────────────────────────────────────────
    # TOKENIZE & SCORE
    # ──────────────────────────────────────────────
    def _tamil_tokens(self, text: str) -> set:
        tokens = re.findall(r'[஀-௿]+', text)
        return {t for t in tokens if len(t) >= 2 and t not in self.TAMIL_STOP}

    def _english_tokens(self, text: str) -> set:
        tokens = re.findall(r'[a-z]+', text.lower())
        return {t for t in tokens if len(t) >= 3 and t not in self.ENGLISH_STOP}

    def _build_search_query(self, text: str) -> str:
        title_area = text[:150]
        tamil_toks = sorted(self._tamil_tokens(title_area), key=len, reverse=True)[:3]
        eng_toks = sorted(self._english_tokens(text[:200]), key=len, reverse=True)[:2]
        parts = list(tamil_toks) + list(eng_toks)
        return ' '.join(parts[:5])

    def _score_article(self, q_tamil: set, q_english: set, article: Dict) -> float:
        title = article.get('title', '')
        summary = article.get('summary', '')

        t_title = self._tamil_tokens(title)
        t_summary = self._tamil_tokens(summary)
        e_title = self._english_tokens(title)
        e_summary = self._english_tokens(summary)

        all_tamil = t_title | t_summary
        all_english = e_title | e_summary

        if not (q_tamil & all_tamil) and not (q_english & all_english):
            return 0.0

        score = 0.0

        if q_tamil and all_tamil:
            title_hit = len(q_tamil & t_title) / max(len(q_tamil), 1)
            sum_hit   = len(q_tamil & t_summary) / max(len(q_tamil), 1)
            jaccard   = len(q_tamil & all_tamil) / max(len(q_tamil | all_tamil), 1)
            score += title_hit * 0.45 + sum_hit * 0.15 + jaccard * 0.20

        if q_english and all_english:
            title_hit = len(q_english & e_title) / max(len(q_english), 1)
            sum_hit   = len(q_english & e_summary) / max(len(q_english), 1)
            score += title_hit * 0.15 + sum_hit * 0.05

        # Boost for newspaper sources (more credible)
        if article.get('is_newspaper'):
            score *= 1.3

        # Boost for multiple title hits
        title_hits = len(q_tamil & t_title) + len(q_english & e_title)
        if title_hits >= 4:   score = min(1.0, score * 2.0)
        elif title_hits >= 3: score = min(1.0, score * 1.6)
        elif title_hits >= 2: score = min(1.0, score * 1.3)

        return score

    def _find_matches(self, text: str, articles: List[Dict]) -> List[Dict]:
        q_tamil   = self._tamil_tokens(text)
        q_english = self._english_tokens(text)

        # Also do a targeted search
        search_query = self._build_search_query(text)
        if search_query:
            search_arts = self._fetch_search_articles(search_query)
            # Deduplicate
            seen = {a['link'] or a['title'] for a in articles}
            for a in search_arts:
                key = a.get('link') or a.get('title')
                if key not in seen:
                    seen.add(key)
                    articles.append(a)

        results = []
        for article in articles:
            score = self._score_article(q_tamil, q_english, article)
            if score > 0.01:
                a = article.copy()
                a['similarity_score'] = round(score * 100, 1)
                results.append(a)

        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        print(f"[TAMIL-CLS] Matches found: {len(results)}, top score: {results[0]['similarity_score'] if results else 0}")
        return results[:10]

    # ──────────────────────────────────────────────
    # FAKE SIGNAL DETECTION
    # ──────────────────────────────────────────────
    def _detect_fake_signals(self, text: str) -> Dict:
        signals = []
        score = 0

        for pattern in self.FAKE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                signals.append(pattern)
                score += 1

        # Excessive punctuation
        if text.count('!') >= 3:
            signals.append('excessive_exclamation')
            score += 1
        if text.count('?') >= 3:
            signals.append('excessive_questions')
            score += 0.5

        # ALL CAPS words
        caps_words = [w for w in text.split() if len(w) > 3 and w.isupper()]
        if len(caps_words) >= 3:
            signals.append('all_caps')
            score += 1

        # Very short text (likely a rumour snippet)
        if len(text.strip()) < 80:
            signals.append('very_short_text')
            score += 0.5

        return {'signals': signals, 'score': score}

    # ──────────────────────────────────────────────
    # VERDICT
    # ──────────────────────────────────────────────
    def _decide_verdict(self, text: str, matches: List[Dict], fake_signals: Dict) -> Dict:
        strong_matches = [m for m in matches if m['similarity_score'] >= 12]
        newspaper_matches = [m for m in strong_matches if m.get('is_newspaper')]
        top_score = matches[0]['similarity_score'] if matches else 0
        match_count = len(strong_matches)
        fake_score = fake_signals['score']
        matched_sources = list({m['source'] for m in strong_matches})

        print(f"[TAMIL-CLS] strong_matches={match_count}, newspaper={len(newspaper_matches)}, top={top_score}, fake_signals={fake_score}")

        # ── Decision tree ──

        # 1. Newspaper source match → strong REAL signal
        if len(newspaper_matches) >= 1 or (match_count >= 1 and top_score >= 25):
            prediction = 'real'
            confidence = min(0.92, 0.68 + len(newspaper_matches) * 0.06 + match_count * 0.03)
            verdict_ta = f"இந்த செய்தி {', '.join(matched_sources[:2]) or 'நம்பகமான ஆதாரம்'} போன்ற நம்பகமான தமிழ் செய்தி ஆதாரங்களில் உறுதிப்படுத்தப்பட்டுள்ளது."
            verdict_en = f"Verified in Tamil source(s): {', '.join(matched_sources[:3]) or 'trusted Tamil news'}."

        # 2. Multiple matches (Google News) → likely REAL
        elif match_count >= 3 or top_score >= 40:
            prediction = 'real'
            confidence = min(0.85, 0.62 + match_count * 0.05)
            verdict_ta = f"இந்த செய்தி {match_count} நம்பகமான ஆதாரங்களில் காணப்படுகிறது."
            verdict_en = f"Found in {match_count} trusted Tamil sources: {', '.join(matched_sources[:3])}."

        # 3. Weak match + fake signals → FAKE
        elif match_count >= 1 and fake_score >= 2:
            prediction = 'fake'
            confidence = min(0.82, 0.60 + fake_score * 0.05)
            verdict_ta = f"இந்த செய்தியில் போலி செய்தி அறிகுறிகள் உள்ளன மற்றும் நம்பகமான ஆதாரங்களில் உறுதிப்படவில்லை."
            verdict_en = f"Fake news signals detected ({len(fake_signals['signals'])} indicators). Weak source match only."

        # 4. Single weak match, no fake signals → unverified (lean fake)
        elif match_count == 1 and fake_score < 2:
            prediction = 'fake'
            confidence = 0.62
            verdict_ta = "இந்த செய்தி போதுமான ஆதாரங்களில் உறுதிப்படவில்லை. சரிபார்க்க முடியவில்லை."
            verdict_en = "Only one weak source match. Cannot verify this news."

        # 5. No match + fake signals → strong FAKE
        elif match_count == 0 and fake_score >= 2:
            prediction = 'fake'
            confidence = min(0.88, 0.70 + fake_score * 0.04)
            verdict_ta = f"இந்த செய்தி எந்த தமிழ் செய்தித்தாளிலும் காணப்படவில்லை மற்றும் போலி செய்தி அறிகுறிகள் உள்ளன."
            verdict_en = f"Not found in any Tamil newspaper. {len(fake_signals['signals'])} fake news indicators detected."

        # 6. No match, no fake signals → unverified (lean fake)
        else:
            prediction = 'fake'
            confidence = 0.72
            verdict_ta = "இந்த செய்தி எந்த நம்பகமான தமிழ் செய்தி ஆதாரத்திலும் காணப்படவில்லை. இது போலி அல்லது சரிபார்க்கப்படாத செய்தியாக இருக்கலாம்."
            verdict_en = "Not found in any trusted Tamil newspaper or news source. Likely fake or unverified."

        explanation = (
            f"{'✅' if prediction == 'real' else '❌'} {verdict_ta} "
            f"{verdict_en} Confidence: {confidence*100:.1f}%."
        )

        return {
            'prediction': prediction,
            'confidence': round(confidence, 3),
            'explanation': explanation,
            'verdict_tamil': verdict_ta,
            'verdict_english': verdict_en,
            'source_matches': matches[:5],
            'strong_match_count': match_count,
            'top_score': top_score,
            'fake_signals': fake_signals['signals'],
            'matched_sources': matched_sources,
        }
