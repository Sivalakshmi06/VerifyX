import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import './Detection.css';

const EmotionAnalysis = () => {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extractedText, setExtractedText] = useState('');

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!text.trim() && !image) {
      toast.error('Please enter text or upload a screenshot to analyze');
      return;
    }

    setLoading(true);
    try {
      let response;
      
      if (image && text.trim()) {
        // If both image and text are provided, use image + text analysis
        const formData = new FormData();
        formData.append('image', image);
        formData.append('additionalText', text);
        console.log('Uploading image with text for emotion analysis...');
        response = await axios.post('/api/detect/emotion-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        // Store extracted text
        if (response.data.data.extracted_text) {
          setExtractedText(response.data.data.extracted_text);
        }
      } else if (image) {
        // If only image is uploaded, try OCR + emotion analysis
        const formData = new FormData();
        formData.append('image', image);
        console.log('Uploading image for OCR and emotion analysis...');
        response = await axios.post('/api/detect/emotion-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        // Store extracted text
        if (response.data.data.extracted_text) {
          setExtractedText(response.data.data.extracted_text);
        }
      } else {
        // Text-only analysis
        console.log('Analyzing text...');
        response = await axios.post('/api/detect/emotion', { text });
      }
      
      setResult(response.data.data);
      toast.success('Analysis complete!');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.response?.data?.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>😡 Emotional Manipulation Analysis</h1>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          Analyze text or message screenshots for emotional manipulation, scams, and phishing attempts.
        </p>

        <div className="form-group">
          <label>📸 Upload Screenshot (Optional - Text extraction requires Tesseract OCR setup)</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            style={{
              padding: '10px',
              border: '2px dashed #cbd5e0',
              borderRadius: '8px',
              width: '100%',
              cursor: 'pointer'
            }}
          />
          <p style={{ fontSize: '12px', color: '#718096', marginTop: '8px' }}>
            💡 Tip: For best results, paste the message text directly in the text field below instead of uploading an image.
          </p>
          {imagePreview && (
            <div style={{ marginTop: '15px', textAlign: 'center' }}>
              <img 
                src={imagePreview} 
                alt="Preview" 
                style={{ 
                  maxWidth: '100%', 
                  maxHeight: '300px', 
                  borderRadius: '8px',
                  border: '2px solid #e2e8f0'
                }} 
              />
              <button
                onClick={() => {
                  setImage(null);
                  setImagePreview(null);
                  setExtractedText('');
                }}
                style={{
                  marginTop: '10px',
                  padding: '8px 16px',
                  background: '#f56565',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Remove Image
              </button>
            </div>
          )}
        </div>

        <div className="form-group">
          <label>📝 Enter Text to Analyze (Recommended)</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste message text here for analysis. This is the most reliable way to analyze emotional manipulation and scams."
            rows="8"
          />
        </div>

        <button 
          onClick={handleAnalyze} 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Analyzing...' : '🔍 Analyze Emotions'}
        </button>

        {result && (
          <div className="result-card result-real">
            <h2>🎯 Emotional Analysis Results</h2>
            
            {/* Extracted Text from Image */}
            {extractedText && (
              <div className="result-item" style={{ 
                background: '#f0f9ff',
                padding: '15px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #bae6fd'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#0c4a6e' }}>
                  📝 Text Extracted from Image
                </h3>
                <p style={{ 
                  color: '#0c4a6e', 
                  fontSize: '14px',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  background: 'white',
                  padding: '10px',
                  borderRadius: '4px',
                  margin: 0
                }}>
                  {extractedText}
                </p>
              </div>
            )}
            
            {/* Scam Detection Alert */}
            {result.is_scam && (
              <div className="result-item" style={{ 
                background: '#fee',
                padding: '20px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '3px solid #f56565'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#c53030', fontSize: '24px' }}>
                  🚨 SCAM ALERT!
                </h3>
                <p style={{ 
                  fontSize: '18px', 
                  fontWeight: 'bold', 
                  color: '#c53030',
                  margin: '10px 0'
                }}>
                  {result.scam_type}
                </p>
                <p style={{ color: '#742a2a', fontSize: '15px', lineHeight: '1.6', margin: '10px 0' }}>
                  Confidence: {result.scam_confidence}%
                </p>
                {result.scam_indicators && result.scam_indicators.length > 0 && (
                  <div style={{ marginTop: '15px' }}>
                    <strong style={{ color: '#c53030' }}>Warning Signs Detected:</strong>
                    <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                      {result.scam_indicators.map((indicator, idx) => (
                        <li key={idx} style={{ color: '#742a2a', marginTop: '5px' }}>
                          {indicator}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Manipulation Type */}
            <div className="result-item" style={{ 
              background: result.manipulation_score > 60 ? '#fee' : result.manipulation_score > 30 ? '#fef3cd' : '#e8f5e9',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <h3 style={{ margin: '0 0 10px 0', color: '#1a202c' }}>
                ⚠️ Manipulation Type
              </h3>
              <p style={{ 
                fontSize: '20px', 
                fontWeight: 'bold', 
                color: result.manipulation_score > 60 ? '#c53030' : result.manipulation_score > 30 ? '#d69e2e' : '#38a169',
                margin: 0
              }}>
                {result.manipulation_type}
              </p>
            </div>

            {/* Confidence Score */}
            <div className="result-item" style={{ marginBottom: '20px' }}>
              <strong>🎯 Confidence:</strong>
              <span style={{ 
                fontSize: '18px', 
                fontWeight: 'bold', 
                color: '#667eea',
                marginLeft: '10px'
              }}>
                {result.confidence}%
              </span>
              <div className="progress-bar" style={{ marginTop: '10px' }}>
                <div 
                  style={{ 
                    width: `${result.confidence}%`,
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    height: '8px',
                    borderRadius: '4px',
                    transition: 'width 0.5s ease'
                  }}
                />
              </div>
            </div>

            {/* Manipulation Score */}
            <div className="manipulation-score" style={{ marginBottom: '20px' }}>
              <h3>📊 Overall Manipulation Score</h3>
              <p style={{ fontSize: '28px', fontWeight: 'bold', color: '#d68910', margin: '10px 0' }}>
                {result.manipulation_score}%
              </p>
              <div className="progress-bar">
                <div 
                  style={{ 
                    width: `${result.manipulation_score}%`,
                    background: result.manipulation_score > 60 ? '#e53e3e' : result.manipulation_score > 30 ? '#d69e2e' : '#48bb78',
                    height: '12px',
                    borderRadius: '6px',
                    transition: 'width 0.5s ease'
                  }}
                />
              </div>
              <p style={{ fontSize: '14px', color: '#718096', marginTop: '8px' }}>
                {result.manipulation_score > 60 
                  ? '🚨 High manipulation detected - be very cautious!' 
                  : result.manipulation_score > 30 
                  ? '⚠️ Moderate manipulation detected - verify information' 
                  : '✅ Low manipulation detected - appears relatively neutral'}
              </p>
            </div>

            {/* Triggering Words */}
            {result.triggering_words && result.triggering_words.length > 0 && (
              <div className="result-item" style={{ marginBottom: '20px' }}>
                <h3 style={{ color: '#1a202c', marginBottom: '10px' }}>🔍 Triggering Words</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {result.triggering_words.map((word, index) => (
                    <span 
                      key={index}
                      style={{
                        background: '#fed7d7',
                        color: '#c53030',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        fontSize: '14px',
                        fontWeight: '500',
                        border: '1px solid #fc8181'
                      }}
                    >
                      {word}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Explanation */}
            <div className="result-item" style={{ 
              background: '#f7fafc',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px',
              border: '1px solid #e2e8f0'
            }}>
              <h3 style={{ color: '#1a202c', marginBottom: '10px' }}>💡 Explanation</h3>
              <p style={{ 
                color: '#4a5568', 
                lineHeight: '1.6',
                margin: 0,
                fontSize: '15px'
              }}>
                {result.explanation}
              </p>
            </div>

            {/* Dominant Emotion */}
            <div className="result-item" style={{ marginBottom: '20px' }}>
              <strong>🎭 Dominant Emotion:</strong>
              <span style={{ 
                marginLeft: '10px',
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#667eea'
              }}>
                {result.dominant_emotion} ({result.dominant_emotion_score}%)
              </span>
            </div>

            {/* Manipulation Techniques */}
            {result.manipulation_techniques && result.manipulation_techniques.length > 0 && (
              <div className="result-item" style={{ marginBottom: '20px' }}>
                <h3 style={{ color: '#1a202c', marginBottom: '10px' }}>🎯 Manipulation Techniques Detected</h3>
                <ul style={{ 
                  listStyle: 'none', 
                  padding: 0,
                  margin: 0
                }}>
                  {result.manipulation_techniques.map((technique, index) => (
                    <li 
                      key={index}
                      style={{
                        background: '#fff5f5',
                        padding: '10px 15px',
                        marginBottom: '8px',
                        borderRadius: '6px',
                        borderLeft: '4px solid #fc8181',
                        color: '#742a2a'
                      }}
                    >
                      • {technique.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sentiment Analysis */}
            {result.sentiment && (
              <div className="result-item" style={{ 
                marginTop: '20px',
                background: '#edf2f7',
                padding: '15px',
                borderRadius: '8px'
              }}>
                <h3 style={{ color: '#1a202c', marginBottom: '10px' }}>� Sentiment Analysis</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                  <div>
                    <p style={{ margin: '0 0 5px 0', color: '#718096', fontSize: '14px' }}>Label</p>
                    <p style={{ margin: 0, fontWeight: 'bold', color: '#2d3748' }}>{result.sentiment.label}</p>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 5px 0', color: '#718096', fontSize: '14px' }}>Polarity</p>
                    <p style={{ margin: 0, fontWeight: 'bold', color: '#2d3748' }}>{result.sentiment.polarity}</p>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 5px 0', color: '#718096', fontSize: '14px' }}>Subjectivity</p>
                    <p style={{ margin: 0, fontWeight: 'bold', color: '#2d3748' }}>{result.sentiment.subjectivity}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EmotionAnalysis;
