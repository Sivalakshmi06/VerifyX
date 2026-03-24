"""
News Matcher - English-only news article matching
Uses TF-IDF cosine similarity + targeted Google News search for topic-specific matching
"""

import re
import requests
import feedparser
from typing import List, Dict
from collections import Counter
from urllib.parse import quote_plus
import math
import time


class NewsMatcher:
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'same', 'so', 'than', 'too', 'very',
            'as', 'if', 'just', 'now', 'said', 'says', 'say', 'get', 'got',
            'make', 'made', 'take', 'taken', 'see', 'seen', 'come', 'came',
            'go', 'went', 'know', 'knew', 'think', 'thought', 'use', 'used',
            'http', 'https', 'www', 'com', 'org', 'net', 'utm', 'source',
            'updated', 'articleshow', 'cms', 'timesofindia', 'indiatimes',
            'read', 'more', 'also', 'new', 'one', 'two', 'three', 'first',
            'last', 'after', 'before', 'over', 'under', 'about', 'into',
            'through', 'during', 'including', 'until', 'against', 'among',
            'throughout', 'despite', 'towards', 'upon', 'concerning',
            'news', 'report', 'reports', 'reported', 'reporting', 'latest'
        }
        self.generic_words = {
            'man', 'woman', 'year', 'time', 'day', 'week', 'month',
            'big', 'high', 'low', 'major', 'minor', 'top', 'key', 'amid',
            'hundred', 'thousand', 'million', 'billion',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'june', 'july', 'august',
            'september', 'october', 'november', 'december'
        }
        self._search_cache = {}

    def _extract_keywords(self, text, min_length=3):
        """Extract meaningful English keywords, filtering noise"""
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'https?://\S+', ' ', text)
        text = re.sub(r'www\.\S+', ' ', text)
        text = re.sub(r'[^a-z\s]', ' ', text)
        words = text.split()
        keywords = [w for w in words if len(w) >= min_length and w not in self.stop_words]
        seen = set()
        result = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
        return result

    def _specific_keywords(self, keywords):
        """Filter out generic words, keep only topic-specific ones"""
        return [kw for kw in keywords if kw not in self.generic_words]

    def _extract_proper_nouns(self, text):
        """Extract capitalized words (likely named entities: people, places, orgs)"""
        # Work on original text before lowercasing
        words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        # Filter out sentence-start words (preceded by . or start of text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentence_starts = set()
        for s in sentences:
            first = re.match(r'\b([A-Z][a-z]+)\b', s.strip())
            if first:
                sentence_starts.add(first.group(1))
        proper = [w for w in words if w not in sentence_starts]
        # Also grab consecutive capitalized words as phrases (e.g. "Prime Minister Modi")
        phrases = re.findall(r'\b(?:[A-Z][a-z]+ ){1,3}[A-Z][a-z]+\b', text)
        return proper, phrases

    def _extract_bigrams(self, keywords):
        """Extract meaningful bigrams from keyword list"""
        bigrams = []
        for i in range(len(keywords) - 1):
            a, b = keywords[i], keywords[i+1]
            if len(a) >= 4 and len(b) >= 4:
                bigrams.append(f"{a} {b}")
        return bigrams

    def _build_search_query(self, query_text):
        """Build a targeted search query prioritizing named entities and key phrases"""
        # 1. Extract proper nouns from original text (before lowercasing)
        proper_nouns, noun_phrases = self._extract_proper_nouns(query_text[:500])

        # 2. Extract regular keywords
        keywords = self._extract_keywords(query_text[:500])
        specific = self._specific_keywords(keywords)

        # 3. Build query: noun phrases first, then proper nouns, then specific keywords
        query_parts = []
        seen = set()

        # Add multi-word noun phrases (highest priority)
        for phrase in noun_phrases[:2]:
            phrase_lower = phrase.lower()
            if phrase_lower not in seen and len(phrase) > 5:
                query_parts.append(f'"{phrase}"')
                seen.add(phrase_lower)

        # Add individual proper nouns
        for noun in proper_nouns:
            noun_lower = noun.lower()
            if noun_lower not in seen and noun_lower not in self.stop_words:
                query_parts.append(noun)
                seen.add(noun_lower)
                if len(query_parts) >= 4:
                    break

        # Fill remaining slots with specific keywords (sorted by length)
        if len(query_parts) < 5:
            specific_sorted = sorted(set(specific), key=len, reverse=True)
            for kw in specific_sorted:
                if kw not in seen:
                    query_parts.append(kw)
                    seen.add(kw)
                    if len(query_parts) >= 5:
                        break

        query = ' '.join(query_parts[:5])
        print(f'[SEARCH] Built query: {query}')
        return query

    def _fetch_topic_search_articles(self, search_query, max_results=25):
        """
        Search Google News English RSS with topic-specific keywords.
        Finds articles about the specific topic even if not in general RSS feed.
        """
        if not search_query:
            return []

        cache_key = search_query[:50]
        now = time.time()
        if cache_key in self._search_cache:
            cached_time, cached_articles = self._search_cache[cache_key]
            if now - cached_time < 300:
                print('[SEARCH] Using cached results for: ' + cache_key[:40])
                return cached_articles

        try:
            encoded_query = quote_plus(search_query)
            search_url = 'https://news.google.com/rss/search?q=' + encoded_query + '&hl=en-IN&gl=IN&ceid=IN:en'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            print('[SEARCH] Searching Google News: ' + search_query[:60])
            resp = requests.get(search_url, timeout=10, headers=headers)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            articles = []
            for entry in feed.entries[:max_results]:
                title = entry.get('title', '').strip()
                if not title:
                    continue
                summary = entry.get('summary', '').strip()
                summary = summary[:500] if summary else title
                # Extract source from title (Google News appends " - Source Name")
                source = 'Google News'
                if ' - ' in title:
                    parts = title.rsplit(' - ', 1)
                    if len(parts) == 2 and len(parts[1]) < 50:
                        source = parts[1].strip()
                        title = parts[0].strip()
                articles.append({
                    'source': source,
                    'title': title,
                    'summary': summary,
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                })
            print('[SEARCH] Found ' + str(len(articles)) + ' articles for: ' + search_query[:40])
            self._search_cache[cache_key] = (now, articles)
            return articles
        except Exception as e:
            print('[SEARCH ERROR] ' + str(e))
            return []

    def _tfidf_vectors(self, query_kw, articles_kw):
        all_docs = [query_kw] + articles_kw
        doc_count = len(all_docs)
        vocab = set(query_kw)
        idf = {}
        for term in vocab:
            df = sum(1 for doc in all_docs if term in doc)
            idf[term] = math.log((doc_count + 1) / (df + 1)) + 1
        tf_q = Counter(query_kw)
        total_q = max(len(query_kw), 1)
        vec_q = {t: (tf_q[t] / total_q) * idf[t] for t in query_kw}
        return vec_q, idf

    def _cosine(self, vec1, vec2_kw, idf):
        tf2 = Counter(vec2_kw)
        total2 = max(len(vec2_kw), 1)
        vec2 = {t: (tf2[t] / total2) * idf.get(t, 0) for t in vec2_kw if t in idf}
        common = set(vec1.keys()) & set(vec2.keys())
        if not common:
            return 0.0
        dot = sum(vec1[t] * vec2[t] for t in common)
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    def find_similar_articles(self, query_text, articles, max_results=10, min_similarity=0.05):
        """
        Find English articles similar to query.
        1. Does targeted Google News search for topic-specific articles
        2. Combines with provided RSS articles
        3. Scores all using TF-IDF cosine similarity
        """
        # Step 1: targeted Google News search
        search_query = self._build_search_query(query_text)
        search_articles = self._fetch_topic_search_articles(search_query, max_results=25) if search_query else []

        # Step 2: combine search results with RSS articles, deduplicate
        seen_keys = set()
        all_articles = []
        for a in search_articles + (articles or []):
            key = a.get('link', '') or a.get('title', '')
            if key not in seen_keys:
                seen_keys.add(key)
                all_articles.append(a)

        if not all_articles:
            return []

        query_kw = self._extract_keywords(query_text)
        if not query_kw:
            print('[MATCHING] No keywords extracted from query')
            return []

        query_specific = set(self._specific_keywords(query_kw))
        query_set = set(query_kw)
        print('[MATCHING] Query keywords: ' + str(query_kw[:20]))
        print('[MATCHING] Specific keywords: ' + str(list(query_specific)[:15]))
        print('[MATCHING] Total articles to score: ' + str(len(all_articles)))

        articles_title_kw = [self._extract_keywords(a.get('title', '')) for a in all_articles]
        articles_summary_kw = [self._extract_keywords(a.get('summary', '')) for a in all_articles]
        vec_q, idf = self._tfidf_vectors(query_kw, articles_title_kw + articles_summary_kw)

        # Extract proper nouns from query for phrase matching
        query_proper, query_phrases = self._extract_proper_nouns(query_text[:500])
        query_proper_lower = {p.lower() for p in query_proper}

        results = []
        for i, article in enumerate(all_articles):
            title_kw = articles_title_kw[i]
            summary_kw = articles_summary_kw[i]
            title_set = set(title_kw)
            summary_set = set(summary_kw)
            article_all_kw = title_set | summary_set

            # Gate: must share at least 2 specific keywords OR 1 proper noun
            specific_overlap = query_specific & article_all_kw
            proper_overlap = query_proper_lower & article_all_kw
            if query_specific:
                if len(specific_overlap) < 2 and not proper_overlap:
                    continue

            title_sim = self._cosine(vec_q, title_kw, idf)
            summary_sim = self._cosine(vec_q, summary_kw, idf)
            title_overlap = len(query_set & title_set) / max(len(query_set), 1)
            summary_overlap = len(query_set & summary_set) / max(len(query_set), 1)
            title_score = max(title_sim, title_overlap * 0.8)
            summary_score = max(summary_sim, summary_overlap * 0.6)
            final_score = (title_score * 0.7) + (summary_score * 0.3)

            n_specific_title = len(query_specific & title_set)
            n_proper_title = len(query_proper_lower & title_set)

            # Boost for proper noun matches in title (strong signal)
            if n_proper_title >= 2:
                final_score = min(1.0, final_score * 2.2)
            elif n_proper_title >= 1:
                final_score = min(1.0, final_score * 1.6)

            if n_specific_title >= 4:
                final_score = min(1.0, final_score * 2.0)
            elif n_specific_title >= 3:
                final_score = min(1.0, final_score * 1.5)
            elif n_specific_title >= 2:
                final_score = min(1.0, final_score * 1.3)
            elif n_specific_title >= 1:
                final_score = min(1.0, final_score * 1.1)

            # Phrase match bonus: check if any query noun phrase appears in article title
            article_title_raw = article.get('title', '').lower()
            for phrase in query_phrases:
                if phrase.lower() in article_title_raw:
                    final_score = min(1.0, final_score * 1.8)
                    break

            if final_score >= min_similarity:
                article_copy = article.copy()
                article_copy['similarity_score'] = round(final_score * 100, 1)
                results.append(article_copy)

        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        print('[MATCHING] Found ' + str(len(results)) + ' relevant articles above threshold ' + str(min_similarity))
        return results[:max_results]

    def find_duplicate_or_similar(self, article, other_articles, similarity_threshold=0.7):
        article_text = article.get('title', '') + ' ' + article.get('summary', '')
        duplicates = []
        for other in other_articles:
            if other.get('link') == article.get('link'):
                continue
            other_text = other.get('title', '') + ' ' + other.get('summary', '')
            a_kw = self._extract_keywords(article_text)
            o_kw = self._extract_keywords(other_text)
            if not a_kw or not o_kw:
                continue
            vec_q, idf = self._tfidf_vectors(a_kw, [o_kw])
            sim = self._cosine(vec_q, o_kw, idf)
            if sim >= similarity_threshold:
                c = other.copy()
                c['similarity_score'] = round(sim * 100, 1)
                duplicates.append(c)
        return sorted(duplicates, key=lambda x: x['similarity_score'], reverse=True)

    def extract_entities(self, text):
        entities = {'locations': [], 'organizations': [], 'people': []}
        if not text:
            return entities
        text_lower = text.lower()
        location_keywords = [
            'india', 'delhi', 'mumbai', 'bangalore', 'kolkata', 'hyderabad', 'pune', 'chennai',
            'tamil nadu', 'tamilnadu', 'coimbatore', 'madurai', 'salem', 'thoothukudi',
            'tirunelveli', 'vellore', 'kanchipuram', 'villupuram', 'cuddalore',
            'us', 'usa', 'america', 'uk', 'britain', 'china', 'pakistan', 'russia',
            'europe', 'asia', 'africa', 'australia', 'canada', 'japan', 'korea',
            'iran', 'israel', 'middle east', 'gulf', 'saudi', 'iraq', 'ukraine',
            'taiwan', 'hong kong', 'south korea', 'north korea', 'france', 'germany',
            'telangana', 'andhra', 'karnataka', 'kerala', 'maharashtra', 'gujarat',
            'rajasthan', 'punjab', 'haryana', 'uttar pradesh', 'bihar', 'odisha'
        ]
        org_keywords = [
            'government', 'ministry', 'police', 'court', 'parliament', 'congress',
            'company', 'corporation', 'bank', 'university', 'hospital', 'agency',
            'military', 'army', 'navy', 'air force', 'united nations', 'nato', 'bcci',
            'ipl', 'csk', 'rcb', 'mi', 'kkr', 'srh', 'dc', 'pbks', 'gt', 'lsg'
        ]
        for loc in location_keywords:
            if loc in text_lower and loc not in entities['locations']:
                entities['locations'].append(loc)
        for org in org_keywords:
            if org in text_lower and org not in entities['organizations']:
                entities['organizations'].append(org)
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 2:
                if i > 0 and words[i-1].lower() not in ['the', 'a', 'an']:
                    clean = re.sub(r'[^a-zA-Z]', '', word)
                    if clean and len(clean) > 2 and clean not in entities['people']:
                        entities['people'].append(clean)
        entities['locations'] = entities['locations'][:8]
        entities['organizations'] = entities['organizations'][:8]
        entities['people'] = entities['people'][:5]
        return entities
