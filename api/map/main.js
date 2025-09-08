var config = window.APP_CONFIG;

// fix tile server URL prefix - only add if not already present
for (var key in config['map']['tile_server']) {
  if (config['map']['tile_server'].hasOwnProperty(key)) {
      var value = config['map']['tile_server'][key];
      // Only add prefix if the URL doesn't already have one
      if (!value.startsWith('http://') && !value.startsWith('https://')) {
        var prefix = is_localhost(value) ? 'http://' : 'https://';
        config['map']['tile_server'][key] = prefix + value;
      }
  }
}

// default camera view
var centerLatitude = config['map']['location']['latitude'];
var centerLongitude = config['map']['location']['longitude'];
var metersPerDegreeLongitude = 111320 * Math.cos(centerLatitude * Math.PI / 180);
var metersPerDegreeLatitude = 111132.954 - 559.822 * Math.cos(
  2 * centerLongitude * Math.PI / 180) + 1.175 * 
  Math.cos(4 * centerLongitude * Math.PI / 180);
var widthDegrees = config['map']['center_width'] / metersPerDegreeLongitude;
var heightDegrees = config['map']['center_height'] / metersPerDegreeLatitude;
var west = centerLongitude - widthDegrees / 2;
var south = centerLatitude - heightDegrees / 2;
var east = centerLongitude + widthDegrees / 2;
var north = centerLatitude + heightDegrees / 2;
var extent = Cesium.Rectangle.fromDegrees(west, south, east, north);
Cesium.Camera.DEFAULT_VIEW_RECTANGLE = extent;
Cesium.Camera.DEFAULT_VIEW_FACTOR = 0;

var imageryProviders = [];

imageryProviders.push(new Cesium.ProviderViewModel({
	name: "ESRI",
	iconUrl: './icon/esri.jpg',
	tooltip: 'ESRI Tiles',
	creationFunction: function() {
		return new Cesium.UrlTemplateImageryProvider({
			url: config['map']['tile_server']['esri'] + '{z}/{y}/{x}',
      credit: 'Esri, Maxar, Earthstar Geographics, USDA FSA, USGS, Aerogrid, IGN, IGP, and the GIS User Community',
			maximumLevel: 20,
		});
	}
}));

imageryProviders.push(new Cesium.ProviderViewModel({
	name: "MapBox Streets v11",
	iconUrl: './icon/mapBoxStreets.png',
	tooltip: 'MapBox Streets v11 Tiles',
	creationFunction: function() {
		return new Cesium.UrlTemplateImageryProvider({
			url: config['map']['tile_server']['mapbox_streets'],
      credit: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
			maximumLevel: 16,
		});
	}
}));

imageryProviders.push(new Cesium.ProviderViewModel({
	name: "MapBox Dark v10",
	iconUrl: './icon/mapBoxDark.png',
	tooltip: 'MapBox Dark v10 Tiles',
	creationFunction: function() {
		return new Cesium.UrlTemplateImageryProvider({
			url: config['map']['tile_server']['mapbox_dark'],
      credit: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
			maximumLevel: 16,
		});
	}
}));

imageryProviders.push(new Cesium.ProviderViewModel({
	name: "OpenTopoMap",
	iconUrl: './icon/opentopomap.png',
	tooltip: 'OpenTopoMap Tiles',
	creationFunction: function() {
		return new Cesium.UrlTemplateImageryProvider({
			url: config['map']['tile_server']['opentopomap'],
      credit: '<code>Kartendaten: © <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>-Mitwirkende, SRTM | Kartendarstellung: © <a href="http://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)</code>',
			maximumLevel: 8,
		});
	}
}));

// Satellite imagery providers
imageryProviders.push(new Cesium.ProviderViewModel({
	name: "ESRI World Imagery",
	iconUrl: './icon/esri.jpg',
	tooltip: 'ESRI World Imagery (Satellite)',
	creationFunction: function() {
		return new Cesium.UrlTemplateImageryProvider({
			url: config['map']['tile_server']['esri_satellite'],
      credit: 'Source: Esri, Maxar, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community',
			maximumLevel: 19,
		});
	}
}));

imageryProviders.push(new Cesium.ProviderViewModel({
	name: "Google Satellite",
	iconUrl: './icon/esri.jpg',
	tooltip: 'Google Satellite Imagery',
	creationFunction: function() {
		return new Cesium.UrlTemplateImageryProvider({
			url: config['map']['tile_server']['google_satellite'],
      credit: '© Google',
			maximumLevel: 20,
		});
	}
}));

var terrainProviders = [];

terrainProviders.push(new Cesium.ProviderViewModel({
	name: "WGS84 Ellipsoid",
	iconUrl: './icon/opentopomap.png',
	tooltip: 'WGS84 Ellipsoid Terrain',
	creationFunction: function() {
		return new Cesium.EllipsoidTerrainProvider({
		});
	}
}));

