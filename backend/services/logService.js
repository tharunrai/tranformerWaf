const fs = require('fs');
const path = require('path');

const logsFile = path.join(__dirname, '../data/logs.json');
const detectionsFile = path.join(__dirname, '../data/detections.json');

// Ensure files exist
if (!fs.existsSync(logsFile)) fs.writeFileSync(logsFile, '[]');
if (!fs.existsSync(detectionsFile)) fs.writeFileSync(detectionsFile, '[]');

async function addDetection(detection) {
  try {
    const detections = JSON.parse(fs.readFileSync(detectionsFile));
    detections.unshift(detection); // Add to front
    if (detections.length > 10) detections.pop(); // Keep last 10
    fs.writeFileSync(detectionsFile, JSON.stringify(detections, null, 2));
  } catch (error) {
    console.error('Error adding detection:', error);
  }
}

async function getDetections() {
  try {
    return JSON.parse(fs.readFileSync(detectionsFile));
  } catch (error) {
    console.error('Error getting detections:', error);
    return [];
  }
}

async function addLog(log) {
  try {
    const logs = JSON.parse(fs.readFileSync(logsFile));
    logs.push({ ...log, timestamp: new Date() }); // Include timestamp for training
    fs.writeFileSync(logsFile, JSON.stringify(logs, null, 2));
  } catch (error) {
    console.error('Error adding log:', error);
  }
}

async function getLogs() {
  try {
    return JSON.parse(fs.readFileSync(logsFile));
  } catch (error) {
    console.error('Error getting logs:', error);
    return [];
  }
}

module.exports = { addDetection, getDetections, addLog, getLogs };