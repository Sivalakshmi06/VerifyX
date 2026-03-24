# 📰 News Verification & Analysis System

## Overview

The News Verification system analyzes news articles against 20+ official news sources worldwide to verify credibility, find related articles, and detect manipulation.

## Features

### 1. **Verify News Against Official Sources**
- Input: News text or URL
- Output: Credibility score, matching articles, entities detected
- Searches across 20+ trusted news sources including:
  - Times of India, BBC News, Reuters, AP News, CNN
  - The Guardian, NDTV, Dina Thanthi, Deccan Herald
  - The Hindu, India Today, Hindustan Times, The Telegraph
  - Scroll.in, Quint, DW News, France24, Al Jazeera, NPR, NYT

### 2. **Find Related News Articles**
- Search for articles related to your news
- Get similarity scores for each match
- View articles from multiple sources
- Fast parallel fetching with caching

### 3. **Trending Topics**
- See what's trending across all news sources
- Keyword-based trending analysis
- Updated hourly with cache

### 4. **Browse All News Sources**
- View latest news from all 20+ sources
- Organized by source
- Quick access to full articles

## How to Use

### Access the Feature
1. Login to the application
2. Click "News Verification" in the navigation menu
3. Choose your action from the tabs

### Verify News

**Step 1:** Enter news text or URL
```
Text: Paste the news article text
OR
URL: https://example.com/news-article
```

**Step 2:** Click "Verify Against Sources"

**Step 3:** View results:
- **Credibility Score**: 0-100% (higher = more credible)
- **Verification Status**: Verified or Unverified
- **Matching Articles**: Related articles from trusted sources
- **Entities Detected**: Locations, organizations mentioned
- **Sources Covered**: How many sources reported similar news

### Search Related News

**Step 1:** Enter news text or URL

**Step 2:** Click "Find Related News"

**Step 3:** View results:
- **Related Articles**: Sorted by similarity (0-100%)
- **Source**: Which news outlet reported it
- **Summary**: Article preview
- **Read More**: Link to full article

### View Trending Topics

**Step 1:** Click "Trending Topics" tab

**Step 2:** See trending keywords and mention counts

**Step 3:** Click on a topic to search for related news

### Browse All Sources

**Step 1:** Click "All Sources" tab

**Step 2:** View latest news from each source

**Step 3:** Click "Read more" to access full articles

## Technical Details

### Architecture

```
Frontend (React)
    ↓
Backend (Node.js/Express)
    ↓
AI Model (Flask/Python)
    ├── News Aggregator (Fetches from RSS feeds)
    ├── News Matcher (Finds similar articles)
    └── URL Verifier (Fetches URL content)
    ↓
Official News Sources (20+ RSS feeds)
```

### Performance Optimization

1. **Parallel Fetching**: Fetches from all sources simultaneously
2. **Caching**: 1-hour cache to reduce API calls
3. **Keyword Matching**: Fast TF-IDF similarity calculation
4. **Async Processing**: Non-blocking operations

### Supported News Sources

| Region | Sources |
|--------|---------|
| India | Times of India, NDTV, Dina Thanthi, Deccan Herald, The Hindu, India Today, Hindustan Times, The Telegraph, Scroll.in, Quint |
| International | BBC News, Reuters, AP News, CNN, The Guardian, DW News, France24, Al Jazeera, NPR, NYT |

## API Endpoints

### Verify News
```
POST /api/detect/news-verify
Body: { text: string, url: string }
Response: { credibility_score, matching_articles, entities_found, ... }
```

### Search Related News
```
POST /api/detect/news-search
Body: { text: string, url: string, max_results: number }
Response: { related_articles, total_found, ... }
```

### Get Trending Topics
```
GET /api/news/trending
Response: { trending_topics: [{ topic, count }, ...] }
```

### Get All News Sources
```
GET /api/news/all-sources
Response: { sources: [{ source, articles }, ...] }
```

## Credibility Score Interpretation

| Score | Status | Meaning |
|-------|--------|---------|
| 80-100% | ✅ Highly Credible | Found in multiple trusted sources |
| 50-79% | ⚠️ Moderately Credible | Found in some trusted sources |
| 0-49% | ❌ Low Credibility | Not found in trusted sources |

## Tips for Best Results

1. **Use Complete News**: Provide full article text for better matching
2. **Include URL**: URLs help fetch original content
3. **Check Multiple Sources**: More matches = higher credibility
4. **Review Entities**: Check if locations/organizations are correct
5. **Read Full Articles**: Click "Read more" to verify details

## Troubleshooting

### No Results Found
- Try with different keywords
- Check if URL is accessible
- Ensure text is in English or Tamil

### Slow Performance
- System is fetching from 20+ sources
- First request takes longer (subsequent requests use cache)
- Cache refreshes every hour

### Incorrect Matches
- Similarity algorithm is keyword-based
- May match articles with similar keywords but different topics
- Always verify by reading full articles

## Future Enhancements

- [ ] Support for more languages
- [ ] Real-time news updates
- [ ] Machine learning-based similarity
- [ ] Fact-checking integration
- [ ] Social media news tracking
- [ ] Video news verification

## Support

For issues or suggestions, contact the development team.

---

**Last Updated**: March 2026
**Version**: 1.0
