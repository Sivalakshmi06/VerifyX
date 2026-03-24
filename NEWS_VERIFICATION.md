# News Verification System

## Overview

The system now includes real-time news verification by cross-referencing claims with trusted news sources:
- **Times of India** (English) - Reliability: 95%
- **Dina Thanthi** (Tamil) - Reliability: 90%

## Features

### 1. Automatic Source Verification
Every news text is automatically checked against recent articles from trusted sources.

### 2. Verification Statuses

#### ✅ Verified (80-100%)
- **Color**: Green
- **Meaning**: Claim is confirmed by trusted sources
- **Action**: High confidence in authenticity

#### 🟧 Partially Verified (50-79%)
- **Color**: Orange
- **Meaning**: Similar content found but not exact match
- **Action**: Moderate confidence, verify details

#### 🟨 Unverified (20-49%)
- **Color**: Yellow
- **Meaning**: Limited matching content
- **Action**: Low confidence, needs more verification

#### 🔴 Not Found (0-19%)
- **Color**: Red
- **Meaning**: No matching content in trusted sources
- **Action**: Highly suspicious, likely fake

### 3. Matching Articles Display

Shows up to 5 matching articles with:
- Source name (Times of India / Dina Thanthi)
- Article title
- Similarity percentage
- Direct link to original article
- Publication date

### 4. Verification Score

Calculated based on:
- **Similarity**: How closely the text matches trusted articles
- **Source Reliability**: Weight given to each source (95% for TOI, 90% for Dina Thanthi)
- **Number of Matches**: More matches = higher confidence

## How It Works

### Step 1: Text Analysis
```
User submits text → Extract key phrases → Identify language
```

### Step 2: Source Selection
```
English text → Check Times of India first, then Dina Thanthi
Tamil text → Check Dina Thanthi first, then Times of India
```

### Step 3: Matching
```
Compare text with recent articles → Calculate similarity → Rank matches
```

### Step 4: Scoring
```
Weight matches by similarity and source reliability → Calculate final score
```

## Technical Implementation

### News Sources Configuration

```python
trusted_sources = {
    'times_of_india': {
        'name': 'Times of India',
        'url': 'https://timesofindia.indiatimes.com',
        'language': 'en',
        'reliability': 95
    },
    'dina_thanthi': {
        'name': 'Dina Thanthi',
        'url': 'https://www.dinathanthi.com',
        'language': 'ta',
        'reliability': 90
    }
}
```

### Similarity Calculation

Uses multiple factors:
1. **Title Similarity**: SequenceMatcher algorithm (60% weight)
2. **Key Phrase Matching**: Presence of important words (40% weight)

### Caching System

- Recent news cached for 1 hour
- Reduces API calls
- Improves response time

## API Response

```json
{
  "verification": {
    "status": "Verified",
    "score": 87,
    "message": "This claim is verified by trusted news sources",
    "color": "green",
    "sources_checked": ["Times of India", "Dina Thanthi"],
    "matches": [
      {
        "source": "Times of India",
        "title": "Government announces new policy...",
        "similarity": 92.5,
        "url": "https://timesofindia.indiatimes.com/article1",
        "date": "2026-03-01",
        "reliability": 95
      }
    ],
    "timestamp": "2026-03-01T10:30:00"
  }
}
```

## UI Display

### Verification Box
- Color-coded background (green/orange/yellow/red)
- Status badge with percentage
- Clear message about verification
- List of sources checked

### Matching Articles
- Card-style display
- Source name and reliability
- Article title
- Similarity percentage badge
- Clickable link to original article

## Future Enhancements

### Phase 1 (Current)
- ✅ Times of India integration
- ✅ Dina Thanthi integration
- ✅ Similarity matching
- ✅ Verification scoring

### Phase 2 (Planned)
- [ ] RSS feed integration for real-time updates
- [ ] More Tamil news sources (The Hindu Tamil, Dinamalar)
- [ ] Regional language support (Hindi, Telugu, Malayalam)
- [ ] Historical article database

### Phase 3 (Advanced)
- [ ] Fact-checking database integration
- [ ] Social media trend analysis
- [ ] Expert verification system
- [ ] Blockchain-based verification records

## Adding New Sources

To add a new trusted source:

```python
# In ai_model/models/news_verifier.py

self.trusted_sources['new_source'] = {
    'name': 'Source Name',
    'url': 'https://source-url.com',
    'rss_feed': 'https://source-url.com/rss',
    'language': 'en',  # or 'ta'
    'reliability': 85  # 0-100 scale
}
```

## Production Implementation

### For Live RSS Feeds:

```python
import feedparser

def _fetch_rss_feed(self, rss_url):
    """Fetch and parse RSS feed"""
    feed = feedparser.parse(rss_url)
    news_items = []
    
    for entry in feed.entries[:50]:  # Latest 50 articles
        news_items.append({
            'title': entry.title,
            'url': entry.link,
            'date': entry.published,
            'content': entry.summary
        })
    
    return news_items
```

### For API Integration:

```python
def _fetch_from_api(self, api_url, api_key):
    """Fetch news from API"""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(api_url, headers=headers)
    return response.json()
```

## Testing

### Test with Verified News:
```
Text: "Government announces new education policy"
Expected: High verification score with matching articles
```

### Test with Fake News:
```
Text: "Aliens landed in Mumbai yesterday"
Expected: Low/No verification score, no matches
```

### Test with Tamil News:
```
Text: "தமிழக அரசு புதிய திட்டம் அறிவிப்பு"
Expected: Matches from Dina Thanthi
```

## Benefits

1. **Credibility**: Cross-reference with established news sources
2. **Transparency**: Show users where information comes from
3. **Education**: Teach users to verify news
4. **Speed**: Real-time verification in seconds
5. **Accuracy**: Multiple sources increase reliability

## Limitations

1. **Recent News Only**: Only checks recent articles (cached)
2. **Language Specific**: Best for English and Tamil
3. **Similarity Based**: May miss paraphrased content
4. **Source Dependent**: Limited to configured sources

## Maintenance

### Update Cache Duration:
```python
self.cache_expiry = 3600  # 1 hour (adjust as needed)
```

### Monitor Source Availability:
- Check if sources are accessible
- Update URLs if changed
- Add fallback sources

### Performance Optimization:
- Implement async requests
- Use connection pooling
- Add request rate limiting

---

**The news verification system is now live and integrated into the text detection feature!**
