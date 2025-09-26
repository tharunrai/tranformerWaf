const express = require('express');
const router = express.Router();
const logService = require('../services/logService');

// Simple tokenization for DistilBERT (readable format)
function tokenizeForDistilBERT(text) {
  // Basic tokenization: split by spaces, remove punctuation, lowercase
  return text.toLowerCase()
    .replace(/[^\w\s]/g, '') // Remove punctuation
    .split(/\s+/)
    .filter(token => token.length > 0);
}

// GET /detections - Retrieve recent detections
router.get('/detections', async (req, res) => {
  const detections = await logService.getDetections();
  res.json(detections);
});

// GET /logs - Retrieve all logs with tokenized format for DistilBERT
router.get('/logs', async (req, res) => {
  const logs = await logService.getLogs();
  const tokenizedLogs = logs.map(log => ({
    ...log,
    pathTokens: tokenizeForDistilBERT(log.path),
    bodyTokens: tokenizeForDistilBERT(log.body || ''),
    headerTokens: tokenizeForDistilBERT(JSON.stringify(log.headers || {}))
  }));
  res.json(tokenizedLogs);
});

module.exports = router;