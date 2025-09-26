import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TrainingData from './components/TrainingData';
import MLTester from './components/MLTester';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <h1>�️ WAF Security Dashboard</h1>
          <div className="nav-links">
            <Link to="/" className="nav-link">Analytics</Link>
            <Link to="/training-data" className="nav-link">Training Data</Link>
            <Link to="/ml-tester" className="nav-link">ML Tester</Link>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/training-data" element={<TrainingData />} />
          <Route path="/ml-tester" element={<MLTester />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;