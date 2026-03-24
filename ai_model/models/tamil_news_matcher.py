"""
Tamil News Matcher - Dedicated matcher for Tamil news verification
Fetches live Tamil news from Google News Tamil RSS and matches against query
"""

import re
import requests
import feedparser
from typing import List, Dict
from urllib.parse import quote_plus
import time


class TamilNewsMatcher:
    """
    Dedicated Tamil news matcher.
    - Fetches live Tamil articles from Google News Tamil RSS (general + topic search)
    - Handles mixed Tamil+English queries (URL slugs + Tamil page content)
    - Returns related Tamil articles with similarity scores
    """

    TAMIL_RSS_SOURCES = {
        'Google News Tamil': 'https://news.google.com/rss?hl=ta&gl=IN&ceid=IN:ta',
        'Google News Tamil India': 'https://news.google.com/rss/headlines/section/geo/India?hl=ta&gl=IN&ceid=IN:ta',
    }

    TAMIL_STOP = set([
        'என்று', 'என்ற', 'ஆனால்',
        'இந்த', 'அந்த', 'இது', 'அது',
        'உள்ள', 'உள்ளது', 'செய்த',
        'செய்து', 'இருந்த', 'இருந்து',
        'வந்த', 'வந்து', 'தான்', 'மட்டும்',
        'கூட', 'போது', 'பின்', 'முன்',
        'மேலும்', 'அதன்', 'இதன்',
        'அவர்', 'இவர்', 'அவர்கள்',
        'இவர்கள்', 'ஒரு', 'பல', 'சில',
        'அனைத்து', 'எல்லா', 'மற்றும்',
        'அல்லது', 'என்னும்', 'ஆகும்',
        'ஆகிய', 'என்பது', 'என்பதால்',
        'கொண்டு', 'கொண்டார்',
        'கொண்டனர்', 'வருகின்றனர்',
        'வருகிறது', 'தெரிவித்தனர்',
        'தெரிவித்தார்', 'நடத்தி',
        'அறிவித்தனர்', 'அறிவித்தார்',
    ])

    ENGLISH_STOP = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'this', 'that', 'these', 'those', 'it', 'its',
        'as', 'if', 'not', 'no', 'so', 'than', 'too', 'very', 'just', 'now',
        'said', 'says', 'say', 'also', 'new', 'after', 'before', 'over', 'about',
        'into', 'news', 'report', 'latest', 'read', 'more', 'one', 'two', 'three',
    }

    def __init__(self):
        self._cache = {}
        self._cache_time = None
        self._search_cache = {}

    def _fetch_general_tamil_articles(self, max_per_source=25) -> List[Dict]:
        """Fetch live Tamil articles from Google News Tamil RSS (general feed)"""
        now = time.time()
        if self._cache_time and (now - self._cache_time) < 300 and self._cache:
            return self._cache.get('articles', [])

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        all_articles = []

        for source_name, url in self.TAMIL_RSS_SOURCES.items():
            try:
                resp = requests.get(url, timeout=8, headers=headers)
                resp.raise_for_status()
                feed = feedparser.parse(resp.content)
                count = 0
                for entry in feed.entries[:max_per_source]:
                    title = entry.get('title', '').strip()
                    if not title:
                        continue
                    summary = entry.get('summary', '').strip()
                    summary = summary[:400] if summary else title
                    all_articles.append({
                        'source': source_name,
                        'title': title,
                        'summary': summary,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                    })
                    count += 1
                print('[TAMIL] ' + source_name + ': ' + str(count) + ' articles')
            except Exception as e:
                print('[TAMIL ERROR] ' + source_name + ': ' + str(e))

        self._cache = {'articles': all_articles}
        self._cache_time = now
        print('[TAMIL] General feed total: ' + str(len(all_articles)))
        return all_articles

    def _fetch_topic_search_articles(self, search_query: str, max_results=25) -> List[Dict]:
        """Search Google News Tamil RSS with a specific query string."""
        if not search_query:
            return []

        cache_key = search_query[:50]
        now = time.time()
        if cache_key in self._search_cache:
            cached_time, cached_articles = self._search_cache[cache_key]
            if now - cached_time < 300:
                print('[TAMIL SEARCH] Using cached results for: ' + cache_key[:40])
                return cached_articles

        try:
            encoded_query = quote_plus(search_query)
            search_url = 'https://news.google.com/rss/search?q=' + encoded_query + '&hl=ta&gl=IN&ceid=IN:ta'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            print('[TAMIL SEARCH] Searching: ' + search_query[:60])
            resp = requests.get(search_url, timeout=10, headers=headers)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            articles = []
            for entry in feed.entries[:max_results]:
                title = entry.get('title', '').strip()
                if not title:
                    continue
                summary = entry.get('summary', '').strip()
                summary = summary[:400] if summary else title
                source = 'Google News Tamil'
                if ' - ' in title:
                    parts = title.rsplit(' - ', 1)
                    if len(parts) == 2 and len(parts[1]) < 40:
                        source = parts[1].strip()
                        title = parts[0].strip()
                articles.append({
                    'source': source,
                    'title': title,
                    'summary': summary,
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                })
            print('[TAMIL SEARCH] Found ' + str(len(articles)) + ' articles')
            self._search_cache[cache_key] = (now, articles)
            return articles
        except Exception as e:
            print('[TAMIL SEARCH ERROR] ' + str(e))
            return []

    def _extract_tamil_tokens(self, text: str) -> List[str]:
        """Extract Tamil-script tokens from text"""
        if not text:
            return []
        tokens = re.findall(r'[஀-௿]+', text)
        result = []
        seen = set()
        for t in tokens:
            if len(t) >= 2 and t not in self.TAMIL_STOP and t not in seen:
                seen.add(t)
                result.append(t)
        return result

    def _extract_english_tokens(self, text: str) -> List[str]:
        """Extract English tokens from text"""
        if not text:
            return []
        text_lower = text.lower()
        tokens = re.findall(r'[a-z]+', text_lower)
        result = []
        seen = set()
        for t in tokens:
            if len(t) >= 3 and t not in self.ENGLISH_STOP and t not in seen:
                seen.add(t)
                result.append(t)
        return result

    def _build_search_query(self, text: str) -> str:
        """
        Build best search query from mixed Tamil+English text.
        Uses first 150 chars (title area) for Tamil tokens to avoid nav menu noise.
        """
        # Use only first 150 chars for Tamil (title is most specific)
        title_area = text[:150]
        rest_area = text[150:400]

        title_tamil = self._extract_tamil_tokens(title_area)
        rest_tamil = self._extract_tamil_tokens(rest_area)
        english_tokens = self._extract_english_tokens(text[:300])

        search_parts = []
        # Title Tamil tokens first (most specific)
        if title_tamil:
            title_sorted = sorted(title_tamil, key=len, reverse=True)
            search_parts.extend(title_sorted[:3])
        # Add some from rest if needed
        if len(search_parts) < 3 and rest_tamil:
            rest_sorted = sorted(rest_tamil, key=len, reverse=True)
            search_parts.extend(rest_sorted[:2])
        # Add English keywords
        if english_tokens:
            english_sorted = sorted(english_tokens, key=len, reverse=True)
            search_parts.extend(english_sorted[:2])

        return ' '.join(search_parts[:5])

    def _score_article(self, tamil_query: set, english_query: set, article: Dict) -> float:
        """
        Score article against both Tamil and English query tokens.
        Tamil tokens match Tamil article text.
        English tokens match English words in article titles (many Tamil news sites use English words).
        """
        title = article.get('title', '')
        summary = article.get('summary', '')

        title_tamil = set(self._extract_tamil_tokens(title))
        title_english = set(self._extract_english_tokens(title))
        summary_tamil = set(self._extract_tamil_tokens(summary))
        summary_english = set(self._extract_english_tokens(summary))

        all_tamil = title_tamil | summary_tamil
        all_english = title_english | summary_english

        # Check if any overlap at all
        tamil_overlap = len(tamil_query & all_tamil) if tamil_query else 0
        english_overlap = len(english_query & all_english) if english_query else 0

        if tamil_overlap == 0 and english_overlap == 0:
            return 0.0

        score = 0.0

        # Tamil scoring (primary)
        if tamil_query and all_tamil:
            title_t_overlap = len(tamil_query & title_tamil) / max(len(tamil_query), 1)
            summary_t_overlap = len(tamil_query & summary_tamil) / max(len(tamil_query), 1)
            jaccard_t = len(tamil_query & all_tamil) / max(len(tamil_query | all_tamil), 1)
            score += (title_t_overlap * 0.4) + (summary_t_overlap * 0.15) + (jaccard_t * 0.2)

        # English scoring (secondary - for mixed titles)
        if english_query and all_english:
            title_e_overlap = len(english_query & title_english) / max(len(english_query), 1)
            summary_e_overlap = len(english_query & summary_english) / max(len(english_query), 1)
            score += (title_e_overlap * 0.2) + (summary_e_overlap * 0.05)

        # Boost for multiple title hits
        title_hits = len(tamil_query & title_tamil) + len(english_query & title_english)
        if title_hits >= 4:
            score = min(1.0, score * 2.0)
        elif title_hits >= 3:
            score = min(1.0, score * 1.6)
        elif title_hits >= 2:
            score = min(1.0, score * 1.3)
        elif title_hits >= 1:
            score = min(1.0, score * 1.1)

        return score

    def find_related_tamil_news(self, query_text: str, max_results: int = 10) -> List[Dict]:
        """
        Find Tamil news articles related to the query.
        Handles mixed Tamil+English queries (e.g. from URL fetcher output).
        """
        tamil_tokens = set(self._extract_tamil_tokens(query_text))
        english_tokens = set(self._extract_english_tokens(query_text))

        if not tamil_tokens and not english_tokens:
            print('[TAMIL] No tokens extracted from query')
            return []

        print('[TAMIL] Tamil tokens (' + str(len(tamil_tokens)) + '): ' + str(list(tamil_tokens)[:8]))
        print('[TAMIL] English tokens (' + str(len(english_tokens)) + '): ' + str(list(english_tokens)[:8]))

        # Build search query
        search_query = self._build_search_query(query_text)
        print('[TAMIL] Search query: ' + search_query[:60])

        # Fetch: targeted search + general feed
        search_articles = self._fetch_topic_search_articles(search_query, max_results=25)

        # Fallback: if search returned nothing, try with just the 2 longest Tamil tokens
        if not search_articles and tamil_tokens:
            fallback_tokens = sorted(tamil_tokens, key=len, reverse=True)[:2]
            fallback_query = ' '.join(fallback_tokens)
            print('[TAMIL] Fallback search with: ' + fallback_query)
            search_articles = self._fetch_topic_search_articles(fallback_query, max_results=25)

        general_articles = self._fetch_general_tamil_articles()

        # Deduplicate by link/title
        seen_keys = set()
        all_articles = []
        for a in search_articles + general_articles:
            key = a.get('link', '') or a.get('title', '')
            if key not in seen_keys:
                seen_keys.add(key)
                all_articles.append(a)

        print('[TAMIL] Total unique articles to score: ' + str(len(all_articles)))

        results = []
        for article in all_articles:
            score = self._score_article(tamil_tokens, english_tokens, article)
            if score > 0.01:
                article_copy = article.copy()
                article_copy['similarity_score'] = round(score * 100, 1)
                results.append(article_copy)

        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        print('[TAMIL] Found ' + str(len(results)) + ' related articles')
        return results[:max_results]
