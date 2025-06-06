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

## Issue Development Workflow

When working on GitHub issues, follow this standardized workflow:

### 1. Branch Management
```bash
# Create and checkout a new branch for the issue
git checkout -b issue-##-brief-description

# Example: git checkout -b issue-12-nearest-neighbor-association
```

### 2. Development Process
- Implement the feature or fix following existing code patterns
- Write **minimal, idiomatic code** - prefer concise, readable solutions
- **DO NOT add comments** unless absolutely necessary for complex algorithms
- Follow existing architectural patterns and naming conventions

### 3. Testing Requirements
- **All new business logic MUST have corresponding tests**
- Add tests in `test/event/` following existing patterns
- Ensure tests cover edge cases and error conditions
- Run tests to verify functionality:
```bash
# Run tests in event container
docker exec -it 3lips-event python -m pytest test/
```

### 4. Code Review Process
Before creating a PR, perform a thorough self-review:

- **Remove unnecessary comments** - code should be self-documenting
- **Minimize lines of code** - prefer concise, readable implementations
- **Ensure idiomatic Python/JavaScript** - follow language best practices
- **Check for code duplication** - extract common functionality
- **Verify error handling** - handle edge cases appropriately

### 5. Pre-commit Validation
```bash
# Run pre-commit hooks to catch issues early
git add .
git commit -m "Initial implementation"

# Fix any issues flagged by pre-commit hooks
# Re-commit after fixes
```

### 6. Pull Request Creation
```bash
# Push branch to remote
git push -u origin issue-##-brief-description

# Create PR using GitHub CLI
gh pr create --title "Fix ###: Brief description" \
  --body "Closes ###\n\n## Changes\n- Brief bullet points\n\n## Testing\n- Test coverage added for new functionality"
```

### 7. PR Template
Use this template for pull request descriptions:
```markdown
Closes #[issue-number]

## Changes
- Concise bullet points of what changed
- Focus on the "what" not the "how"

## Testing
- New tests added for [specific functionality]
- All existing tests pass
- Edge cases covered: [list any specific edge cases]

## Code Quality
- [ ] Removed unnecessary comments
- [ ] Minimized lines of code
- [ ] Code is idiomatic and follows patterns
- [ ] Pre-commit hooks pass
- [ ] No code duplication
```

### 8. Review Checklist
Before submitting PR, verify:
- [ ] Branch name follows `issue-##-brief-description` pattern
- [ ] All new business logic has tests
- [ ] Code is minimal and idiomatic
- [ ] No unnecessary comments added
- [ ] Pre-commit hooks pass without issues
- [ ] PR description is clear and complete

## Testing

Tests are located in `test/event/` and focus on geometry calculations and detection association. Run tests within the event container environment.

**Test Requirements:**
- All new business logic must have corresponding unit tests
- Tests should cover normal operation, edge cases, and error conditions
- Follow existing test patterns and naming conventions

## Key Algorithms

- **Association**: Delay-Doppler matching of radar detections to ADS-B truth
- **Localization**: Three methods for computing target positions from bistatic range measurements
- **Tracking**: Multi-hypothesis tracking with Kalman filtering, handling track states (TENTATIVE → CONFIRMED → COASTING → DELETED)

