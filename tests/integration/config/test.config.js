const config = {
  baseUrl: process.env.BASE_URL || 'http://localhost:8080',
  apiUrl: process.env.API_URL || 'http://localhost:8080',
  cesiumUrl: process.env.CESIUM_URL || 'http://localhost:8081',
  syntheticAdsbUrl: process.env.SYNTHETIC_ADSB_URL || 'http://localhost:5001',
  adsb2ddUrl: process.env.ADSB2DD_URL || 'http://localhost:49155',
  
  timeouts: {
    default: 10000,
    navigation: 30000,
    apiResponse: 15000,
    mapLoad: 45000
  },
  
  retries: {
    default: 3,
    flaky: 5
  },
  
  viewport: {
    width: 1280,
    height: 720
  },
  
  testData: {
    aircraft: {
      icao: 'TEST001',
      callsign: 'TEST123',
      lat: 37.7749,
      lon: -122.4194,
      altitude: 35000
    }
  }
};

module.exports = config;