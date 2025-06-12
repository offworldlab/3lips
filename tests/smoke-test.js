async function smokeTest(navigate, screenshot, evaluate) {
  console.log('🚀 Running 3lips smoke test...');
  
  const results = {
    testName: '3lips Smoke Test',
    checks: [],
    passed: 0,
    failed: 0,
    timestamp: new Date().toISOString()
  };

  function addCheck(name, passed, details = '') {
    results.checks.push({ name, passed, details });
    if (passed) {
      results.passed++;
      console.log(`✅ ${name}`);
    } else {
      results.failed++;
      console.log(`❌ ${name}: ${details}`);
    }
  }

  try {
    console.log('📍 Testing: http://localhost:8080');
    
    console.log('🌐 Check 1: Page loads');
    await navigate('http://localhost:8080');
    addCheck('Page loads', true);
    
    console.log('🏷️ Check 2: Correct title');
    const title = await evaluate('document.title');
    const hasCorrectTitle = title && title.includes('3lips');
    addCheck('Correct title', hasCorrectTitle, hasCorrectTitle ? title : `Got: ${title}`);
    
    console.log('📋 Check 3: Form exists');
    const hasForm = await evaluate('document.querySelector("form") !== null');
    addCheck('Form exists', hasForm, hasForm ? 'Found' : 'Missing form element');
    
    console.log('▶️ Check 4: API button exists');
    const hasApiButton = await evaluate('document.querySelector("#buttonApi") !== null');
    addCheck('API button exists', hasApiButton, hasApiButton ? 'Found' : 'Missing #buttonApi');
    
    console.log('🗺️ Check 5: Map button exists');
    const hasMapButton = await evaluate('document.querySelector("#buttonMap") !== null');
    addCheck('Map button exists', hasMapButton, hasMapButton ? 'Found' : 'Missing #buttonMap');
    
    console.log('📸 Check 6: Take screenshot');
    await screenshot('smoke-test-result', '', 1280, 720);
    addCheck('Screenshot captured', true, 'smoke-test-result');
    
    const allPassed = results.failed === 0;
    
    console.log('\n📊 Smoke Test Results:');
    console.log(`✅ Passed: ${results.passed}`);
    console.log(`❌ Failed: ${results.failed}`);
    console.log(`🎯 Overall: ${allPassed ? 'PASS' : 'FAIL'}`);
    
    if (allPassed) {
      console.log('🎉 3lips is working correctly!');
    } else {
      console.log('⚠️ Issues detected - check failed tests above');
    }
    
    return {
      passed: allPassed,
      message: allPassed ? '3lips basic functionality verified' : `${results.failed} checks failed`,
      details: results
    };
    
  } catch (error) {
    console.error('💥 Smoke test failed with error:', error.message);
    addCheck('Test execution', false, error.message);
    
    return {
      passed: false,
      message: `Smoke test error: ${error.message}`,
      details: results
    };
  }
}

async function runSmokeTest() {
  console.log('🧪 3lips Smoke Test (Standalone Mode)');
  console.log('ℹ️ This test requires Claude Code Puppeteer MCP to run');
  console.log('ℹ️ Use: claude.ai/code with Puppeteer MCP server installed');
  console.log('\n📋 Test Checklist:');
  console.log('  1. Page loads at http://localhost:8080');
  console.log('  2. Title contains "3lips"');
  console.log('  3. Form element exists');
  console.log('  4. API button (#buttonApi) exists');
  console.log('  5. Map button (#buttonMap) exists');
  console.log('  6. Screenshot captured');
  console.log('\n⚡ To run: Load this file in Claude Code and call smokeTest()');
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { smokeTest, runSmokeTest };
} else {
  runSmokeTest();
}