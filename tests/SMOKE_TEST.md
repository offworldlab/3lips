# 3lips Smoke Test

Quick verification that 3lips is working after changes.

## Quick Start

### 1. Start Services
```bash
cd tests
docker compose -f docker-compose.smoke.yml up -d
```

### 2. Run Test with Claude Code
```
claude: Load the file tests/smoke-test.js and run the smokeTest function using Puppeteer MCP
```

### 3. Check Results
- ✅ **All checks pass** = 3lips is working
- ❌ **Any check fails** = something broke

## What It Tests

1. **Page loads** at http://localhost:8080
2. **Title** contains "3lips"
3. **Form** element exists
4. **API button** (#buttonApi) exists  
5. **Map button** (#buttonMap) exists
6. **Screenshot** captured for visual check

## Manual Alternative

If Claude Code isn't available:

```bash
# Start services
cd tests
docker compose -f docker-compose.smoke.yml up -d

# Check manually
curl http://localhost:8080  # Should return HTML
open http://localhost:8080  # Should show 3lips page
```

## Expected Output

```
🚀 Running 3lips smoke test...
📍 Testing: http://localhost:8080
🌐 Check 1: Page loads
✅ Page loads
🏷️ Check 2: Correct title
✅ Correct title
📋 Check 3: Form exists
✅ Form exists
▶️ Check 4: API button exists
✅ API button exists
🗺️ Check 5: Map button exists
✅ Map button exists
📸 Check 6: Take screenshot
✅ Screenshot captured

📊 Smoke Test Results:
✅ Passed: 6
❌ Failed: 0
🎯 Overall: PASS
🎉 3lips is working correctly!
```

## When to Use

- **After any code changes**
- **Before committing**
- **When debugging issues**
- **Before deploying**

## Cleanup

```bash
cd tests
docker compose -f docker-compose.smoke.yml down
```

## Files

- `smoke-test.js` - Main test script
- `docker-compose.smoke.yml` - Minimal service setup
- `SMOKE_TEST.md` - This documentation