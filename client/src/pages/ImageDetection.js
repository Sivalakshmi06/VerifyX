import React, { useState, useRef } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import './Detection.css';

const ImageDetection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview]           = useState(null);
  const [fileType, setFileType]         = useState(null);
  const [result, setResult]             = useState(null);
  const [loading, setLoading]           = useState(false);
  const [dragOver, setDragOver]         = useState(false);
  const inputRef = useRef();

  const handleFile = (file) => {
    if (!file) return;
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setFileType(file.type.startsWith('video') ? 'video' : 'image');
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) { toast.error('Please select an image first'); return; }
    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedFile);
    try {
      const res = await axios.post('/api/detect/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data.data);
      toast.success('Analysis complete');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const isDeepfake = result?.isDeepfake;
  const confPct = result
    ? Math.round(result.confidence > 1 ? result.confidence : result.confidence * 100)
    : 0;
  const details  = result?.analysisDetails || result?.analysis_details;
  const dfType   = details?.deepfake_type || null;

  // Threshold: confidence > 70% → Likely Deepfake
  const likelyFake = isDeepfake && confPct >= 70;

  const badge = !result ? null
    : likelyFake
    ? { icon: '🔴', label: 'Likely Deepfake',    bg: '#fff5f5', border: '#fc8181', color: '#e53e3e' }
    : isDeepfake
    ? { icon: '🟡', label: 'Needs Review',        bg: '#fffff0', border: '#f6e05e', color: '#744210' }
    : confPct >= 70
    ? { icon: '🟢', label: 'Verified Authentic',  bg: '#f0fff4', border: '#68d391', color: '#276749' }
    : { icon: '🟡', label: 'Likely Real',          bg: '#f0fff4', border: '#9ae6b4', color: '#276749' };

  const typeMap = {
    'Face Swap':    { icon: '🔄', color: '#e53e3e', bg: '#fff5f5' },
    'GAN Generated':{ icon: '🤖', color: '#805ad5', bg: '#faf5ff' },
    'Lip Sync Fake':{ icon: '🎙️', color: '#dd6b20', bg: '#fffaf0' },
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🎬 Deepfake Detection</h1>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          Upload an image or video — the heatmap will reveal the truth.
        </p>

        {/* Drop zone */}
        <div
          className="upload-area"
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current.click()}
          style={{
            borderColor: dragOver ? '#667eea' : undefined,
            background:  dragOver ? '#ebf4ff' : undefined
          }}
        >
          <input
            ref={inputRef} type="file" accept="image/*,video/*"
            onChange={(e) => handleFile(e.target.files[0])}
            style={{ display: 'none' }}
          />
          <p style={{ fontSize: '48px', margin: 0 }}>📤</p>
          <p style={{ fontSize: '18px', color: '#4a5568' }}>
            {dragOver ? 'Drop it here' : 'Click or drag & drop image / video'}
          </p>
          <p style={{ fontSize: '13px', color: '#a0aec0' }}>JPG, PNG, MP4, AVI, MOV — max 50MB</p>
        </div>

        {/* Preview */}
        {preview && (
          <div className="image-preview" style={{ marginTop: '16px' }}>
            <h3>Selected {fileType === 'video' ? 'Video' : 'Image'}:</h3>
            {fileType === 'video'
              ? <video src={preview} controls style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '8px' }} />
              : <img src={preview} alt="Preview" />}
          </div>
        )}

        {selectedFile && (
          <button
            onClick={handleAnalyze} className="btn btn-primary"
            disabled={loading} style={{ marginTop: '20px' }}
          >
            {loading ? '⏳ Analyzing...' : '🔍 Analyze Media'}
          </button>
        )}

        {/* ── RESULTS ── */}
        {result && (
          <div
            className={`result-card ${isDeepfake ? 'result-fake' : 'result-real'}`}
            style={{ marginTop: '24px' }}
          >

            {/* Heatmap — front and center */}
            {result.heatmapUrl && (
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '16px', color: '#2d3748', marginBottom: '10px' }}>
                  🌡️ Analysis Heatmap
                </h3>
                <div className="image-preview">
                  <img src={result.heatmapUrl} alt="Analysis Heatmap" />
                </div>

                {/* Colour key */}
                <div style={{
                  marginTop: '12px', padding: '14px 16px',
                  background: '#f7fafc', borderRadius: '10px',
                  border: '1px solid #e2e8f0', fontSize: '13px', color: '#4a5568'
                }}>
                  {isDeepfake ? (
                    <div style={{ lineHeight: '1.9' }}>
                      <div>🔴 <strong>Red / warm regions</strong> — face areas the model flagged as manipulated (high Grad-CAM activation)</div>
                      <div>🔵 <strong>Blue / cool regions</strong> — natural areas with no manipulation signal</div>
                      <div>🟦 <strong>Bounding box</strong> — detected face region analyzed by the model</div>
                      <div>💡 Concentrated red on face = strong deepfake signal</div>
                    </div>
                  ) : (
                    <div style={{ lineHeight: '1.9' }}>
                      <div>💜 <strong>Cool tones throughout</strong> — low activation, consistent with a real photo</div>
                      <div>🟩 <strong>Green bounding box</strong> — detected face region, no manipulation found</div>
                      <div>💡 No concentrated warm patches = no deepfake signal detected</div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Single trust badge */}
            {badge && (
              <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                <div style={{
                  display: 'inline-flex', alignItems: 'center', gap: '10px',
                  padding: '12px 28px', borderRadius: '40px',
                  background: badge.bg, border: `2px solid ${badge.border}`,
                  fontSize: '17px', fontWeight: 800, color: badge.color,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                }}>
                  {badge.icon} {badge.label}
                </div>
              </div>
            )}

            {/* Deepfake type — only when fake */}
            {isDeepfake && dfType && (() => {
              const t = typeMap[dfType] || { icon: '⚠️', color: '#e53e3e', bg: '#fff5f5' };
              return (
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: '8px',
                    padding: '8px 20px', borderRadius: '20px',
                    background: t.bg, border: `1.5px solid ${t.color}`,
                    fontSize: '14px', fontWeight: 600, color: t.color
                  }}>
                    {t.icon} Detected Type: {dfType}
                  </div>
                </div>
              );
            })()}

            {/* Confidence bar */}
            <div style={{ padding: '0 4px' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between',
                fontSize: '13px', color: '#718096', marginBottom: '6px'
              }}>
                <span>🎯 Confidence</span>
                <strong style={{ color: '#667eea' }}>{confPct}%</strong>
              </div>
              <div style={{ height: '10px', background: '#e2e8f0', borderRadius: '5px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%', width: confPct + '%',
                  background: isDeepfake
                    ? 'linear-gradient(90deg, #f6ad55, #e53e3e)'
                    : 'linear-gradient(90deg, #667eea, #68d391)',
                  borderRadius: '5px', transition: 'width 1.2s ease'
                }} />
              </div>
              <div style={{ textAlign: 'center', fontSize: '12px', color: '#a0aec0', marginTop: '4px' }}>
                {confPct >= 85 ? '🔥 Very confident'
                  : confPct >= 70 ? '✅ Confident'
                  : confPct >= 55 ? '🤔 Moderate — borderline image'
                  : '😅 Low confidence — ambiguous image'}
              </div>
            </div>

            {result.framesAnalyzed && (
              <div style={{ fontSize: '13px', color: '#718096', textAlign: 'center', marginTop: '12px' }}>
                Video frames analyzed: {result.framesAnalyzed}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageDetection;
