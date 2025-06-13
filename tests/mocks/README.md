# Mock Services for CI Testing

This directory contains mock responses for external dependencies that aren't available in the standalone 3lips repository.

## Mock Services Provided

- **Mock Radar Services**: Provides empty detection responses on ports 8001, 8002
- **Mock ADS-B Service**: Provides empty aircraft data on port 8003

## Usage

The `docker-compose.ci.yml` file uses nginx to serve these mock responses, allowing the 3lips services to start and respond correctly without requiring the full retina monorepo dependencies.

## Mock API Responses

All mock services return empty but valid JSON responses:
- Radar: `{"detections": [], "timestamp": <current_timestamp>}`
- ADS-B: `{"aircraft": [], "timestamp": <current_timestamp>}`