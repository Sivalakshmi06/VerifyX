import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import './Detection.css';

const TextDetection = () => {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [language, setLanguage] = useState('en');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim() && !url.trim()) {
      toast.error('Please enter text or URL to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/detect/text', { text, url, language });
      const data = response.data.data;
      // sourceMatches comes as source_matches from backend
      if (data) {
        data.sourceMatches = data.source_matches || [];
      }
      setResult(data);
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error(error.response?.data?.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>📰 Fake News Detection</h1>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          Analyze news content to detect fake news. Supports English and Tamil languages.
        </p>

        <div className="form-group">
          <label>Select Language</label>
          <select 
            value={language} 
            onChange={(e) => setLanguage(e.target.value)}
            className="language-select"
          >
            <option value="en">English</option>
            <option value="ta">Tamil (தமிழ்)</option>
          </select>
        </div>

        <div className="form-group">
          <label>🔗 Enter News URL (Optional)</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/news-article"
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '16px'
            }}
          />
          <p style={{ fontSize: '13px', color: '#718096', marginTop: '5px' }}>
            Paste a news article URL to automatically fetch and analyze its content
          </p>
        </div>

        <div className="form-group">
          <label>📝 Or Enter Text to Analyze</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste news article or text here..."
            rows="8"
          />
        </div>

        <button 
          onClick={handleAnalyze} 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Analyzing...' : '🔍 Analyze Text'}
        </button>

        {result && (
          <div className={`result-card ${result.prediction === 'fake' ? 'result-fake' : 'result-real'}`}>
            <h2>Analysis Results</h2>

            {/* Main Verdict */}
            <div style={{
              textAlign: 'center',
              padding: '25px',
              marginBottom: '20px',
              borderRadius: '12px',
              background: result.prediction === 'fake'
                ? 'linear-gradient(135deg, #fed7d7, #feb2b2)'
                : 'linear-gradient(135deg, #c6f6d5, #9ae6b4)',
              border: `3px solid ${result.prediction === 'fake' ? '#f56565' : '#48bb78'}`
            }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>
                {result.prediction === 'fake' ? '❌' : '✅'}
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: result.prediction === 'fake' ? '#c53030' : '#276749' }}>
                {result.prediction === 'fake' ? 'FAKE / UNVERIFIED NEWS' : 'REAL NEWS'}
              </div>
              <div style={{ fontSize: '16px', color: '#4a5568', marginTop: '8px' }}>
                Confidence: {(result.confidence * 100).toFixed(1)}%
              </div>
              <div style={{
                width: '60%', margin: '10px auto 0', height: '8px',
                background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden'
              }}>
                <div style={{
                  width: `${result.confidence * 100}%`, height: '100%',
                  background: result.prediction === 'fake' ? '#f56565' : '#48bb78',
                  transition: 'width 0.5s ease'
                }} />
              </div>
            </div>



            {result.urlInfo && (
              <div className="result-item" style={{ 
                background: result.urlInfo.isTrusted ? '#c6f6d5' : '#fef5e7',
                padding: '15px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: `3px solid ${result.urlInfo.isTrusted ? '#48bb78' : '#ed8936'}`
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#1a202c' }}>
                  🔗 URL Source Information
                </h3>
                <div style={{ fontSize: '14px', color: '#2d3748' }}>
                  <p style={{ margin: '5px 0' }}><strong>Title:</strong> {result.urlInfo.title}</p>
                  <p style={{ margin: '5px 0' }}><strong>Domain:</strong> {result.urlInfo.domain}</p>
                  <p style={{ margin: '10px 0 5px 0' }}>
                    <strong>Source Status:</strong> 
                    <span style={{ 
                      marginLeft: '8px',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      background: result.urlInfo.isTrusted ? '#48bb78' : '#ed8936',
                      color: 'white',
                      fontSize: '13px',
                      fontWeight: 'bold',
                      display: 'inline-block'
                    }}>
                      {result.urlInfo.isTrusted ? '✓ VERIFIED TRUSTED SOURCE' : '⚠ Unverified Source'}
                    </span>
                  </p>
                  {result.urlInfo.isTrusted && (
                    <p style={{ 
                      marginTop: '10px',
                      padding: '10px',
                      background: '#e6fffa',
                      borderRadius: '6px',
                      color: '#234e52',
                      fontSize: '13px',
                      lineHeight: '1.5'
                    }}>
                      ℹ️ This content is from a verified trusted news organization with established editorial standards and fact-checking processes. Content from trusted sources is considered highly reliable.
                    </p>
                  )}
                </div>
              </div>
            )}
            
            <div className="result-item">
              <strong>Detected Language:</strong> {result.detectedLanguage}
            </div>
            
            {result.explanation && (
              <div className="result-item" style={{ 
                background: '#f7fafc', 
                padding: '15px', 
                borderRadius: '8px',
                marginTop: '15px'
              }}>
                <strong>📝 Explanation:</strong>
                <p style={{ marginTop: '8px', lineHeight: '1.6', color: '#2d3748' }}>
                  {result.explanation}
                </p>
              </div>
            )}
            
            {result.sourceReliability && (
              <div className="result-item" style={{ 
                background: '#f7fafc', 
                padding: '15px', 
                borderRadius: '8px',
                marginTop: '15px'
              }}>
                <strong>🔍 Source Reliability:</strong>
                <div style={{ marginTop: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#2d3748' }}>
                      {result.sourceReliability.level}
                    </span>
                    <span style={{ 
                      fontSize: '24px', 
                      fontWeight: 'bold',
                      color: result.sourceReliability.score >= 75 ? '#48bb78' : 
                             result.sourceReliability.score >= 50 ? '#ed8936' : '#f56565'
                    }}>
                      {result.sourceReliability.score}/100
                    </span>
                  </div>
                  <div style={{ 
                    width: '100%', 
                    height: '12px', 
                    background: '#e2e8f0', 
                    borderRadius: '6px', 
                    marginTop: '10px',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      width: `${result.sourceReliability.score}%`, 
                      height: '100%', 
                      background: result.sourceReliability.score >= 75 ? '#48bb78' : 
                                 result.sourceReliability.score >= 50 ? '#ed8936' : '#f56565',
                      transition: 'width 0.5s ease'
                    }}></div>
                  </div>
                  <p style={{ marginTop: '10px', color: '#4a5568', fontSize: '14px' }}>
                    {result.sourceReliability.description}
                  </p>
                  {result.sourceReliability.factors && result.sourceReliability.factors.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
                      <strong style={{ fontSize: '14px' }}>Factors:</strong>
                      <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
                        {result.sourceReliability.factors.map((factor, idx) => (
                          <li key={idx} style={{ fontSize: '13px', color: '#4a5568', marginTop: '3px' }}>
                            {factor}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {result.wikipediaVerification && result.wikipediaVerification.found && (
              <div className="result-item" style={{ 
                background: '#e6f3ff',
                padding: '15px',
                borderRadius: '8px',
                marginTop: '15px',
                border: '2px solid #4299e1'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#1a202c' }}>
                  📚 Wikipedia Verification
                </h3>
                <p style={{ color: '#2d3748', marginBottom: '15px' }}>
                  {result.wikipediaVerification.message}
                </p>
                {result.wikipediaVerification.articles && result.wikipediaVerification.articles.map((article, idx) => (
                  <div key={idx} style={{ 
                    background: 'white',
                    padding: '12px',
                    borderRadius: '6px',
                    marginTop: '10px',
                    border: '1px solid #bee3f8'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{ margin: '0 0 8px 0', color: '#2c5282', fontSize: '15px' }}>
                          {article.title}
                        </h4>
                        <p style={{ color: '#4a5568', fontSize: '13px', lineHeight: '1.5', margin: '0 0 8px 0' }}>
                          {article.summary}
                        </p>
                        <a 
                          href={article.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{ color: '#3182ce', fontSize: '12px', textDecoration: 'none' }}
                        >
                          Read on Wikipedia →
                        </a>
                      </div>
                      <div style={{ 
                        marginLeft: '15px',
                        padding: '6px 12px',
                        background: '#bee3f8',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: '600',
                        color: '#2c5282',
                        whiteSpace: 'nowrap'
                      }}>
                        {article.relevance}% match
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {result.suspiciousWords && result.suspiciousWords.length > 0 && (
              <div className="result-item">
                <strong>Suspicious Words Found:</strong>
                <div className="suspicious-words">
                  {result.suspiciousWords.map((word, idx) => (
                    <span key={idx} className="word-badge">{word}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TextDetection;
