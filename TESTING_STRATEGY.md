# Simplified Testing Strategy for 3lips

## Core Principle: Test for Correctness Only

Focus on ensuring the system produces correct results. Performance testing can come later.

## Critical Issues to Fix First

### 1. Tests Won't Run
The current tests fail because of import path issues. Fix this first:

```bash
# Run tests from project root with proper Python path
cd /Users/jonnyspicer/repos/retina/3lips
PYTHONPATH=./event python -m pytest test/
```

### 2. Missing Core Tests
We have tests for geometry and spatial detection, but nothing for the main tracking logic.

## Simple Test Plan

### Phase 1: Fix What's Broken (Do This First)
1. **Fix import paths** in test files
2. **Create test runner script** that sets PYTHONPATH correctly
3. **Verify existing tests pass**

### Phase 2: Test Core Tracking Logic
Create just these essential tests:

#### 1. Track Lifecycle Test
```python
# test/event/test_track_lifecycle.py
def test_track_states():
    """Test that tracks move through states correctly:
    TENTATIVE → CONFIRMED → COASTING → DELETED"""
    # Create track, update it, verify state changes
```

#### 2. Association Test  
```python
# test/event/test_association.py
def test_detection_to_track_association():
    """Test that detections associate to correct tracks"""
    # Create tracks, new detections, verify correct matching
```

#### 3. ADS-B Integration Test
```python
# test/event/test_adsb_integration.py
def test_adsb_track_creation():
    """Test that ADS-B data creates confirmed tracks"""
    # Send ADS-B data, verify tracks are created as CONFIRMED
```

### Phase 3: Integration Tests (One Simple Test)
```python
# test/integration/test_full_pipeline.py
def test_radar_to_track_pipeline():
    """Test complete flow: radar detection → track output"""
    # Send synthetic radar data
    # Verify tracks are created and updated
    # Check output format is correct
```

## What NOT to Test (For Now)
- Performance/speed
- Memory usage
- Docker containers
- API endpoints
- Cesium visualization
- Edge cases
- Error handling

## Test Data Approach

Keep it simple - hardcode test scenarios:

```python
# test/fixtures/simple_scenarios.py
SINGLE_AIRCRAFT = {
    "detections": [
        {"time": 0, "range": 1000, "bearing": 45},
        {"time": 1, "range": 1100, "bearing": 45.5},
        {"time": 2, "range": 1200, "bearing": 46}
    ],
    "expected_track_count": 1,
    "expected_final_position": [1200, 46]
}
```

## Before Stone Soup Integration (Issue #1)

Just create ONE test that captures current behavior:

```python
# test/integration/test_current_tracker_baseline.py
def test_current_tracker_baseline():
    """Capture how the current tracker behaves"""
    # Run known scenario through current tracker
    # Save the output as the baseline
    # After Stone Soup integration, this test ensures same behavior
```

## Implementation Steps

### Week 1: Fix Tests
1. Fix import issues
2. Create `run_tests.sh` script:
   ```bash
   #!/bin/bash
   cd /Users/jonnyspicer/repos/retina/3lips
   PYTHONPATH=./event python -m pytest test/ -v
   ```
3. Verify existing geometry tests pass

### Week 2: Core Tests
1. Write track lifecycle test
2. Write association test  
3. Write ADS-B integration test

### Week 3: Integration Test
1. Write one full pipeline test
2. Create baseline test for Stone Soup comparison

## Success Criteria

- All tests pass reliably
- Core tracking behavior is validated
- Stone Soup integration won't break existing functionality

## Test Dependencies

Add to `event/requirements.txt`:
```
pytest>=8.0.0
pytest-mock>=3.12.0
```

That's it. No fancy test frameworks, no performance benchmarks, no complex fixtures. Just simple tests that verify the tracking system works correctly.