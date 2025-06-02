/**
 * Track visualization and logging for the 3lips map interface
 */

var trackEntities = {};  // Store track entities by track_id
var trackPaths = {};     // Store track paths (polylines) by track_id
var trackHistory = {};   // Store track position history for path rendering

// Display toggle states
var displaySettings = {
  showTracks: true,
  showPaths: true,
  showLabels: true
};

var style_track_tentative = {
  color: 'rgba(255, 165, 0, 0.8)',  // Orange for tentative tracks
  pointSize: 12,
  type: "track_tentative"
};

var style_track_confirmed = {
  color: 'rgba(0, 128, 255, 0.9)',  // Blue for confirmed tracks
  pointSize: 14,
  type: "track_confirmed"
};

var style_track_adsb = {
  color: 'rgba(255, 0, 255, 1.0)',  // Magenta for ADS-B tracks
  pointSize: 16,
  type: "track_adsb"
};

var style_track_coasting = {
  color: 'rgba(128, 128, 128, 0.6)',  // Gray for coasting tracks
  pointSize: 10,
  type: "track_coasting"
};

// Initialize UI controls when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initializeTrackControls();
});

function initializeTrackControls() {
  const toggleTracks = document.getElementById('toggleTracks');
  const togglePaths = document.getElementById('togglePaths');
  const toggleLabels = document.getElementById('toggleLabels');

  if (toggleTracks) {
    toggleTracks.addEventListener('click', function() {
      displaySettings.showTracks = !displaySettings.showTracks;
      this.classList.toggle('active', displaySettings.showTracks);
      this.textContent = displaySettings.showTracks ? 'Show Tracks' : 'Hide Tracks';
      updateTrackVisibility();
    });
  }

  if (togglePaths) {
    togglePaths.addEventListener('click', function() {
      displaySettings.showPaths = !displaySettings.showPaths;
      this.classList.toggle('active', displaySettings.showPaths);
      this.textContent = displaySettings.showPaths ? 'Show Paths' : 'Hide Paths';
      updatePathVisibility();
    });
  }

  if (toggleLabels) {
    toggleLabels.addEventListener('click', function() {
      displaySettings.showLabels = !displaySettings.showLabels;
      this.classList.toggle('active', displaySettings.showLabels);
      this.textContent = displaySettings.showLabels ? 'Show Labels' : 'Hide Labels';
      updateLabelVisibility();
    });
  }
}

function updateTrackVisibility() {
  Object.values(trackEntities).forEach(entity => {
    if (entity && entity.point) {
      entity.point.show = displaySettings.showTracks;
    }
  });
}

function updatePathVisibility() {
  Object.values(trackPaths).forEach(entity => {
    if (entity && entity.polyline) {
      entity.polyline.show = displaySettings.showPaths;
    }
  });
}

function updateLabelVisibility() {
  Object.values(trackEntities).forEach(entity => {
    if (entity && entity.label) {
      entity.label.show = displaySettings.showLabels;
    }
  });
}

function updateLegendStats(tracks) {
  const adsbTracks = tracks.filter(t => t.adsb_info);
  const radarTracks = tracks.filter(t => !t.adsb_info);
  
  const trackCountEl = document.getElementById('trackCount');
  const adsbCountEl = document.getElementById('adsbCount');
  const radarCountEl = document.getElementById('radarCount');
  
  if (trackCountEl) trackCountEl.textContent = tracks.length;
  if (adsbCountEl) adsbCountEl.textContent = adsbTracks.length;
  if (radarCountEl) radarCountEl.textContent = radarTracks.length;
}

function event_tracks() {
  var tracks_url = window.location.origin + '/api' + window.location.search;

  fetch(tracks_url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (!data["system_tracks"]) {
        console.log("[TRACKS] No system_tracks in API response");
        return;
      }

      const tracks = data["system_tracks"];
      console.log(`[TRACKS] Processing ${tracks.length} system tracks:`, tracks.map(t => ({
        id: t.track_id,
        status: t.status,
        hits: t.hits,
        misses: t.misses,
        hasAdsb: !!t.adsb_info,
        stateType: typeof t.current_state_vector,
        stateLength: t.current_state_vector ? t.current_state_vector.length : 'N/A',
        statePreview: t.current_state_vector ? t.current_state_vector.slice(0, 3) : 'N/A'
      })));

      // Debug: Log the first track's complete structure
      if (tracks.length > 0) {
        console.log(`[TRACKS DEBUG] First track complete structure:`, tracks[0]);
      }

      // Clean up old tracks that are no longer active
      cleanupOldTracks(tracks);

      // Process each track
      tracks.forEach(track => {
        processTrack(track);
      });

      // Update legend statistics
      updateLegendStats(tracks);

    })
    .catch(error => {
      console.error('[TRACKS] Error during fetch:', error);
    })
    .finally(() => {
      // Schedule the next fetch after a delay
      setTimeout(event_tracks, 1000);
    });
}

