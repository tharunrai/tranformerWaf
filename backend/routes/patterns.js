const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

const patternsFile = path.join(__dirname, '../data/malicious_patterns.json');

// Ensure patterns file exists
if (!fs.existsSync(patternsFile)) {
  fs.writeFileSync(patternsFile, '[]');
}

// Store malicious pattern for future training
router.post('/store-pattern', async (req, res) => {
  try {
    const pattern = req.body;
    
    // Add timestamp and unique ID
    pattern.id = Date.now() + Math.random().toString(36).substr(2, 9);
    pattern.stored_at = new Date().toISOString();
    
    // Read existing patterns
    const patterns = JSON.parse(fs.readFileSync(patternsFile));
    
    // Add new pattern
    patterns.push(pattern);
    
    // Keep only last 1000 patterns (memory management)
    if (patterns.length > 1000) {
      patterns.splice(0, patterns.length - 1000);
    }
    
    // Save to file
    fs.writeFileSync(patternsFile, JSON.stringify(patterns, null, 2));
    
    console.log(`📝 Stored malicious pattern: ${pattern.pattern_signature}`);
    
    res.json({ 
      success: true, 
      message: 'Pattern stored successfully',
      pattern_id: pattern.id 
    });
    
  } catch (error) {
    console.error('Error storing pattern:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Get stored patterns for analysis
router.get('/patterns', async (req, res) => {
  try {
    const patterns = JSON.parse(fs.readFileSync(patternsFile));
    
    // Optional filtering
    const { threat_type, limit = 100 } = req.query;
    
    let filteredPatterns = patterns;
    
    if (threat_type) {
      filteredPatterns = patterns.filter(p => 
        p.threat_type && p.threat_type.toLowerCase().includes(threat_type.toLowerCase())
      );
    }
    
    // Return most recent patterns first
    filteredPatterns = filteredPatterns
      .sort((a, b) => new Date(b.stored_at) - new Date(a.stored_at))
      .slice(0, parseInt(limit));
    
    res.json({
      success: true,
      count: filteredPatterns.length,
      total_patterns: patterns.length,
      patterns: filteredPatterns
    });
    
  } catch (error) {
    console.error('Error retrieving patterns:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Export patterns for training (Firebase preparation)
router.get('/export-patterns', async (req, res) => {
  try {
    const patterns = JSON.parse(fs.readFileSync(patternsFile));
    
    // Format for ML training
    const trainingData = patterns.map(pattern => ({
      text: pattern.pattern_signature,
      label: 1, // malicious
      features: {
        method: pattern.method,
        confidence: pattern.confidence,
        threat_type: pattern.threat_type
      },
      metadata: {
        timestamp: pattern.stored_at,
        source: 'waf_detection'
      }
    }));
    
    res.json({
      success: true,
      format: 'training_ready',
      count: trainingData.length,
      data: trainingData
    });
    
  } catch (error) {
    console.error('Error exporting patterns:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Clear old patterns (maintenance)
router.delete('/patterns/cleanup', async (req, res) => {
  try {
    const { days_old = 30 } = req.query;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - parseInt(days_old));
    
    const patterns = JSON.parse(fs.readFileSync(patternsFile));
    const filteredPatterns = patterns.filter(pattern => 
      new Date(pattern.stored_at) > cutoffDate
    );
    
    fs.writeFileSync(patternsFile, JSON.stringify(filteredPatterns, null, 2));
    
    res.json({
      success: true,
      message: `Cleaned up patterns older than ${days_old} days`,
      removed: patterns.length - filteredPatterns.length,
      remaining: filteredPatterns.length
    });
    
  } catch (error) {
    console.error('Error cleaning patterns:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router;