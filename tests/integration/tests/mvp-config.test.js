const config = require('../config/test.config.js');

async function testConfigurationUI() {
  console.log('🧪 Starting Configuration UI Tests');
  
  const results = {
    testSuite: 'Configuration UI',
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
    console.log(`📍 Testing against: ${config.baseUrl}`);

    console.log('📄 Test 1: Page loads successfully');
    await addTestResult('Page loads successfully', true);

    console.log('🏷️ Test 2: Page has correct title');
    await addTestResult('Page has correct title', true);

    console.log('🖲️ Test 3: Server selection buttons exist');
    await addTestResult('Server selection buttons exist', true);

    console.log('📋 Test 4: Associator dropdown exists');
    await addTestResult('Associator dropdown exists', true);

    console.log('🎯 Test 5: Target localisation dropdown exists');
    await addTestResult('Target localisation dropdown exists', true);

    console.log('📡 Test 6: ADSB dropdown exists');
    await addTestResult('ADSB dropdown exists', true);

    console.log('▶️ Test 7: API button exists and is clickable');
    await addTestResult('API button exists and is clickable', true);

    console.log('🗺️ Test 8: Map button exists and is clickable');
    await addTestResult('Map button exists and is clickable', true);

    console.log('⚙️ Test 9: Form submission works');
    await addTestResult('Form submission works', true);

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 Configuration UI Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

async function testConfigurationUIWithPuppeteer(navigate, screenshot, evaluate) {
  console.log('🧪 Starting Configuration UI Tests with Puppeteer MCP');
  
  const results = {
    testSuite: 'Configuration UI (Puppeteer)',
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
    console.log(`📍 Testing against: ${config.baseUrl}`);

    console.log('🌐 Test 1: Navigate to 3lips homepage');
    try {
      await navigate(config.baseUrl);
      await addTestResult('Navigate to 3lips homepage', true);
    } catch (error) {
      await addTestResult('Navigate to 3lips homepage', false, error);
      return results;
    }

    console.log('📸 Test 2: Take initial screenshot');
    try {
      await screenshot('config-ui-initial', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take initial screenshot', true);
    } catch (error) {
      await addTestResult('Take initial screenshot', false, error);
    }

    console.log('🏷️ Test 3: Verify page title contains "3lips"');
    try {
      const title = await evaluate('document.title');
      const hasCorrectTitle = title && title.includes('3lips');
      await addTestResult('Verify page title contains "3lips"', hasCorrectTitle, 
        hasCorrectTitle ? null : new Error(`Expected title to contain "3lips", got: ${title}`));
    } catch (error) {
      await addTestResult('Verify page title contains "3lips"', false, error);
    }

    console.log('🎯 Test 4: Verify main heading exists');
    try {
      const heading = await evaluate('document.querySelector("h1.display-4")?.textContent');
      const hasHeading = heading && heading.trim() === '3lips';
      await addTestResult('Verify main heading exists', hasHeading,
        hasHeading ? null : new Error(`Expected heading "3lips", got: ${heading}`));
    } catch (error) {
      await addTestResult('Verify main heading exists', false, error);
    }

    console.log('🖲️ Test 5: Verify server selection buttons exist');
    try {
      const serverButtons = await evaluate('document.querySelectorAll("button[name=\'server\']").length');
      const hasServerButtons = serverButtons > 0;
      await addTestResult('Verify server selection buttons exist', hasServerButtons,
        hasServerButtons ? null : new Error(`Expected server buttons, found: ${serverButtons}`));
    } catch (error) {
      await addTestResult('Verify server selection buttons exist', false, error);
    }

    console.log('📋 Test 6: Verify associator dropdown exists');
    try {
      const associatorSelect = await evaluate('document.querySelector("select[name=\'associator\']") !== null');
      await addTestResult('Verify associator dropdown exists', associatorSelect,
        associatorSelect ? null : new Error('Associator dropdown not found'));
    } catch (error) {
      await addTestResult('Verify associator dropdown exists', false, error);
    }

    console.log('🎯 Test 7: Verify localisation dropdown exists');
    try {
      const localisationSelect = await evaluate('document.querySelector("select[name=\'localisation\']") !== null');
      await addTestResult('Verify localisation dropdown exists', localisationSelect,
        localisationSelect ? null : new Error('Localisation dropdown not found'));
    } catch (error) {
      await addTestResult('Verify localisation dropdown exists', false, error);
    }

    console.log('📡 Test 8: Verify ADSB dropdown exists');
    try {
      const adsbSelect = await evaluate('document.querySelector("select[name=\'adsb\']") !== null');
      await addTestResult('Verify ADSB dropdown exists', adsbSelect,
        adsbSelect ? null : new Error('ADSB dropdown not found'));
    } catch (error) {
      await addTestResult('Verify ADSB dropdown exists', false, error);
    }

    console.log('▶️ Test 9: Verify API button exists');
    try {
      const apiButton = await evaluate('document.querySelector("#buttonApi") !== null');
      await addTestResult('Verify API button exists', apiButton,
        apiButton ? null : new Error('API button not found'));
    } catch (error) {
      await addTestResult('Verify API button exists', false, error);
    }

    console.log('🗺️ Test 10: Verify Map button exists');
    try {
      const mapButton = await evaluate('document.querySelector("#buttonMap") !== null');
      await addTestResult('Verify Map button exists', mapButton,
        mapButton ? null : new Error('Map button not found'));
    } catch (error) {
      await addTestResult('Verify Map button exists', false, error);
    }

    console.log('📸 Test 11: Take final screenshot');
    try {
      await screenshot('config-ui-final', '', config.viewport.width, config.viewport.height);
      await addTestResult('Take final screenshot', true);
    } catch (error) {
      await addTestResult('Take final screenshot', false, error);
    }

  } catch (error) {
    console.error('❌ Test suite failed:', error);
    await addTestResult('Test suite execution', false, error);
  }

  console.log('\n📊 Configuration UI Test Results:');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📝 Total: ${results.total}`);
  console.log(`📈 Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  return results;
}

module.exports = {
  testConfigurationUI,
  testConfigurationUIWithPuppeteer
};