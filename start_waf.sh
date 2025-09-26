#!/bin/bash

echo "🔥 Starting Quick WAF Prototype..."

# Start ML service
echo "Starting WAF ML Service..."
cd ml-service
python app.py &
WAF_PID=$!

# Wait for service to start
echo "Waiting for WAF service to initialize..."
sleep 5

# Check if service is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ WAF service is running!"
else
    echo "❌ WAF service failed to start"
    exit 1
fi

echo "🎯 WAF is ready for testing!"
echo "📊 Health check: http://localhost:8000/health"
echo "🔍 API endpoint: http://localhost:8000/analyze"
echo ""
echo "Run 'python demo/test_attacks.py' to test the WAF"
echo "Press Ctrl+C to stop the WAF service"

# Keep running
wait $WAF_PID