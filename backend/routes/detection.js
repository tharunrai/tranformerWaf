const express = require('express');
const router = express.Router();
const logService = require('../services/logService');

// Rule-based detection logic
function detectThreat(data) {
  const { method, path, headers, body } = data;
  let confidence = 0;
  let threats = [];

  // SQL Injection patterns
  const sqlPatterns = [/union\s+select/i, /select\s+.*\s+from/i, /['";]/];
  if (sqlPatterns.some(pattern => pattern.test(path) || pattern.test(body))) {
    threats.push('SQL Injection');
    confidence = Math.max(confidence, 0.9);
  }

  // XSS patterns
  const xssPatterns = [/<script/i, /javascript:/i, /on\w+=/i];
  if (xssPatterns.some(pattern => pattern.test(path) || pattern.test(body))) {
    threats.push('XSS');
    confidence = Math.max(confidence, 0.85);
  }

  // Path Traversal
  if (/\.\./.test(path) || /\/etc\/passwd/.test(path)) {
    threats.push('Path Traversal');
    confidence = Math.max(confidence, 0.95);
  }

  return { is_attack: confidence > 0, confidence, threats };
}

// POST /analyze - Main rule-based detection + log all requests for training
router.post('/analyze', async (req, res) => {
  const result = detectThreat(req.body);
  // Log every request (malicious or normal) for future model training
  await logService.addLog({ ...req.body, ...result });
  
  if (result.is_attack) {
    await logService.addDetection({ ...req.body, ...result, timestamp: new Date() });
    req.io.emit('detection', result); // Real-time via Socket.IO
  }
  res.json(result);
});

module.exports = router;