// Use Cesium World Terrain instead of problematic terrain.datr.dev
terrainProviders.push(new Cesium.ProviderViewModel({
	name: "Cesium World Terrain",
	iconUrl: './icon/opentopomap.png',
	tooltip: 'Cesium World Terrain (Free)',
	creationFunction: function() {
		return Cesium.createWorldTerrainAsync();
	}
}));

var viewer = new Cesium.Viewer("cesiumContainer", {
	baseLayerPicker: true,
	imageryProviderViewModels: imageryProviders,
	terrainProviderViewModels: terrainProviders,
	geocoder: false,
	shouldAnimate: true,
  animation: false,
  timeline: false,
	selectionIndicator: false
});

// keep data attribution, remove CesiumIon logo
var cesiumCredit = document.querySelector('.cesium-credit-logoContainer');
if (cesiumCredit) {
    cesiumCredit.style.display = 'none';
}

/**
 * @brief Adds a point to Cesium viewer with specified parameters.
 * @param {number} latitude - The latitude of the point in degrees.
 * @param {number} longitude - The longitude of the point in degrees.
 * @param {number} altitude - The altitude of the point in meters.
 * @param {string} pointName - The name of the point.
 * @param {string} pointColor - The color of the point in CSS color string format.
 * @param {number} timestamp - The timestamp in UNIX milliseconds indicating when the point was added.
 * @returns {Entity} The Cesium Entity representing the added point.
 */
 function addPoint(latitude, longitude, altitude, pointName, pointColor, pointSize, type, timestamp) {
  // Convert latitude, longitude, altitude to Cartesian coordinates
  const position = Cesium.Cartesian3.fromDegrees(longitude, latitude, altitude);

  // Create a point entity
  const pointEntity = viewer.entities.add({
      name: pointName,
      position,
      point: {
          color: Cesium.Color.fromCssColorString(pointColor),
          pixelSize: pointSize,
          heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      label: (type === "radar") ? {
          text: pointName,
          showBackground: true,
          backgroundColor: Cesium.Color.BLACK,
          font: '14px sans-serif',
          pixelOffset: new Cesium.Cartesian2(0, -20),
      } : undefined,
      properties: {
          timestamp,
          type,
      },
  });

  return pointEntity;
}

function is_localhost(url) {
  // Handle direct localhost string
  if (url === 'localhost') {
    return true;
  }

  // Remove protocol and port to extract hostname
  let hostname = url.replace(/^https?:\/\//, "");
  hostname = hostname.split(':')[0];
  hostname = hostname.split('/')[0]; // Remove path if present
  
  // Check if hostname is localhost
  if (hostname === 'localhost') {
    return true;
  }
  
  // Check if hostname is an IP address before trying to parse it
  const ipRegex = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
  if (!ipRegex.test(hostname)) {
    return false; // If it's not an IP, assume it's not localhost
  }
  
  const localRanges = ['127.0.0.1', '192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12'];

  const ipToInt = ip => ip.split('.').reduce((acc, octet) => (acc << 8) + +octet, 0) >>> 0;

  return localRanges.some(range => {
    const [rangeStart, rangeSize = 32] = range.split('/');
    const start = ipToInt(rangeStart);
    const end = (start | (1 << (32 - +rangeSize))) >>> 0;
    return ipToInt(hostname) >= start && ipToInt(hostname) <= end;
  });

}

// global vars
var adsb_url;
var adsbEntities = {};

var style_adsb = {};
style_adsb.color = 'rgba(255, 0, 0, 0.5)';
style_adsb.pointSize = 8;
style_adsb.type = "adsb";

window.addEventListener('load', function () {

  // add radar points
  const radar_names = new URLSearchParams(
    window.location.search).getAll('server');
  // Convert container hostnames to localhost for browser access
  var radar_config_url = radar_names.map(url => {
    // Handle full URLs with protocol
    if (url.startsWith('http')) {
      // Replace container hostnames with localhost mappings
      url = url.replace('synthetic-radar1:5000', 'localhost:49158')
               .replace('synthetic-radar2:5000', 'localhost:49159')
               .replace('synthetic-radar3:5000', 'localhost:49160')
               .replace('synthetic-adsb-test:5001', 'localhost:5001')
               .replace('synthetic-adsb:49158', 'localhost:49158')
               .replace('synthetic-adsb:49159', 'localhost:49159')
               .replace('synthetic-adsb:49160', 'localhost:49160');
      return `${url}/api/config`;
    } else {
      // Handle hostname only
      url = url.replace('synthetic-radar1:5000', 'localhost:49158')
               .replace('synthetic-radar2:5000', 'localhost:49159')
               .replace('synthetic-radar3:5000', 'localhost:49160')
               .replace('synthetic-adsb-test:5001', 'localhost:5001')
               .replace('synthetic-adsb:49158', 'localhost:49158')
               .replace('synthetic-adsb:49159', 'localhost:49159')
               .replace('synthetic-adsb:49160', 'localhost:49160');
      return `http://${url}/api/config`;
    }
  });
  radar_config_url = radar_config_url.map(function(url) {
    console.log('Processing radar URL:', url, 'is_localhost:', is_localhost(url));
    if (!is_localhost(url)) {
      console.log('Converting to HTTPS:', url);
      return url.replace(/^http:/, 'https:');
    }
    console.log('Keeping as HTTP:', url);
    return url;
  });
  var style_radar = {};
  style_radar.color = 'rgba(0, 0, 0, 1.0)';
  style_radar.pointSize = 10;
  style_radar.type = "radar";
  style_radar.timestamp = Date.now();
  console.log('DEBUG: radar_config_url array:', radar_config_url);
  radar_config_url.forEach(url => {
    console.log('DEBUG: Processing radar config URL:', url);
    // Skip config requests for synthetic radar servers that don't have config endpoints
    if (url.includes('49158') || url.includes('49159') || url.includes('49160')) {
      console.log('Skipping config request for synthetic radar:', url);
      return;
    }
    
    fetch(url)
      .then(response => {
        if (!response.ok) {
          if (response.status === 404) {
            console.log('Config endpoint not available (expected):', url);
            return null;
          }
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Skip if no data (404 response)
        if (!data) return;
        
        // add radar rx and tx
        if (!doesEntityNameExist(data.location.rx.name)) {
          addPoint(
            data.location.rx.latitude, 
            data.location.rx.longitude, 
            data.location.rx.altitude, 
            data.location.rx.name, 
            style_radar.color, 
            style_radar.pointSize, 
            style_radar.type, 
            style_radar.timestamp
          );
        }
        if (!doesEntityNameExist(data.location.tx.name)) {
          addPoint(
            data.location.tx.latitude, 
            data.location.tx.longitude, 
            data.location.tx.altitude, 
            data.location.tx.name, 
            style_radar.color, 
            style_radar.pointSize, 
            style_radar.type, 
            style_radar.timestamp
          );
        }
      })
      .catch(error => {
        console.error('Error during fetch:', error);
      });
  });

  // get truth URL
  adsb_url = new URLSearchParams(
    window.location.search).get('adsb').split('&');
  adsb_url = adsb_url.map(function(url) {
    // Replace container hostnames with localhost mappings for browser access
    url = url.replace('synthetic-adsb-test:5001', 'localhost:5001')
             .replace('synthetic-adsb:5001', 'localhost:5001')
             .replace('synthetic-radar1:5000', 'localhost:49158') 
             .replace('synthetic-radar2:5000', 'localhost:49159');
    const fullUrl = url.startsWith('http') ? `${url}/data/aircraft.json` : `http://${url}/data/aircraft.json`;
    console.log('Processing ADSB URL:', fullUrl, 'is_localhost:', is_localhost(fullUrl));
    if (!is_localhost(fullUrl)) {
      console.log('Converting to HTTPS:', fullUrl);
      return fullUrl.replace(/^http:/, 'https:');
    }
    console.log('Keeping as HTTP:', fullUrl);
    return fullUrl;
  });
  adsb_url = adsb_url[0];

  // call event loops
  event_adsb();
  event_radar();
  event_ellipsoid();
  event_tracks();

})

function removeEntitiesOlderThan(entityType, maxAgeSeconds) {

  var entities = viewer.entities.values;
  for (var i = entities.length - 1; i >= 0; i--) {
    var entity = entities[i];
    const type = entity.properties["type"].getValue();
    const timestamp = entity.properties["timestamp"].getValue();
    if (entity.properties && entity.properties["type"] && 
      entity.properties["type"].getValue() === entityType &&
      Date.now()-timestamp > maxAgeSeconds*1000) {
        viewer.entities.remove(entity);
    }
  }

}

function removeEntitiesOlderThanAndFade(entityType, maxAgeSeconds, baseAlpha) {

  var entities = viewer.entities.values;
  for (var i = entities.length - 1; i >= 0; i--) {
    var entity = entities[i];
    const type = entity.properties["type"].getValue();
    const timestamp = entity.properties["timestamp"].getValue();
    if (entity.properties && entity.properties["type"] && 
      entity.properties["type"].getValue() === entityType) {
      
      if (Date.now()-timestamp > maxAgeSeconds*1000) {
        viewer.entities.remove(entity);
      }
      else {
        entity.point.color = new Cesium.Color.fromAlpha(
          entity.point.color.getValue(), baseAlpha*(1-(Date.now()-timestamp)/(maxAgeSeconds*1000)));
      }
    }
  }
}

function removeEntitiesByType(entityType) {

  var entities = viewer.entities.values;
  for (var i = entities.length - 1; i >= 0; i--) {
    var entity = entities[i];
    if (entity.properties && entity.properties["type"] && 
      entity.properties["type"].getValue() === entityType) {
        viewer.entities.remove(entity);
    }
  }
}

function doesEntityNameExist(name) {
  for (const entity of viewer.entities.values) {
    if (entity.name === name) {
      return true;
    }
  }
  return false;
}