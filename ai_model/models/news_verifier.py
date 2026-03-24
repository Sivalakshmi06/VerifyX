"""
News Verification System
Cross-references claims with trusted news sources:
- Times of India (English)
- Dina Thanthi (Tamil)
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import time

class NewsVerifier:
    """
    Verify news claims against trusted sources
    """
    
    def __init__(self):
        self.trusted_sources = {
            'times_of_india': {
                'name': 'Times of India',
                'url': 'https://timesofindia.indiatimes.com',
                'rss_feeds': [
                    'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
                    'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',  # India
                    'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms'  # World
                ],
                'language': 'en',
                'reliability': 95
            },
            'dina_thanthi': {
                'name': 'Dina Thanthi',
                'url': 'https://www.dinathanthi.com',
                'rss_feeds': [
                    'https://www.dinathanthi.com/rss/tamilnadu.xml',
                    'https://www.dinathanthi.com/rss/india.xml',
                    'https://www.dinathanthi.com/rss/world.xml'
                ],
                'language': 'ta',
                'reliability': 90
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Cache for recent news (to avoid repeated API calls)
        self.news_cache = {}
        self.cache_expiry = 3600  # 1 hour
    
    def verify_claim(self, text, language='en'):
        """
        Verify a news claim against trusted sources
        
        Args:
            text: News text to verify
            language: 'en' or 'ta'
        
        Returns:
            dict with verification results
        """
        # Extract key phrases from text
        key_phrases = self._extract_key_phrases(text)
        
        # Search in appropriate sources based on language
        if language == 'ta':
            sources_to_check = ['dina_thanthi', 'times_of_india']
        else:
            sources_to_check = ['times_of_india', 'dina_thanthi']
        
        verification_results = []
        found_matches = []
        
        for source_key in sources_to_check:
            source = self.trusted_sources[source_key]
            
            # Get recent news from source
            recent_news = self._get_recent_news_from_rss(source_key)
            
            # Search for matching articles
            matches = self._find_matches(text, key_phrases, recent_news)
            
            if matches:
                for match in matches:
                    found_matches.append({
                        'source': source['name'],
                        'title': match['title'],
                        'similarity': match['similarity'],
                        'url': match.get('url', source['url']),
                        'date': match.get('date', 'Recent'),
                        'reliability': source['reliability']
                    })
        
        # Calculate overall verification score
        verification_score = self._calculate_verification_score(found_matches)
        
        # Determine verification status
        if verification_score >= 80:
            status = "Verified"
            message = "This claim is verified by trusted news sources"
            color = "green"
        elif verification_score >= 50:
            status = "Partially Verified"
            message = "Similar content found in trusted sources, but not exact match"
            color = "orange"
        elif verification_score >= 20:
            status = "Unverified"
            message = "Limited or no matching content found in trusted sources"
            color = "yellow"
        else:
            status = "Not Found"
            message = "No matching content found in trusted sources"
            color = "red"
        
        return {
            'status': status,
            'score': verification_score,
            'message': message,
            'color': color,
            'matches': found_matches[:5],  # Top 5 matches
            'sources_checked': [self.trusted_sources[s]['name'] for s in sources_to_check],
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_recent_news_from_rss(self, source_key):
        """
        Get recent news from RSS feeds (with caching)
        """
        # Check cache
        cache_key = f"{source_key}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.news_cache:
            return self.news_cache[cache_key]
        
        source = self.trusted_sources[source_key]
        news_items = []
        
        try:
            # Fetch from all RSS feeds
            for rss_url in source['rss_feeds']:
                try:
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries[:20]:  # Get latest 20 from each feed
                        news_items.append({
                            'title': entry.get('title', ''),
                            'url': entry.get('link', source['url']),
                            'date': entry.get('published', datetime.now().strftime('%Y-%m-%d')),
                            'content': entry.get('summary', '')
                        })
                except Exception as e:
                    print(f"Error fetching RSS from {rss_url}: {str(e)}")
                    continue
            
            # Cache the results
            if news_items:
                self.news_cache[cache_key] = news_items
            
        except Exception as e:
            print(f"Error fetching news from {source['name']}: {str(e)}")
        
        return news_items
    
    def _extract_key_phrases(self, text):
        """
        Extract key phrases from text for matching
        """
        # Remove common words and extract meaningful phrases
        text_lower = text.lower()
        
        # Remove URLs, special characters
        text_clean = re.sub(r'http\S+|www\S+|https\S+', '', text_lower)
        text_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', text_clean)
        
        # Common stop words to remove
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                     'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
                     'these', 'those', 'it', 'its', 'they', 'them', 'their'}
        
        # Split into words and filter
        words = text_clean.split()
        key_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Return unique key words (top 10)
        return list(set(key_words))[:10]
    
    def _find_matches(self, text, key_phrases, news_items):
        """
        Find matching news articles
        """
        matches = []
        text_lower = text.lower()
        
        for item in news_items:
            # Calculate similarity
            title_similarity = self._calculate_similarity(text_lower, item['title'].lower())
            
            # Check for key phrase matches
            phrase_matches = sum(1 for phrase in key_phrases if phrase in item['title'].lower())
            phrase_score = (phrase_matches / max(len(key_phrases), 1)) * 100
            
            # Combined similarity score
            similarity = (title_similarity * 0.6 + phrase_score * 0.4)
            
            if similarity > 30:  # Threshold for considering a match
                matches.append({
                    'title': item['title'],
                    'url': item.get('url', ''),
                    'date': item.get('date', ''),
                    'similarity': round(similarity, 2)
                })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches
    
    def _calculate_similarity(self, text1, text2):
        """
        Calculate text similarity using SequenceMatcher
        """
        return SequenceMatcher(None, text1, text2).ratio() * 100
    
    def _calculate_verification_score(self, matches):
        """
        Calculate overall verification score based on matches
        """
        if not matches:
            return 0
        
        # Weight by similarity and source reliability
        total_score = 0
        for match in matches[:3]:  # Top 3 matches
            weighted_score = (match['similarity'] * match['reliability']) / 100
            total_score += weighted_score
        
        # Average and normalize
        avg_score = total_score / min(len(matches), 3)
        
        return min(round(avg_score), 100)
    
    def get_source_info(self):
        """
        Get information about trusted sources
        """
        return {
            'sources': [
                {
                    'name': source['name'],
                    'language': source['language'],
                    'reliability': source['reliability'],
                    'url': source['url']
                }
                for source in self.trusted_sources.values()
            ],
            'total_sources': len(self.trusted_sources)
        }
