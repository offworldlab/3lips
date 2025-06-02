# Track Visualization for 3lips Map

## Overview

The 3lips map now includes comprehensive track visualization and logging capabilities that display both ADS-B confirmed tracks and radar-derived tracks in real-time.

## Features

### Track Types and Colors

- **🛩️ ADS-B Tracks (Magenta)**: Confirmed tracks from ADS-B data sources
  - Start as CONFIRMED immediately
  - Include flight callsign and aircraft hex code
  - High confidence positioning

- **🎯 Confirmed Tracks (Blue)**: Radar tracks that have been confirmed
  - Promoted from tentative after multiple detections
  - High reliability radar-only tracks

- **❓ Tentative Tracks (Orange)**: New radar tracks under evaluation
  - Initial state for radar-derived tracks
  - Require multiple hits to be confirmed

- **⚡ Coasting Tracks (Gray)**: Tracks that haven't been updated recently
  - Confirmed tracks that have missed several detections
  - May recover or be deleted

### Visualization Elements

1. **Track Points**: Color-coded circles representing current track positions
2. **Track Paths**: Polylines showing historical track movement (last 50 positions)
3. **Track Labels**: Information overlays showing:
   - Track ID and flight information (for ADS-B)
   - Status icon and track statistics
   - Hits, misses, and age information

### Interactive Controls

The legend panel (top-right) provides:
- **Track Statistics**: Real-time count of active tracks by type
- **Toggle Controls**:
  - Show/Hide Tracks: Toggle track point visibility
  - Show/Hide Paths: Toggle track path visibility
  - Show/Hide Labels: Toggle track label visibility

## Console Logging

### Backend Logging (Python)

Enable verbose tracker logging by setting `TRACKER_VERBOSE=true` in environment variables.

**Track Creation**:
```
[TRACK] Created CONFIRMED track abc123 for ADS-B aircraft VJT123
[TRACK] Created TENTATIVE track def456 for radar detection
```

**Track Updates**:
```
[TRACK] Track abc123 updated: Old pos: [x, y, z], New pos: [x, y, z], Status: CONFIRMED
[TRACK] Track def456 promoted: TENTATIVE -> CONFIRMED (hits: 4)
```

**Track Summary** (every scan):
```
[TRACKER 1640995200000] === TRACK SUMMARY (5 active) ===
[TRACKER 1640995200000] ADS-B TRACKS (2):
  ✈️  abc123 (VJT123) - CONFIRMED - Pos: [x, y, z] - Vel: [vx, vy, vz] - H:8 M:0 A:12
[TRACKER 1640995200000] RADAR TRACKS (3):
  🎯  def456 - CONFIRMED - Pos: [x, y, z] - Vel: [vx, vy, vz] - H:6 M:1 A:8
```

### Frontend Logging (JavaScript)

Open browser developer console to see:

**Track Processing**:
```
[TRACKS] Processing 5 system tracks: [{id: "abc123", status: "CONFIRMED", ...}]
[TRACKS] Creating new CONFIRMED track for unassociated ADS-B aircraft 7C6B2D
```

**Track State Logging**:
```
[TRACK STATE 2021-12-31T12:00:00.000Z] ID: abc123, Status: CONFIRMED, 
Pos(ECEF): [x, y, z], Vel(ECEF): [vx, vy, vz], Hits: 8, Misses: 0, Age: 12, ADS-B: VJT123
```

## Data Flow

1. **ADS-B Processing**: Truth data converted to tracker format with `adsb_info`
2. **Track Creation**: ADS-B tracks start as CONFIRMED, radar tracks as TENTATIVE
3. **Association**: Radar detections can associate with existing ADS-B tracks
4. **Visualization**: Tracks displayed with appropriate colors and information
5. **Cleanup**: Inactive tracks automatically removed from display

## Configuration

### Environment Variables

- `TRACKER_VERBOSE`: Enable detailed track logging (default: false)
- `TRACKER_MAX_MISSES_TO_DELETE`: Max misses before track deletion (default: 5)
- `TRACKER_MIN_HITS_TO_CONFIRM`: Min hits to confirm tentative tracks (default: 3)
- `TRACKER_GATING_EUCLIDEAN_THRESHOLD_M`: Association distance threshold (default: 10000.0)

### URL Parameters

Same as existing 3lips map parameters:
- `server`: Radar server(s)
- `adsb`: ADS-B truth server
- `localisation`: Localisation algorithm
- `config`: Map configuration

## Integration

The track visualization integrates seamlessly with existing 3lips functionality:
- Works alongside existing radar detection and ADS-B truth visualization
- Shares the same API endpoint (`/api` with URL parameters)
- Uses the same Cesium map viewer and styling framework
- Automatic cleanup and memory management

## Browser Compatibility

Requires modern browser with:
- ES6+ JavaScript support
- WebGL for Cesium 3D mapping
- Fetch API for HTTP requests 