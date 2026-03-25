import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [analyticsRes, historyRes] = await Promise.all([
        axios.get('/api/dashboard/analytics'),
        axios.get('/api/dashboard/history?limit=5')
      ]);
      
      setAnalytics(analyticsRes.data.data);
      setHistory(historyRes.data.data.analyses || []);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      toast.error(error.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (analysisId) => {
    try {
      const response = await axios.get(`/api/dashboard/report/${analysisId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis-${analysisId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Report downloaded!');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <div className="card">
        <h1>📊 Dashboard</h1>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          Welcome back, {user?.name}! Here's your analysis overview.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div style={{ background: 'linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)', padding: '20px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 4px 15px rgba(255, 107, 53, 0.3)' }}>
            <h3 style={{ color: '#ffffff', margin: '0 0 10px 0' }}>Total Analyses</h3>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ffffff', margin: '0' }}>
              {analytics?.totalAnalyses || 0}
            </p>
          </div>
          
          {analytics?.analysisByType?.map((item) => (
            <div key={item._id} style={{ background: 'linear-gradient(135deg, #0d2137 0%, #1a3a52 100%)', padding: '20px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 4px 15px rgba(13, 33, 55, 0.3)' }}>
              <h3 style={{ color: '#ffffff', margin: '0 0 10px 0', textTransform: 'capitalize' }}>
                {item._id} Analysis
              </h3>
              <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff6b35', margin: '0' }}>
                {item.count}
              </p>
            </div>
          ))}
        </div>

        <h2>Recent Analysis History</h2>
        {history.length === 0 ? (
          <p style={{ color: '#718096' }}>No analysis history yet. Start analyzing content!</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f7fafc', borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Type</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Prediction</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Confidence</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Date</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item._id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '12px', textTransform: 'capitalize' }}>{item.type}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px',
                        background: item.result.prediction?.toLowerCase().includes('fake') || 
                                   item.result.prediction?.toLowerCase().includes('high') ? '#fed7d7' : '#c6f6d5',
                        color: item.result.prediction?.toLowerCase().includes('fake') || 
                               item.result.prediction?.toLowerCase().includes('high') ? '#c53030' : '#22543d'
                      }}>
                        {item.result.prediction || 'N/A'}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      {typeof item.result.confidence === 'number' 
                        ? (item.result.confidence > 1 
                          ? item.result.confidence.toFixed(1) 
                          : (item.result.confidence * 100).toFixed(1))
                        : '0.0'}%
                    </td>
                    <td style={{ padding: '12px' }}>
                      {new Date(item.createdAt).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <button 
                        onClick={() => downloadReport(item._id)}
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '14px' }}
                      >
                        📄 Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