function processTrack(track) {
  const trackId = track.track_id;
  const status = track.status;
  const currentState = track.current_state_vector;
  
  if (!currentState || currentState.length < 3) {
    console.warn(`[TRACKS] Track ${trackId} has no valid position state:`, currentState);
    return;
  }

  // Log track state to console
  logTrackState(track);

  // Convert ECEF to LLA for visualization - with safe number conversion
  const safeFloat = (value) => {
    if (value === null || value === undefined) return 0;
    const num = typeof value === 'string' ? parseFloat(value) : Number(value);
    return isNaN(num) ? 0 : num;
  };

  const ecefPosition = {
    x: safeFloat(currentState[0]),
    y: safeFloat(currentState[1]), 
    z: safeFloat(currentState[2])
  };
  
  // Validate ECEF values
  if (ecefPosition.x === 0 && ecefPosition.y === 0 && ecefPosition.z === 0) {
    console.warn(`[TRACKS] Track ${trackId} has zero ECEF position, skipping visualization`);
    return;
  }
  
  const llaPosition = ecefToLla(ecefPosition.x, ecefPosition.y, ecefPosition.z);
  
  if (!llaPosition) {
    console.warn(`[TRACKS] Failed to convert ECEF to LLA for track ${trackId}:`, ecefPosition);
    return;
  }

  // Determine track style based on status and ADS-B info
  let style;
  let trackLabel = `Track ${trackId}`;
  
  if (track.adsb_info) {
    style = style_track_adsb;
    trackLabel = `${track.adsb_info.flight || track.adsb_info.hex} (${trackId})`;
  } else {
    switch (status) {
      case 'CONFIRMED':
        style = style_track_confirmed;
        break;
      case 'COASTING':
        style = style_track_coasting;
        break;
      case 'TENTATIVE':
      default:
        style = style_track_tentative;
        break;
    }
  }

  // Update or create track entity
  updateTrackEntity(trackId, llaPosition, trackLabel, style, track);
  
  // Update track path
  updateTrackPath(trackId, llaPosition, style);
}

function updateTrackEntity(trackId, llaPosition, label, style, track) {
  const entityName = `track_${trackId}`;
  const position = Cesium.Cartesian3.fromDegrees(
    llaPosition.longitude, 
    llaPosition.latitude, 
    llaPosition.altitude
  );

  // Remove existing entity if it exists
  if (trackEntities[trackId]) {
    viewer.entities.remove(trackEntities[trackId]);
  }

  // Create track entity with enhanced label
  const statusIcon = track.adsb_info ? '✈️' : 
    (track.status === 'CONFIRMED' ? '🎯' : 
     track.status === 'COASTING' ? '⚡' : '❓');
  
  const labelText = `${statusIcon} ${label}\nHits: ${track.hits}, Misses: ${track.misses}\nAge: ${track.age_scans}`;

  const trackEntity = viewer.entities.add({
    name: entityName,
    position: position,
    point: {
      color: Cesium.Color.fromCssColorString(style.color),
      pixelSize: style.pointSize,
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
      show: displaySettings.showTracks
    },
    label: {
      text: labelText,
      showBackground: true,
      backgroundColor: Cesium.Color.BLACK.withAlpha(0.7),
      font: '12px sans-serif',
      pixelOffset: new Cesium.Cartesian2(0, -30),
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 1,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      show: displaySettings.showLabels
    },
    properties: {
      timestamp: Date.now(),
      type: style.type,
      track_id: trackId,
      track_status: track.status,
      track_hits: track.hits,
      track_misses: track.misses,
      adsb_info: track.adsb_info
    }
  });

  trackEntities[trackId] = trackEntity;
}

