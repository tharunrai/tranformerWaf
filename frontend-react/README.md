# WAF Frontend - React

A modern React-based frontend for the WAF (Web Application Firewall) prototype dashboard.

## Features

- **Real-time Monitoring**: Live threat detection updates via WebSocket
- **Interactive Testing**: Test various attack types with one click
- **Statistics Dashboard**: View detection metrics and threat counts
- **Responsive Design**: Modern UI with clean, professional styling

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend services running (see main README)

### Installation

```bash
cd frontend-react
npm install
```

### Running the Application

```bash
npm start
```

The application will start on `http://localhost:3001` (or next available port).

### Backend Dependencies

Make sure these services are running:
- **ML Service**: `http://localhost:8000` (FastAPI)
- **Backend API**: `http://localhost:5000` (Node.js/Express)

## Features Overview

### Dashboard Components

1. **Statistics Cards**
   - Total Detections: Shows all processed requests
   - Active Threats: Shows currently detected malicious requests

2. **Test Buttons**
   - **SQL Injection**: Tests common SQL injection patterns
   - **XSS**: Tests cross-site scripting attempts
   - **Benign**: Tests normal, safe requests

3. **Detection Logs**
   - Real-time display of recent detections
   - Color-coded entries (red for attacks, green for benign)
   - Shows threat type, timestamp, and request details

### Real-time Updates

The dashboard connects to the backend via WebSocket for instant updates when new threats are detected.

## API Integration

The React app communicates with the backend through:

- **REST API**: `/detections` - Fetch detection history
- **WebSocket**: Real-time detection events
- **Proxy**: All API calls are proxied through the development server

## Development

### Available Scripts

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Create production build
- `npm run eject` - Eject from Create React App

### Project Structure

```
frontend-react/
├── public/
│   └── index.html
├── src/
│   ├── App.js          # Main application component
│   ├── App.css         # Component styles
│   ├── index.js        # Application entry point
│   └── index.css       # Global styles
└── package.json
```

## Troubleshooting

### Connection Issues

If you see proxy errors:
1. Ensure backend services are running on correct ports
2. Check that CORS is properly configured in the backend
3. Verify WebSocket connection to backend

### Port Conflicts

If port 3001 is busy, React will prompt for an alternative port.

## Production Deployment

```bash
npm run build
```

This creates an optimized production build in the `build` folder that can be served by any static web server.