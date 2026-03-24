# 🚀 Quick Start: News Verification

## System Status

✅ **All Services Running**
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- AI Model: http://localhost:5001

## What's New

### New Feature: News Verification & Analysis
Verify news against 20+ official news sources worldwide!

## How to Access

1. **Login** to http://localhost:3000
2. **Click** "News Verification" in the navigation menu
3. **Choose** one of 4 tabs:
   - 🔐 **Verify News** - Check credibility against official sources
   - 🔍 **Find Related News** - Search for similar articles
   - 📈 **Trending Topics** - See what's trending
   - 📰 **All Sources** - Browse latest news

## Quick Examples

### Example 1: Verify a News Article

**Input:**
```
Text: "India launches new satellite for weather forecasting"
```

**Output:**
```
✅ Credibility Score: 85%
Found 12 matching articles from:
- Times of India
- BBC News
- Reuters
- NDTV
- AP News
```

### Example 2: Find Related News

**Input:**
```
URL: https://timesofindia.indiatimes.com/...
```

**Output:**
```
🔗 Related Articles: 15 found
- 92% match: "India's new weather satellite operational"
- 88% match: "ISRO launches advanced satellite"
- 85% match: "Weather forecasting technology upgrade"
```

### Example 3: Check Trending Topics

**Output:**
```
📈 Trending Now:
- India: 45 mentions
- Technology: 38 mentions
- Weather: 32 mentions
- Satellite: 28 mentions
```

## Features

### ✅ Verify Against Official Sources
- Searches 20+ trusted news outlets
- Calculates credibility score
- Shows matching articles
- Detects entities (locations, organizations)

### 🔍 Find Related News
- Keyword-based similarity matching
- Similarity scores (0-100%)
- Multiple source coverage
- Direct links to articles

### 📈 Trending Analysis
- Real-time trending topics
- Keyword frequency tracking
- Updated hourly

### 📰 Browse All Sources
- Latest news from each source
- Organized by outlet
- Quick article previews

## Supported News Sources (20+)

**India:**
- Times of India
- NDTV
- Dina Thanthi
- Deccan Herald
- The Hindu
- India Today
- Hindustan Times
- The Telegraph
- Scroll.in
- Quint

**International:**
- BBC News
- Reuters
- AP News
- CNN
- The Guardian
- DW News
- France24
- Al Jazeera
- NPR
- The New York Times

## Performance

- **First Request**: ~5-10 seconds (fetches from all sources)
- **Cached Requests**: <1 second (uses 1-hour cache)
- **Parallel Fetching**: All sources fetched simultaneously
- **Optimization**: Image resizing, keyword extraction, TF-IDF similarity

## Credibility Scores

| Score | Status | Meaning |
|-------|--------|---------|
| 80%+ | ✅ Highly Credible | Multiple trusted sources |
| 50-79% | ⚠️ Moderate | Some trusted sources |
| <50% | ❌ Low Credibility | Not in trusted sources |

## Tips

1. **Use complete news text** for better matching
2. **Include URLs** when available
3. **Check multiple sources** for verification
4. **Review entities** to ensure accuracy
5. **Read full articles** to verify details

## Troubleshooting

### "No matching articles found"
- Try different keywords
- Check if URL is accessible
- Ensure text is in English or Tamil

### "Slow performance"
- First request fetches from all sources (normal)
- Subsequent requests use cache (fast)
- Cache refreshes every hour

### "Incorrect matches"
- Algorithm is keyword-based
- Always verify by reading full articles
- Check if keywords match your intent

## Next Steps

1. ✅ Login to the application
2. ✅ Navigate to "News Verification"
3. ✅ Try verifying a news article
4. ✅ Search for related news
5. ✅ Check trending topics

## System Architecture

```
Your Browser (localhost:3000)
        ↓
Backend API (localhost:5000)
        ↓
AI Model (localhost:5001)
        ├── News Aggregator
        ├── News Matcher
        └── URL Verifier
        ↓
20+ Official News Sources (RSS Feeds)
```

## Database

All analyses are saved to MongoDB:
- Verification results
- Search history
- User interactions
- Credibility scores

## Support

For issues or questions:
1. Check the full guide: `NEWS_VERIFICATION_GUIDE.md`
2. Review error messages in browser console
3. Check backend logs for API errors
4. Verify all services are running

---

**Ready to verify news?** 🚀

Go to http://localhost:3000 and click "News Verification"!
