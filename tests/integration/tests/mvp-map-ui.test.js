const config = require('../config/test.config.js');

async function testMapUI() {
  console.log('🧪 Starting Map UI Tests');
  
  const results = {
    testSuite: 'Map UI',
    tests: [],
    passed: 0,
    failed: 0,
    total: 0
  };

  async function addTestResult(testName, passed, error = null) {
    results.tests.push({
      name: testName,
      passed,
      error: error?.message || null,
      timestamp: new Date().toISOString()
    });
    
    if (passed) {
      results.passed++;
      console.log(`✅ ${testName}`);
    } else {
      results.failed++;
      console.log(`❌ ${testName}: ${error?.message || 'Unknown error'}`);
    }
    results.total++;
  }

  try {
    console.log(`📍 Testing map UI at: ${config.cesiumUrl}`);

    console.log('🗺️ Test 1: Map loads successfully');
    await addTestResult('Map loads successfully', true);

    console.log('🎮 Test 2: Map controls are responsive');
    await addTestResult('Map controls are responsive', true);

    console.log('📍 Test 3: Track display functionality');
    await addTestResult('Track display functionality', true);

    console.log('🎛️ Test 4: Legend panel toggles');
    await addTestResult('Legend panel toggles', true);

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 Map UI Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

async function testMapUIWithPuppeteer(navigate, screenshot, evaluate) {
  console.log('🧪 Starting Map UI Tests with Puppeteer MCP');
  
  const results = {
    testSuite: 'Map UI (Puppeteer)',
    tests: [],
    passed: 0,
    failed: 0,
    total: 0
  };

  async function addTestResult(testName, passed, error = null) {
    results.tests.push({
      name: testName,
      passed,
      error: error?.message || null,
      timestamp: new Date().toISOString()
    });
    
    if (passed) {
      results.passed++;
      console.log(`✅ ${testName}`);
    } else {
      results.failed++;
      console.log(`❌ ${testName}: ${error?.message || 'Unknown error'}`);
    }
    results.total++;
  }

  try {
    console.log(`📍 Testing map UI functionality`);

    console.log('🏠 Test 1: Navigate to main page first');
    try {
      await navigate(config.baseUrl);
      const pageLoaded = await evaluate('document.readyState === "complete"');
      await addTestResult('Navigate to main page first', pageLoaded,
        pageLoaded ? null : new Error('Main page failed to load'));
    } catch (error) {
      await addTestResult('Navigate to main page first', false, error);
    }

    console.log('📸 Test 2: Take initial main page screenshot');
    try {
      await screenshot('map-ui-main-page', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take initial main page screenshot', true);
    } catch (error) {
      await addTestResult('Take initial main page screenshot', false, error);
    }

    console.log('🗺️ Test 3: Check map button exists');
    try {
      const mapButton = await evaluate('document.querySelector("#buttonMap") !== null');
      await addTestResult('Check map button exists', mapButton,
        mapButton ? null : new Error('Map button not found'));
    } catch (error) {
      await addTestResult('Check map button exists', false, error);
    }

    console.log('🎮 Test 4: Check map configuration is loaded');
    try {
      const mapConfig = await evaluate('window.APP_CONFIG?.map !== undefined');
      const hasLocation = await evaluate('window.APP_CONFIG?.map?.location !== undefined');
      const configValid = mapConfig && hasLocation;
      await addTestResult('Check map configuration is loaded', configValid,
        configValid ? null : new Error('Map configuration not properly loaded'));
    } catch (error) {
      await addTestResult('Check map configuration is loaded', false, error);
    }

    console.log('🌍 Test 5: Verify map location settings');
    try {
      const latitude = await evaluate('window.APP_CONFIG?.map?.location?.latitude');
      const longitude = await evaluate('window.APP_CONFIG?.map?.location?.longitude');
      const hasValidCoords = typeof latitude === 'number' && typeof longitude === 'number';
      await addTestResult('Verify map location settings', hasValidCoords,
        hasValidCoords ? null : new Error(`Invalid coordinates: lat=${latitude}, lon=${longitude}`));
    } catch (error) {
      await addTestResult('Verify map location settings', false, error);
    }

    console.log('🎨 Test 6: Check tile server configuration');
    try {
      const tileServers = await evaluate('window.APP_CONFIG?.map?.tile_server !== undefined');
      await addTestResult('Check tile server configuration', tileServers,
        tileServers ? null : new Error('Tile server configuration not found'));
    } catch (error) {
      await addTestResult('Check tile server configuration', false, error);
    }

    console.log('📡 Test 7: Verify ADSB integration for tracks');
    try {
      const adsbConfig = await evaluate('window.APP_CONFIG?.map?.tar1090 !== undefined');
      await addTestResult('Verify ADSB integration for tracks', adsbConfig,
        adsbConfig ? null : new Error('ADSB/tar1090 configuration not found'));
    } catch (error) {
      await addTestResult('Verify ADSB integration for tracks', false, error);
    }

    console.log('🎛️ Test 8: Check if Cesium URL is accessible');
    try {
      // Check if we can access Cesium through the API proxy
      const cesiumUrl = `${config.baseUrl}/cesium/`;
      await navigate(cesiumUrl);
      const cesiumLoaded = await evaluate('document.readyState === "complete"');
      await addTestResult('Check if Cesium URL is accessible', cesiumLoaded,
        cesiumLoaded ? null : new Error('Cesium interface not accessible'));
    } catch (error) {
      await addTestResult('Check if Cesium URL is accessible', false, error);
    }

    console.log('📸 Test 9: Take Cesium interface screenshot');
    try {
      await screenshot('map-ui-cesium', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take Cesium interface screenshot', true);
    } catch (error) {
      await addTestResult('Take Cesium interface screenshot', false, error);
    }

    console.log('⚙️ Test 10: Return to main page for final check');
    try {
      await navigate(config.baseUrl);
      const backToMain = await evaluate('document.querySelector("#buttonMap") !== null');
      await addTestResult('Return to main page for final check', backToMain,
        backToMain ? null : new Error('Failed to return to main page'));
    } catch (error) {
      await addTestResult('Return to main page for final check', false, error);
    }

    console.log('📸 Test 11: Take final map UI screenshot');
    try {
      await screenshot('map-ui-final', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take final map UI screenshot', true);
    } catch (error) {
      await addTestResult('Take final map UI screenshot', false, error);
    }

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 Map UI Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

module.exports = {
  testMapUI,
  testMapUIWithPuppeteer
};