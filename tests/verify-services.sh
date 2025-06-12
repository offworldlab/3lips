#!/bin/bash
# Verify 3lips services are running and accessible

echo "🔍 Verifying 3lips services..."
echo ""

# Check API service
echo "1️⃣ Checking API service (port 5000)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200"; then
    echo "✅ API service is running"
else
    echo "❌ API service is not accessible"
fi

# Check Cesium service  
echo ""
echo "2️⃣ Checking Cesium service (port 8080)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
    echo "✅ Cesium service is running"
else
    echo "❌ Cesium service is not accessible"
fi

# Check if main page loads
echo ""
echo "3️⃣ Checking main page content..."
if curl -s http://localhost:5000 | grep -q "3lips"; then
    echo "✅ Main page contains '3lips'"
else
    echo "❌ Main page doesn't contain expected content"
fi

# Check for form elements
echo ""
echo "4️⃣ Checking for form elements..."
if curl -s http://localhost:5000 | grep -q 'id="buttonApi"'; then
    echo "✅ API button found"
else
    echo "❌ API button not found"
fi

if curl -s http://localhost:5000 | grep -q 'id="buttonMap"'; then
    echo "✅ Map button found"
else
    echo "❌ Map button not found"
fi

echo ""
echo "📊 Service verification complete!"
echo ""
echo "To run full Puppeteer tests:"
echo "1. Use Claude Code with Puppeteer MCP"
echo "2. Load tests/smoke-test.js"
echo "3. Execute: await smokeTest(puppeteer_navigate, puppeteer_screenshot, puppeteer_evaluate)"