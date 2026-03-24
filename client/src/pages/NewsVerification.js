import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import './Detection.css';

const NewsVerification = () => {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [language, setLanguage] = useState('en');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('verify');
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [allSources, setAllSources] = useState([]);

  useEffect(() => {
    // Fetch trending topics on mount
    fetchTrendingTopics();
  }, []);

  const fetchTrendingTopics = async () => {
    try {
      const response = await axios.get('/api/news/trending');
      if (response.data.success) {
        setTrendingTopics(response.data.trending_topics);
      }
    } catch (error) {
      console.error('Error fetching trending topics:', error);
    }
  };

  const fetchAllSources = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/news/all-sources');
      if (response.data.success) {
        setAllSources(response.data.sources);
      }
    } catch (error) {
      toast.error('Failed to fetch news from all sources');
    } finally {
      setLoading(false);
    }
  };

  const detectLanguage = (inputText) => {
    // Simple Tamil detection - check for Tamil Unicode characters
    const tamilRegex = /[\u0B80-\u0BFF]/g;
    const tamilChars = inputText.match(tamilRegex);
    
    if (tamilChars && tamilChars.length > 5) {
      return 'ta'; // Tamil detected
    }
    return 'en'; // Default to English
  };

  const handleVerify = async () => {
    if (!text.trim() && !url.trim()) {
      toast.error('Please enter text or URL to verify');
      return;
    }

    setLoading(true);
    try {
      // Auto-detect language from text if available
      let detectedLang = language;
      if (text.trim()) {
        detectedLang = detectLanguage(text);
        if (detectedLang !== language) {
          setLanguage(detectedLang);
          console.log(`[AUTO-DETECT] Detected language: ${detectedLang}`);
        }
      }

      const response = await axios.post('/api/detect/news-verify', {
        text: text.trim(),
        url: url.trim(),
        language: detectedLang
      });

      if (response.data.success) {
        setResult(response.data.data);
        toast.success('Verification complete!');
      } else {
        toast.warning('Verification completed with limited results');
        setResult(response.data.data || {});
      }
    } catch (error) {
      console.error('Verification error:', error);
      // Show partial results if available
      if (error.response?.data?.data) {
        setResult(error.response.data.data);
        toast.warning('Verification completed with some limitations');
      } else {
        toast.error(error.response?.data?.message || 'Verification failed - please try again');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearchRelated = async () => {
    if (!text.trim() && !url.trim()) {
      toast.error('Please enter text or URL to search');
      return;
    }

    setLoading(true);
    try {
      // Auto-detect language from text if available
      let detectedLang = language;
      if (text.trim()) {
        detectedLang = detectLanguage(text);
        if (detectedLang !== language) {
          setLanguage(detectedLang);
          console.log(`[AUTO-DETECT] Detected language: ${detectedLang}`);
        }
      }

      const response = await axios.post('/api/detect/news-search', {
        text: text.trim(),
        url: url.trim(),
        max_results: 15,
        language: detectedLang
      });

      if (response.data.success) {
        setResult({
          ...response.data.data,
          verification_status: 'search_results'
        });
        toast.success('Search complete!');
      } else {
        toast.warning('Search completed with limited results');
        setResult({
          ...response.data.data,
          verification_status: 'search_results'
        });
      }
    } catch (error) {
      console.error('Search error:', error);
      if (error.response?.data?.data) {
        setResult({
          ...error.response.data.data,
          verification_status: 'search_results'
        });
        toast.warning('Search completed with some limitations');
      } else {
        toast.error(error.response?.data?.message || 'Search failed - please try again');
      }
    } finally {
      setLoading(false);
    }
  };

  const getCredibilityColor = (score) => {
    if (score >= 80) return '#48bb78';
    if (score >= 50) return '#f6ad55';
    return '#f56565';
  };

  const getCredibilityLabel = (score) => {
    if (score >= 80) return '✅ Highly Credible';
    if (score >= 50) return '⚠️ Moderately Credible';
    return '❌ Low Credibility';
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🔍 News Verification & Analysis</h1>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          Verify news against 20+ official news sources worldwide. Find related articles and check credibility.
        </p>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #e2e8f0' }}>
          <button
            onClick={() => setActiveTab('verify')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'verify' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
              color: activeTab === 'verify' ? 'white' : '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              transition: 'all 0.3s'
            }}
          >
            🔐 Verify News
          </button>
          <button
            onClick={() => setActiveTab('trending')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'trending' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
              color: activeTab === 'trending' ? 'white' : '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              transition: 'all 0.3s'
            }}
          >
            📈 Trending Topics
          </button>
          <button
            onClick={() => { setActiveTab('sources'); fetchAllSources(); }}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'sources' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
              color: activeTab === 'sources' ? 'white' : '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              transition: 'all 0.3s'
            }}
          >
            📰 All Sources
          </button>
        </div>

        {/* Verify Tab */}
        {activeTab === 'verify' && (
          <>
            <div className="form-group">
              <label>🌐 Select Language (Auto-detects Tamil)</label>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '16px',
                  cursor: 'pointer'
                }}
              >
                <option value="en">English (7 sources)</option>
                <option value="ta">Tamil - தமிழ் (3 sources: Dinathanthi, Dinamalar, Dina Karan)</option>
              </select>
              <p style={{ fontSize: '12px', color: '#718096', marginTop: '5px' }}>
                {language === 'en' 
                  ? '📰 Verifying against 7 English news sources' 
                  : '📰 Verifying against 3 Tamil news sources'}
              </p>
              <p style={{ fontSize: '11px', color: '#a0aec0', marginTop: '3px', fontStyle: 'italic' }}>
                💡 Tip: Paste Tamil text and it will automatically switch to Tamil sources
              </p>
            </div>

            <div className="form-group">
              <label>📝 Enter News Text</label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste the news text you want to verify..."
                rows="6"
              />
            </div>

            <div className="form-group">
              <label>🔗 Or Enter URL</label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/news-article"
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
              <button
                onClick={handleVerify}
                className="btn btn-primary"
                disabled={loading}
                style={{ flex: 1 }}
              >
                {loading ? '⏳ Verifying...' : '🔐 Verify Against Sources'}
              </button>
              <button
                onClick={handleSearchRelated}
                className="btn btn-secondary"
                disabled={loading}
                style={{ flex: 1, background: '#4299e1' }}
              >
                {loading ? '⏳ Searching...' : '🔍 Find Related News'}
              </button>
            </div>

            {/* Results */}
            {result && (
              <div className="result-card result-real">
                <h2>📊 Verification Results</h2>

                {/* Credibility Score */}
                {result.credibility_score !== undefined && (
                  <div className="result-item" style={{ marginBottom: '20px' }}>
                    <h3 style={{ margin: '0 0 10px 0' }}>🎯 Credibility Score</h3>
                    <div style={{
                      fontSize: '36px',
                      fontWeight: 'bold',
                      color: getCredibilityColor(result.credibility_score),
                      marginBottom: '10px'
                    }}>
                      {result.credibility_score}%
                    </div>
                    <p style={{
                      fontSize: '18px',
                      fontWeight: 'bold',
                      color: getCredibilityColor(result.credibility_score),
                      margin: 0
                    }}>
                      {getCredibilityLabel(result.credibility_score)}
                    </p>
                    <div className="progress-bar" style={{ marginTop: '10px' }}>
                      <div
                        style={{
                          width: `${result.credibility_score}%`,
                          background: getCredibilityColor(result.credibility_score),
                          height: '12px',
                          borderRadius: '6px',
                          transition: 'width 0.5s ease'
                        }}
                      />
                    </div>
                  </div>
                )}

                {/* Verification Status */}
                <div className="result-item" style={{
                  background: result.verification_status === 'verified' ? '#e8f5e9' : '#fff3e0',
                  padding: '15px',
                  borderRadius: '8px',
                  marginBottom: '20px',
                  border: `2px solid ${result.verification_status === 'verified' ? '#4caf50' : '#ff9800'}`
                }}>
                  <h3 style={{ margin: '0 0 10px 0' }}>
                    {result.verification_status === 'verified' ? '✅ Verified' : '⚠️ Unverified'}
                  </h3>
                  <p style={{ margin: 0, color: '#333' }}>
                    Found {result.total_matches} matching articles from {result.sources_covered} news sources
                  </p>
                </div>

                {/* Entities Found */}
                {result.entities_found && (
                  <div className="result-item" style={{ marginBottom: '20px' }}>
                    <h3 style={{ margin: '0 0 10px 0' }}>🏷️ Entities Detected</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                      <div>
                        <p style={{ margin: '0 0 5px 0', color: '#718096', fontSize: '14px' }}>Locations</p>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                          {result.entities_found.locations && result.entities_found.locations.length > 0 ? (
                            result.entities_found.locations.map((loc, idx) => (
                              <span key={idx} style={{
                                background: '#e0f2f1',
                                color: '#00695c',
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px'
                              }}>
                                {loc}
                              </span>
                            ))
                          ) : (
                            <span style={{ color: '#999' }}>None</span>
                          )}
                        </div>
                      </div>
                      <div>
                        <p style={{ margin: '0 0 5px 0', color: '#718096', fontSize: '14px' }}>Organizations</p>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                          {result.entities_found.organizations && result.entities_found.organizations.length > 0 ? (
                            result.entities_found.organizations.map((org, idx) => (
                              <span key={idx} style={{
                                background: '#f3e5f5',
                                color: '#6a1b9a',
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px'
                              }}>
                                {org}
                              </span>
                            ))
                          ) : (
                            <span style={{ color: '#999' }}>None</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Matching Articles - same style as TextDetection "Found in Trusted Sources" */}
                {(() => {
                  const articles = result.matching_articles || result.related_articles || [];
                  const count = articles.length;
                  return count > 0 ? (
                    <div className="result-item" style={{ marginBottom: '20px' }}>
                      <strong>📰 Found in Trusted Sources ({count})</strong>
                      <div style={{ marginTop: '10px' }}>
                        {articles.map((article, idx) => (
                          <div key={idx} style={{
                            background: '#f0fff4',
                            padding: '12px',
                            marginBottom: '8px',
                            borderRadius: '8px',
                            borderLeft: '4px solid #48bb78'
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '10px' }}>
                              <div style={{ flex: 1 }}>
                                <p style={{ margin: '0 0 4px 0', fontWeight: 'bold', color: '#1a202c', fontSize: '14px' }}>
                                  {article.title}
                                </p>
                                <p style={{ margin: 0, color: '#718096', fontSize: '12px' }}>📰 {article.source}</p>
                              </div>
                              <span style={{
                                background: '#c6f6d5',
                                color: '#276749',
                                padding: '4px 10px',
                                borderRadius: '4px',
                                fontWeight: 'bold',
                                fontSize: '12px',
                                whiteSpace: 'nowrap'
                              }}>
                                {article.similarity_score}% match
                              </span>
                            </div>
                            {article.link && (
                              <a href={article.link} target="_blank" rel="noopener noreferrer"
                                style={{ color: '#38a169', fontSize: '12px', textDecoration: 'none', marginTop: '6px', display: 'inline-block' }}>
                                Read article →
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="result-item" style={{
                      background: '#fef5e7',
                      padding: '15px',
                      borderRadius: '8px',
                      marginBottom: '20px',
                      border: '2px solid #f39c12'
                    }}>
                      <p style={{ margin: 0, color: '#744210', fontSize: '14px' }}>
                        ℹ️ No matching articles found in the selected sources. This could mean the news is very recent or not widely covered yet.
                      </p>
                    </div>
                  );
                })()}
              </div>
            )}
          </>
        )}

        {/* Trending Tab */}
        {activeTab === 'trending' && (
          <div>
            <h2>📈 Trending Topics</h2>
            {trendingTopics.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px', marginTop: '20px' }}>
                {trendingTopics.map((topic, idx) => (
                  <div key={idx} style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    padding: '20px',
                    borderRadius: '8px',
                    textAlign: 'center',
                    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
                  }}>
                    <p style={{ margin: '0 0 10px 0', fontSize: '18px', fontWeight: 'bold' }}>
                      {topic.topic}
                    </p>
                    <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', opacity: 0.9 }}>
                      {topic.count} mentions
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading trending topics...</p>
            )}
          </div>
        )}

        {/* All Sources Tab */}
        {activeTab === 'sources' && (
          <div>
            <h2>📰 News from All Sources</h2>
            {loading ? (
              <p>Loading news from all sources...</p>
            ) : allSources.length > 0 ? (
              <div style={{ marginTop: '20px' }}>
                {allSources.map((sourceData, idx) => (
                  <div key={idx} style={{
                    background: '#f7fafc',
                    padding: '20px',
                    marginBottom: '20px',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <h3 style={{ margin: '0 0 15px 0', color: '#1a202c' }}>
                      📰 {sourceData.source}
                      <span style={{
                        marginLeft: '10px',
                        background: '#667eea',
                        color: 'white',
                        padding: '4px 12px',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}>
                        {sourceData.article_count} articles
                      </span>
                    </h3>
                    <div>
                      {sourceData.articles.map((article, aIdx) => (
                        <div key={aIdx} style={{
                          background: 'white',
                          padding: '12px',
                          marginBottom: '10px',
                          borderRadius: '6px',
                          borderLeft: '3px solid #667eea'
                        }}>
                          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold', color: '#1a202c' }}>
                            {article.title}
                          </p>
                          <p style={{ margin: '0 0 8px 0', color: '#718096', fontSize: '13px' }}>
                            {article.summary}
                          </p>
                          {article.link && (
                            <a href={article.link} target="_blank" rel="noopener noreferrer" style={{
                              color: '#667eea',
                              textDecoration: 'none',
                              fontSize: '12px'
                            }}>
                              Read more →
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No sources loaded. Click the "All Sources" tab to fetch news.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsVerification;
