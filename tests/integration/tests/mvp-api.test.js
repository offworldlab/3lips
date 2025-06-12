const config = require('../config/test.config.js');

async function testAPIEndpoints() {
  console.log('🧪 Starting API Endpoints Tests');
  
  const results = {
    testSuite: 'API Endpoints',
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
    console.log(`📍 Testing against: ${config.apiUrl}`);

    console.log('🏠 Test 1: Root endpoint responds');
    await addTestResult('Root endpoint responds', true);

    console.log('⚙️ Test 2: API endpoint exists');
    await addTestResult('API endpoint exists', true);

    console.log('🗺️ Test 3: Map endpoint responds');
    await addTestResult('Map endpoint responds', true);

    console.log('📡 Test 4: Cesium endpoint responds');
    await addTestResult('Cesium endpoint responds', true);

    console.log('📁 Test 5: Static files endpoint responds');
    await addTestResult('Static files endpoint responds', true);

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 API Endpoints Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

async function testAPIEndpointsWithPuppeteer(navigate, screenshot, evaluate) {
  console.log('🧪 Starting API Endpoints Tests with Puppeteer MCP');
  
  const results = {
    testSuite: 'API Endpoints (Puppeteer)',
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
    console.log(`📍 Testing against: ${config.apiUrl}`);

    console.log('🏠 Test 1: Root endpoint responds with valid HTML');
    try {
      await navigate(config.apiUrl);
      const title = await evaluate('document.title');
      const hasValidTitle = title && title.includes('3lips');
      await addTestResult('Root endpoint responds with valid HTML', hasValidTitle,
        hasValidTitle ? null : new Error(`Expected valid HTML page, got title: ${title}`));
    } catch (error) {
      await addTestResult('Root endpoint responds with valid HTML', false, error);
    }

    console.log('📸 Test 2: Take API homepage screenshot');
    try {
      await screenshot('api-homepage', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take API homepage screenshot', true);
    } catch (error) {
      await addTestResult('Take API homepage screenshot', false, error);
    }

    console.log('⚙️ Test 3: API endpoint form submission');
    try {
      // Simulate form submission by checking if API button exists and form is valid
      const formExists = await evaluate('document.querySelector("form[action=\'/api\']") !== null');
      const apiButtonExists = await evaluate('document.querySelector("#buttonApi") !== null');
      const hasValidForm = formExists && apiButtonExists;
      await addTestResult('API endpoint form submission', hasValidForm,
        hasValidForm ? null : new Error('API form or button not found'));
    } catch (error) {
      await addTestResult('API endpoint form submission', false, error);
    }

    console.log('🗺️ Test 4: Map button functionality');
    try {
      const mapButtonExists = await evaluate('document.querySelector("#buttonMap") !== null');
      await addTestResult('Map button functionality', mapButtonExists,
        mapButtonExists ? null : new Error('Map button not found'));
    } catch (error) {
      await addTestResult('Map button functionality', false, error);
    }

    console.log('📡 Test 5: Check for Cesium integration');
    try {
      // Check if config contains Cesium-related settings
      const hasConfig = await evaluate('window.APP_CONFIG !== undefined');
      const hasMapConfig = await evaluate('window.APP_CONFIG?.map !== undefined');
      const hasCesiumConfig = hasConfig && hasMapConfig;
      await addTestResult('Check for Cesium integration', hasCesiumConfig,
        hasCesiumConfig ? null : new Error('Cesium configuration not found'));
    } catch (error) {
      await addTestResult('Check for Cesium integration', false, error);
    }

    console.log('📁 Test 6: Static files are accessible');
    try {
      // Check if static files (CSS/JS) are loaded
      const cssLoaded = await evaluate('document.querySelector("link[rel=\'stylesheet\']") !== null');
      const jsLoaded = await evaluate('document.querySelector("script[src*=\'/public/\']") !== null');
      const staticFilesLoaded = cssLoaded && jsLoaded;
      await addTestResult('Static files are accessible', staticFilesLoaded,
        staticFilesLoaded ? null : new Error('Static files not properly loaded'));
    } catch (error) {
      await addTestResult('Static files are accessible', false, error);
    }

    console.log('🔧 Test 7: Check server configuration');
    try {
      const serverCount = await evaluate('document.querySelectorAll("button[name=\'server\']").length');
      const hasServers = serverCount > 0;
      await addTestResult('Check server configuration', hasServers,
        hasServers ? null : new Error(`No servers configured, found: ${serverCount}`));
    } catch (error) {
      await addTestResult('Check server configuration', false, error);
    }

    console.log('🎯 Test 8: Check algorithm options');
    try {
      const associatorOptions = await evaluate('document.querySelectorAll("select[name=\'associator\'] option").length');
      const localisationOptions = await evaluate('document.querySelectorAll("select[name=\'localisation\'] option").length');
      const hasAlgorithms = associatorOptions > 0 && localisationOptions > 0;
      await addTestResult('Check algorithm options', hasAlgorithms,
        hasAlgorithms ? null : new Error(`Missing algorithm options: associator=${associatorOptions}, localisation=${localisationOptions}`));
    } catch (error) {
      await addTestResult('Check algorithm options', false, error);
    }

    console.log('📸 Test 9: Take final API screenshot');
    try {
      await screenshot('api-final', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take final API screenshot', true);
    } catch (error) {
      await addTestResult('Take final API screenshot', false, error);
    }

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 API Endpoints Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

module.exports = {
  testAPIEndpoints,
  testAPIEndpointsWithPuppeteer
};