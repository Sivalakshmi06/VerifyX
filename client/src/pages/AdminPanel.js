import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const res = await axios.get('/api/admin/users');
        setUsers(res.data.data.users);
      } else if (activeTab === 'logs') {
        const res = await axios.get('/api/admin/logs');
        setLogs(res.data.data.logs);
      } else if (activeTab === 'stats') {
        const res = await axios.get('/api/admin/stats');
        setStats(res.data.data);
      }
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const handleBlockUser = async (userId, block) => {
    try {
      await axios.post(`/api/admin/block/${userId}`, { block });
      toast.success(`User ${block ? 'blocked' : 'unblocked'} successfully`);
      fetchData();
    } catch (error) {
      toast.error('Failed to update user status');
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>👨‍💼 Admin Panel</h1>
        
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #e2e8f0' }}>
          <button 
            onClick={() => setActiveTab('users')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'users' ? 'linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)' : 'transparent',
              color: activeTab === 'users' ? 'white' : '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              transition: 'all 0.3s'
            }}
          >
            Users
          </button>
          <button 
            onClick={() => setActiveTab('logs')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'logs' ? 'linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)' : 'transparent',
              color: activeTab === 'logs' ? 'white' : '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              transition: 'all 0.3s'
            }}
          >
            Analysis Logs
          </button>
          <button 
            onClick={() => setActiveTab('stats')}
            style={{
              padding: '10px 20px',
              border: 'none',
              background: activeTab === 'stats' ? 'linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)' : 'transparent',
              color: activeTab === 'stats' ? 'white' : '#ffffff',
              fontWeight: '600',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              transition: 'all 0.3s'
            }}
          >
            Statistics
          </button>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <>
            {activeTab === 'users' && (
              <div>
                <h2>User Management</h2>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#f7fafc', borderBottom: '2px solid #e2e8f0' }}>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Email</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Role</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Status</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user._id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '12px' }}>{user.name}</td>
                        <td style={{ padding: '12px' }}>{user.email}</td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            background: user.role === 'admin' ? '#fef5e7' : '#ebf8ff',
                            color: user.role === 'admin' ? '#d68910' : '#2c5282'
                          }}>
                            {user.role}
                          </span>
                        </td>
                        <td style={{ padding: '12px' }}>
                          {user.isBlocked ? '🔴 Blocked' : '🟢 Active'}
                        </td>
                        <td style={{ padding: '12px' }}>
                          {user.role !== 'admin' && (
                            <button
                              onClick={() => handleBlockUser(user._id, !user.isBlocked)}
                              className={user.isBlocked ? 'btn btn-primary' : 'btn btn-danger'}
                              style={{ padding: '6px 12px', fontSize: '14px' }}
                            >
                              {user.isBlocked ? 'Unblock' : 'Block'}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === 'logs' && (
              <div>
                <h2>Analysis Logs</h2>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#f7fafc', borderBottom: '2px solid #e2e8f0' }}>
                      <th style={{ padding: '12px', textAlign: 'left' }}>User</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Type</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Prediction</th>
                      <th style={{ padding: '12px', textAlign: 'left' }}>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log._id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '12px' }}>{log.userId?.name || 'Unknown'}</td>
                        <td style={{ padding: '12px', textTransform: 'capitalize' }}>{log.type}</td>
                        <td style={{ padding: '12px' }}>{log.result.prediction}</td>
                        <td style={{ padding: '12px' }}>
                          {new Date(log.createdAt).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === 'stats' && stats && (
              <div>
                <h2>System Statistics</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <div style={{ background: 'linear-gradient(135deg, #0d2137 0%, #1a3a52 100%)', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 15px rgba(13, 33, 55, 0.3)' }}>
                    <h3 style={{ color: '#ffffff' }}>Total Users</h3>
                    <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff6b35' }}>
                      {stats.totalUsers}
                    </p>
                  </div>
                  <div style={{ background: 'linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%)', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 15px rgba(255, 107, 53, 0.3)' }}>
                    <h3 style={{ color: '#ffffff' }}>Blocked Users</h3>
                    <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ffffff' }}>
                      {stats.blockedUsers}
                    </p>
                  </div>
                  <div style={{ background: 'linear-gradient(135deg, #0d2137 0%, #1a3a52 100%)', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 15px rgba(13, 33, 55, 0.3)' }}>
                    <h3 style={{ color: '#ffffff' }}>Total Analyses</h3>
                    <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff6b35' }}>
                      {stats.totalAnalyses}
                    </p>
                  </div>
                </div>

                <h3>Top Fake News Topics</h3>
                <div style={{ marginTop: '20px' }}>
                  {stats.topFakeTopics.map((topic, idx) => (
                    <div key={idx} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      padding: '10px',
                      background: '#f7fafc',
                      marginBottom: '8px',
                      borderRadius: '6px'
                    }}>
                      <span style={{ fontWeight: '500' }}>{topic.word}</span>
                      <span style={{ color: '#718096' }}>{topic.count} occurrences</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