function updateTrackPath(trackId, llaPosition, style) {
  // Initialize track history if not exists
  if (!trackHistory[trackId]) {
    trackHistory[trackId] = [];
  }

  // Add current position to history
  trackHistory[trackId].push({
    longitude: llaPosition.longitude,
    latitude: llaPosition.latitude,
    altitude: llaPosition.altitude,
    timestamp: Date.now()
  });

  // Limit history to last 50 points
  if (trackHistory[trackId].length > 50) {
    trackHistory[trackId].shift();
  }

  // Remove existing path entity if it exists
  if (trackPaths[trackId]) {
    viewer.entities.remove(trackPaths[trackId]);
  }

  // Create path if we have enough points
  if (trackHistory[trackId].length > 1) {
    const positions = trackHistory[trackId].map(point => 
      Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, point.altitude)
    );

    const pathEntity = viewer.entities.add({
      name: `track_path_${trackId}`,
      polyline: {
        positions: positions,
        width: 2,
        material: Cesium.Color.fromCssColorString(style.color).withAlpha(0.6),
        clampToGround: false,
        show: displaySettings.showPaths
      },
      properties: {
        timestamp: Date.now(),
        type: `${style.type}_path`,
        track_id: trackId
      }
    });

    trackPaths[trackId] = pathEntity;
  }
}

function cleanupOldTracks(activeTracks) {
  const activeTrackIds = new Set(activeTracks.map(t => t.track_id));
  
  // Remove entities for tracks that are no longer active
  Object.keys(trackEntities).forEach(trackId => {
    if (!activeTrackIds.has(trackId)) {
      console.log(`[TRACKS] Removing inactive track entity: ${trackId}`);
      if (trackEntities[trackId]) {
        viewer.entities.remove(trackEntities[trackId]);
        delete trackEntities[trackId];
      }
      if (trackPaths[trackId]) {
        viewer.entities.remove(trackPaths[trackId]);
        delete trackPaths[trackId];
      }
      delete trackHistory[trackId];
    }
  });
}

function logTrackState(track) {
  const timestamp = new Date().toISOString();
  const state = track.current_state_vector;
  
  // Debug: Log the actual structure to understand the data format
  if (state && typeof state !== 'object') {
    console.warn(`[TRACKS DEBUG] Unexpected state type for track ${track.track_id}:`, typeof state, state);
    return;
  }
  
  if (state && Array.isArray(state) && state.length > 0) {
    console.log(`[TRACKS DEBUG] Track ${track.track_id} state structure:`, {
      length: state.length,
      first_element: state[0],
      type_of_first: typeof state[0],
      full_state: state
    });
  }
  
  // Safe number conversion function
  const safeToFixed = (value, decimals = 1) => {
    if (value === null || value === undefined) return 'null';
    const num = typeof value === 'string' ? parseFloat(value) : Number(value);
    return isNaN(num) ? `${value}(NaN)` : num.toFixed(decimals);
  };
  
  let position = 'N/A';
  let velocity = 'N/A';
  
  if (state && Array.isArray(state) && state.length >= 3) {
    try {
      position = `[${safeToFixed(state[0])}, ${safeToFixed(state[1])}, ${safeToFixed(state[2])}]`;
    } catch (e) {
      console.error(`[TRACKS] Error formatting position for track ${track.track_id}:`, e, state);
      position = `ERROR: ${state.slice(0, 3)}`;
    }
    
    if (state.length >= 6) {
      try {
        velocity = `[${safeToFixed(state[3])}, ${safeToFixed(state[4])}, ${safeToFixed(state[5])}]`;
      } catch (e) {
        console.error(`[TRACKS] Error formatting velocity for track ${track.track_id}:`, e, state);
        velocity = `ERROR: ${state.slice(3, 6)}`;
      }
    }
  } else if (state) {
    console.warn(`[TRACKS] Track ${track.track_id} has invalid state vector:`, state);
    position = `INVALID: ${JSON.stringify(state)}`;
  }
  
  const adsbInfo = track.adsb_info ? 
    `ADS-B: ${track.adsb_info.flight || track.adsb_info.hex}` : 
    'Radar-only';
  
  console.log(`[TRACK STATE ${timestamp}] ID: ${track.track_id}, Status: ${track.status}, ` +
              `Pos(ECEF): ${position}, Vel(ECEF): ${velocity}, ` +
              `Hits: ${track.hits}, Misses: ${track.misses}, Age: ${track.age_scans}, ${adsbInfo}`);
}

/**
 * Convert ECEF coordinates to LLA (simplified conversion)
 * Note: This is a basic implementation. For production use, consider a more robust library.
 */
function ecefToLla(x, y, z) {
  try {
    // Use Cesium's built-in conversion
    const cartesian = new Cesium.Cartesian3(x, y, z);
    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
    
    return {
      latitude: Cesium.Math.toDegrees(cartographic.latitude),
      longitude: Cesium.Math.toDegrees(cartographic.longitude),
      altitude: cartographic.height
    };
  } catch (error) {
    console.error('[TRACKS] Error converting ECEF to LLA:', error);
    return null;
  }
}

// Export function for external use
window.event_tracks = event_tracks; 