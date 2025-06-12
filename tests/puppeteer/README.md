# 3lips Puppeteer MCP Tests

Automated testing suite for 3lips MVP functionality using Claude Code's Puppeteer MCP server.

## Overview

This test suite provides comprehensive testing of the 3lips multi-static radar system through browser automation. The tests are designed to work with Claude Code's existing Puppeteer MCP infrastructure.

## Test Structure

```
tests/puppeteer/
├── config/
│   └── test.config.js          # Test configuration and URLs
├── tests/
│   ├── mvp-config.test.js      # Configuration UI tests (Priority 1)
│   ├── mvp-api.test.js         # API endpoints tests (Priority 1)
│   ├── mvp-service-comm.test.js # Service communication tests (Priority 1)
│   └── mvp-map-ui.test.js      # Map/UI tests (Priority 2)
├── docker-compose.test.yml     # Test environment setup
└── README.md                   # This file
```

## Test Suites

### Priority 1: Core MVP Functionality

#### Configuration UI Tests (`mvp-config.test.js`)
- Page loading and title verification
- Server selection button functionality
- Dropdown menu population (associator, localisation, ADSB)
- Form submission capability
- Button interaction (API, Map)

#### API Endpoints Tests (`mvp-api.test.js`)
- Root endpoint response validation
- Static file serving
- Configuration loading
- Algorithm option availability
- Form action endpoints

#### Service Communication Tests (`mvp-service-comm.test.js`)
- Inter-service connectivity
- Event service integration
- ADSB service configuration
- Data pipeline verification
- Cesium service integration

### Priority 2: Extended Functionality

#### Map UI Tests (`mvp-map-ui.test.js`)
- Cesium map initialization
- Map configuration loading
- Coordinate system setup
- Tile server configuration
- ADSB track integration

## Configuration

Tests are configured via `config/test.config.js`:

```javascript
const config = {
  baseUrl: 'http://localhost:8080',      // 3lips API
  cesiumUrl: 'http://localhost:8081',    // Cesium service
  syntheticAdsbUrl: 'http://localhost:5001',  // Test data
  adsb2ddUrl: 'http://localhost:49155',  // Data converter
  
  timeouts: {
    default: 10000,
    navigation: 30000,
    apiResponse: 15000,
    mapLoad: 45000
  }
};
```

## Running Tests with Claude Code

### Prerequisites

1. Ensure Puppeteer MCP server is installed:
   ```bash
   claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer
   ```

2. Start the test environment:
   ```bash
   cd tests
   docker compose -f docker-compose.test.yml up -d
   ```

### Executing Tests

Use Claude Code's Puppeteer MCP commands to run the tests:

#### 1. Configuration UI Tests
```javascript
// Load and execute configuration tests
const configTests = require('./tests/puppeteer/tests/mvp-config.test.js');
const results = await configTests.testConfigurationUIWithPuppeteer(
  puppeteer_navigate, 
  puppeteer_screenshot, 
  puppeteer_evaluate
);
```

#### 2. API Endpoint Tests
```javascript
// Load and execute API tests
const apiTests = require('./tests/puppeteer/tests/mvp-api.test.js');
const results = await apiTests.testAPIEndpointsWithPuppeteer(
  puppeteer_navigate, 
  puppeteer_screenshot, 
  puppeteer_evaluate
);
```

#### 3. Service Communication Tests
```javascript
// Load and execute service communication tests
const serviceTests = require('./tests/puppeteer/tests/mvp-service-comm.test.js');
const results = await serviceTests.testServiceCommunicationWithPuppeteer(
  puppeteer_navigate, 
  puppeteer_screenshot, 
  puppeteer_evaluate
);
```

#### 4. Map UI Tests
```javascript
// Load and execute map UI tests
const mapTests = require('./tests/puppeteer/tests/mvp-map-ui.test.js');
const results = await mapTests.testMapUIWithPuppeteer(
  puppeteer_navigate, 
  puppeteer_screenshot, 
  puppeteer_evaluate
);
```

### Example Claude Code Interaction

```
# Navigate to test configuration
claude: Navigate to http://localhost:8080 and take a screenshot

# Execute specific test
claude: Run the configuration UI tests using the Puppeteer MCP

# Check results
claude: Evaluate the test results and provide a summary
```

## Test Results Format

Each test suite returns structured results:

```javascript
{
  testSuite: 'Configuration UI',
  tests: [
    {
      name: 'Page loads successfully',
      passed: true,
      error: null,
      timestamp: '2024-01-01T12:00:00.000Z'
    }
  ],
  passed: 8,
  failed: 0,
  total: 8
}
```

## Screenshots

Tests automatically capture screenshots at key points:
- `config-ui-initial` - Configuration page load
- `config-ui-final` - Configuration page after tests
- `api-homepage` - API homepage
- `service-comm-initial` - Service communication state
- `map-ui-cesium` - Cesium interface
- `map-ui-final` - Final map state

Screenshots are accessible via Claude Code as `screenshot://<name>`.

## Environment Variables

Configure test environment through environment variables:

```bash
# Test URLs
export BASE_URL=http://localhost:8080
export API_URL=http://localhost:8080
export CESIUM_URL=http://localhost:8081

# Service URLs
export SYNTHETIC_ADSB_URL=http://localhost:5001
export ADSB2DD_URL=http://localhost:49155

# Test configuration
export TEST_TIMEOUT=30000
export VIEWPORT_WIDTH=1280
export VIEWPORT_HEIGHT=720
```

## Docker Test Environment

The `docker-compose.test.yml` creates an isolated test environment:

- **3lips-api-test** (port 8080) - Main API service
- **3lips-event-test** - Event processing service
- **3lips-cesium-test** (port 8081) - Cesium map service
- **synthetic-adsb-test** (port 5001) - Test data generator
- **adsb2dd-test** (port 49155) - Data converter
- **synthetic-radar1/2-test** - Mock radar services

## Troubleshooting

### Common Issues

1. **Service not responding**: Check docker containers are running
   ```bash
   docker compose -f docker-compose.test.yml ps
   ```

2. **Screenshot failures**: Ensure viewport size is set correctly
3. **Navigation timeouts**: Increase timeout values in config
4. **MCP connection issues**: Verify Puppeteer MCP server installation

### Debug Mode

Enable debug logging:
```bash
claude --mcp-debug
```

### Service Health Checks

Verify services before testing:
```bash
curl http://localhost:8080        # 3lips API
curl http://localhost:8081        # Cesium
curl http://localhost:5001        # Synthetic ADSB
curl http://localhost:49155       # ADSB2DD
```

## Benefits

- **Automated MVP verification** using existing MCP infrastructure
- **Fast development cycle** with immediate feedback
- **Integration testing** with real service dependencies
- **Regression prevention** for core functionality
- **Visual validation** through automated screenshots
- **Structured reporting** for easy result analysis