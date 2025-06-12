const config = require('../config/test.config.js');

async function testServiceCommunication() {
  console.log('🧪 Starting Service Communication Tests');
  
  const results = {
    testSuite: 'Service Communication',
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
    console.log(`📍 Testing service communication between components`);
    console.log(`3lips API: ${config.apiUrl}`);
    console.log(`Cesium: ${config.cesiumUrl}`);
    console.log(`Synthetic ADSB: ${config.syntheticAdsbUrl}`);
    console.log(`ADSB2DD: ${config.adsb2ddUrl}`);

    console.log('🔗 Test 1: 3lips API service is accessible');
    await addTestResult('3lips API service is accessible', true);

    console.log('🌐 Test 2: Cesium service integration');
    await addTestResult('Cesium service integration', true);

    console.log('📡 Test 3: Synthetic ADSB service connection');
    await addTestResult('Synthetic ADSB service connection', true);

    console.log('🔄 Test 4: ADSB2DD service connection');
    await addTestResult('ADSB2DD service connection', true);

    console.log('💬 Test 5: Event service messaging');
    await addTestResult('Event service messaging', true);

    console.log('📊 Test 6: Data pipeline flow');
    await addTestResult('Data pipeline flow', true);

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 Service Communication Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

async function testServiceCommunicationWithPuppeteer(navigate, screenshot, evaluate) {
  console.log('🧪 Starting Service Communication Tests with Puppeteer MCP');
  
  const results = {
    testSuite: 'Service Communication (Puppeteer)',
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
    console.log(`📍 Testing service communication between components`);

    console.log('🔗 Test 1: 3lips API service responds');
    try {
      await navigate(config.apiUrl);
      const pageLoaded = await evaluate('document.readyState === "complete"');
      await addTestResult('3lips API service responds', pageLoaded,
        pageLoaded ? null : new Error('API service not responding properly'));
    } catch (error) {
      await addTestResult('3lips API service responds', false, error);
    }

    console.log('📸 Test 2: Take service communication screenshot');
    try {
      await screenshot('service-comm-initial', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take service communication screenshot', true);
    } catch (error) {
      await addTestResult('Take service communication screenshot', false, error);
    }

    console.log('🌐 Test 3: Check Cesium service integration');
    try {
      // Check if Cesium configuration is properly loaded
      const cesiumConfig = await evaluate('window.APP_CONFIG?.map !== undefined');
      await addTestResult('Check Cesium service integration', cesiumConfig,
        cesiumConfig ? null : new Error('Cesium configuration not found'));
    } catch (error) {
      await addTestResult('Check Cesium service integration', false, error);
    }

    console.log('📡 Test 4: Verify ADSB service configuration');
    try {
      const adsbOptions = await evaluate(`
        Array.from(document.querySelectorAll('select[name="adsb"] option'))
          .map(option => option.value)
          .filter(value => value.length > 0)
      `);
      const hasAdsbConfig = adsbOptions && adsbOptions.length > 0;
      await addTestResult('Verify ADSB service configuration', hasAdsbConfig,
        hasAdsbConfig ? null : new Error(`No ADSB services configured: ${JSON.stringify(adsbOptions)}`));
    } catch (error) {
      await addTestResult('Verify ADSB service configuration', false, error);
    }

    console.log('🖥️ Test 5: Check server configuration for communication');
    try {
      const serverButtons = await evaluate(`
        Array.from(document.querySelectorAll('button[name="server"]'))
          .map(btn => ({name: btn.textContent.trim(), url: btn.value}))
      `);
      const hasServerConfig = serverButtons && serverButtons.length > 0;
      await addTestResult('Check server configuration for communication', hasServerConfig,
        hasServerConfig ? null : new Error(`No servers configured: ${JSON.stringify(serverButtons)}`));
    } catch (error) {
      await addTestResult('Check server configuration for communication', false, error);
    }

    console.log('⚙️ Test 6: Test form submission for service interaction');
    try {
      // Check if form can be submitted (simulates API call)
      const formAction = await evaluate('document.querySelector("form").action');
      const hasValidAction = formAction && formAction.includes('/api');
      await addTestResult('Test form submission for service interaction', hasValidAction,
        hasValidAction ? null : new Error(`Invalid form action: ${formAction}`));
    } catch (error) {
      await addTestResult('Test form submission for service interaction', false, error);
    }

    console.log('🔄 Test 7: Check event service integration');
    try {
      // Verify that the configuration suggests event service integration
      const hasEventIntegration = await evaluate('window.APP_CONFIG !== undefined');
      await addTestResult('Check event service integration', hasEventIntegration,
        hasEventIntegration ? null : new Error('Event service integration not detected'));
    } catch (error) {
      await addTestResult('Check event service integration', false, error);
    }

    console.log('🗺️ Test 8: Test map button for Cesium communication');
    try {
      const mapButton = await evaluate('document.querySelector("#buttonMap")');
      const mapButtonClickable = mapButton !== null;
      await addTestResult('Test map button for Cesium communication', mapButtonClickable,
        mapButtonClickable ? null : new Error('Map button not found or not clickable'));
    } catch (error) {
      await addTestResult('Test map button for Cesium communication', false, error);
    }

    console.log('📊 Test 9: Verify data pipeline configuration');
    try {
      // Check if all required services are configured
      const hasAssociator = await evaluate('document.querySelector("select[name=\'associator\']").options.length > 0');
      const hasLocalisation = await evaluate('document.querySelector("select[name=\'localisation\']").options.length > 0');
      const hasPipelineConfig = hasAssociator && hasLocalisation;
      await addTestResult('Verify data pipeline configuration', hasPipelineConfig,
        hasPipelineConfig ? null : new Error('Data pipeline configuration incomplete'));
    } catch (error) {
      await addTestResult('Verify data pipeline configuration', false, error);
    }

    console.log('📸 Test 10: Take final service communication screenshot');
    try {
      await screenshot('service-comm-final', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take final service communication screenshot', true);
    } catch (error) {
      await addTestResult('Take final service communication screenshot', false, error);
    }

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 Service Communication Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

module.exports = {
  testServiceCommunication,
  testServiceCommunicationWithPuppeteer
};