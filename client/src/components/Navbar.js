import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/dashboard" className="nav-logo">
          🛡️ Fake News Detector
        </Link>
        
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
          </li>
          <li className="nav-item">
            <Link to="/text-detection" className="nav-link">News Detection</Link>
          </li>
          <li className="nav-item">
            <Link to="/news-verification" className="nav-link">News Verification</Link>
          </li>
          <li className="nav-item">
            <Link to="/emotion-analysis" className="nav-link">Emotional Manipulation</Link>
          </li>
          <li className="nav-item">
            <Link to="/deepfake-detection" className="nav-link">Deepfake Detection</Link>
          </li>
          {user?.role === 'admin' && (
            <li className="nav-item">
              <Link to="/admin" className="nav-link">Admin Panel</Link>
            </li>
          )}
        </ul>
        
        <div className="nav-user">
          <span className="user-name">👤 {user?.name}</span>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
