"""
URL Verification System
Fetches content from URLs and analyzes them
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class URLVerifier:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work',
            '.click', '.link', '.download', '.stream', '.racing', '.win'
        ]
        self.trusted_domains = [
            'nytimes.com',
            'bbc.com',
            'bbc.co.uk',
            'cnn.com',
            'nbcnews.com',
            'dailythanthi.com',
            'dinamalar.com',
            'dinakaran.com',
            'timesofindia.indiatimes.com',
            'indiatimes.com',
            'ndtv.com',
            'indianexpress.com'
        ]
        self.phishing_keywords = [
            'verify', 'account', 'suspended', 'confirm', 'update', 'secure',
            'banking', 'paypal', 'amazon', 'login', 'signin', 'password',
            'urgent', 'immediately', 'click here', 'prize', 'winner', 'claim'
        ]
    
    def fetch_url_content(self, url):
        """Fetch and extract text content from URL"""
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {'success': False, 'error': 'Invalid URL format'}
            
            # Fetch content with better headers
            response = requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)
            
            # Handle 403 Forbidden by returning a generic message
            if response.status_code == 403:
                return {
                    'success': True,
                    'text': f'Article from {parsed.netloc}',
                    'title': 'News Article',
                    'domain': parsed.netloc,
                    'url': url
                }
            
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Get title
            title = soup.find('title')
            title_text = title.string if title else 'No title'
            
            # Get domain
            domain = parsed.netloc
            
            return {
                'success': True,
                'text': text[:5000],
                'title': title_text,
                'domain': domain,
                'url': url
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Failed to fetch URL: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Error processing URL: {str(e)}'}
    
    def is_trusted_source(self, domain):
        """Check if domain is from trusted news sources"""
        domain_lower = domain.lower()
        for trusted in self.trusted_domains:
            if trusted in domain_lower:
                return True
        return False
