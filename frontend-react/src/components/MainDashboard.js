import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import '../App.css';

const socket = io('http://localhost:5000');

function MainDashboard() {
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({
    totalDetections: 0,
    activeThreats: 0
  });

  useEffect(() => {
    // Listen for real-time detections
    socket.on('detection', (data) => {
      setDetections(prev => [data, ...prev]);
    });

    // Load initial detections
    loadDetections();

    // Set up periodic refresh
    const interval = setInterval(loadDetections, 2000);

    return () => {
      socket.off('detection');
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    // Update stats when detections change
    setStats({
      totalDetections: detections.length,
      activeThreats: detections.filter(d => d.is_malicious).length
    });
  }, [detections]);

  const loadDetections = async () => {
    try {
      const response = await fetch('/detections');
      const data = await response.json();
      setDetections(data);
    } catch (error) {
      console.error('Failed to load detections:', error);
    }
  };

  const testRequest = async (method, path, body = '') => {
    try {
      const response = await fetch('/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          method,
          path,
          headers: { 'User-Agent': 'Test Client' },
          body
        })
      });

      const result = await response.json();
      console.log('Detection result:', result);
    } catch (error) {
      console.error('Test request failed:', error);
    }
  };

  const testSQLInjection = () => testRequest('GET', "/login?user=admin' OR '1'='1");
  const testXSS = () => testRequest('POST', '/search', "<script>alert('xss')</script>");
  const testBenign = () => testRequest('GET', '/home');

  return (
    <div className="container">
      <div className="page-header">
        <h1>Security Overview</h1>
        <p className="page-description">Real-time monitoring and threat detection dashboard</p>
      </div>

      <div className="stats">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Total Requests</h3>
            <div className="stat-number">{stats.totalDetections}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <h3>Threats Detected</h3>
            <div className="stat-number">{stats.activeThreats}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>Blocked Attacks</h3>
            <div className="stat-number">{stats.activeThreats}</div>
          </div>
        </div>
      </div>

      <div className="logs">
        <div className="section-header">
          <h2>Recent Activity</h2>
          <div className="status-indicator">
            <span className="status-dot active"></span>
            <span>Live Monitoring</span>
          </div>
        </div>
        <div className="detection-logs">
          {detections.slice(0, 8).map((detection, index) => (
            <div
              key={index}
              className={`log-entry ${detection.is_malicious ? 'attack' : 'benign'}`}
            >
              <div className="log-header">
                <span className={`status-badge ${detection.is_malicious ? 'danger' : 'success'}`}>
                  {detection.is_malicious ? 'BLOCKED' : 'ALLOWED'}
                </span>
                <span className="timestamp">{new Date().toLocaleTimeString()}</span>
              </div>
              <div className="log-details">
                <span className="threat-type">{detection.threat_type || 'Clean Request'}</span>
                <div className="request-info">{detection.request_signature || 'N/A'}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MainDashboard;