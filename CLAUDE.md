# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

3lips is a multi-static radar target localization system that tracks aircraft using ellipse/ellipsoid intersections. The system integrates radar detections with ADS-B truth data for improved tracking accuracy.

## Architecture

The system consists of three main Docker services:

- **API Service** (`api/`): Flask-based REST API and web interface (port 8080 in dev)
- **Event Service** (`event/`): Core processing engine handling radar data association, localization, and tracking
- **Cesium Service** (`cesium/`): Apache server providing 3D visualization with CesiumJS

Services communicate via TCP sockets and use host networking mode for radar integration.

## Key Components

### Event Processing (`event/`)
- **Associators** (`algorithm/associator/`): Match radar detections to ADS-B aircraft
- **Localizers** (`algorithm/localisation/`): EllipseParametric, EllipsoidParametric, SphericalIntersection
- **Tracker** (`algorithm/track/`): Multi-target tracking using Stone Soup library
- **Truth Integration** (`algorithm/truth/`): ADS-B ground truth handling

### Data Flow
1. Event service polls radar nodes for detections
2. AdsbAssociator matches detections to ADS-B aircraft
3. Localization algorithms compute target positions from bistatic ranges
4. Tracker maintains persistent tracks across time steps
5. Results saved to NDJSON format and served via API

## Development Commands

```bash
# Production build and run
docker compose up -d --build

# Development mode with hot-reloading
docker compose -f docker-compose.dev.yml up

# Run post-processing analysis
docker run -it -v ./save:/app/save 3lips-script bash
PYTHONPATH=/app python plot_accuracy.py <input.ndjson> <target-id>
```

## Configuration

Environment variables are configured in `.env` file:
- **Radar**: RADAR_NAMES, RADAR_URLS for radar node endpoints
- **Map**: MAP_LATITUDE, MAP_LONGITUDE for visualization center
- **Algorithms**: ELLIPSE_N_SAMPLES, ELLIPSOID_THRESHOLD for localization parameters
- **Tracking**: Confirmation thresholds, gating parameters
- **ADS-B**: Integration settings and data retention

## Testing

Tests are located in `test/event/` and focus on geometry calculations and detection association. Run tests within the event container environment.

## Key Algorithms

- **Association**: Delay-Doppler matching of radar detections to ADS-B truth
- **Localization**: Three methods for computing target positions from bistatic range measurements
- **Tracking**: Multi-hypothesis tracking with Kalman filtering, handling track states (TENTATIVE → CONFIRMED → COASTING → DELETED)

