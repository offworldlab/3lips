# Passive Radar Architecture Analysis

This document analyzes the requirements for extending 3lips to support passive radar delay-Doppler data sources instead of relying on ADS-B truth data.

## Current ADS-B vs Passive Radar Paradigms

### Current ADS-B Approach
- **Truth Reference**: ADS-B provides known aircraft positions/velocities
- **Association**: Simple nearest-neighbor matching in position/time space
- **Localization**: Validates/refines ADS-B positions using radar measurements
- **Tracking**: Truth-aided tracking with high confidence initialization

### Passive Radar Approach  
- **No Truth Reference**: Only raw bistatic delay-Doppler measurements
- **Association**: Multi-dimensional association across (delay, Doppler, time, geometry)
- **Localization**: Geometric position solving from multiple bistatic measurements
- **Tracking**: Pure sensor-based tracking without external position reference

## Required Architecture Components

### 1. Bistatic Sensor Models ❌ **MISSING IN STONE SOUP**

**Requirements**:
- Custom sensor models outputting delay-Doppler measurements
- Support for multiple transmitter-receiver geometries
- Bistatic range calculation: `R_b = c * τ / 2` (where τ is time delay)
- Bistatic Doppler: `f_d = (f_0 / c) * (v_r · û_r + v_t · û_t)` 

**Stone Soup Assessment**:
- **Available**: Standard radar sensors (RadarBearingRange, RadarBearingRangeRate)
- **Missing**: Bistatic/passive radar sensor models
- **Action Required**: Create custom sensor classes extending Stone Soup base sensors

**Implementation Path**:
```python
# Custom bistatic sensor extending Stone Soup
class BistaticDelayDopplerSensor(Sensor):
    def __init__(self, tx_position, rx_position, frequency, ...):
        # Transmitter and receiver positions
        # Operating frequency for Doppler calculations
        
    def measure(self, state, noise=True):
        # Return Detection with delay and Doppler measurements
```

### 2. Multi-Dimensional Data Association ✅ **AVAILABLE IN STONE SOUP**

**Requirements**:
- Associate (delay, Doppler, time) measurements across multiple bistatic pairs
- Handle complex hypothesis spaces with geometric constraints
- Multi-frame association for sparse measurements

**Stone Soup Assessment**:
- **✅ Excellent Support**: Multiple advanced association algorithms
  - **Multi-Hypothesis Tracking (MHT)**: Handle complex association scenarios
  - **Probabilistic Multi-Hypothesis Tracker (PMHT)**: Statistical association
  - **Efficient Hypothesis Management (EHM)**: Scalable hypothesis pruning
  - **Loopy Belief Propagation (LBP)**: Graph-based association
  - **Multi-Frame Assignment (MFA)**: Temporal association

**Implementation Path**:
- Leverage existing Stone Soup associators with custom distance metrics
- Create multi-dimensional gating functions for delay-Doppler space

### 3. Geometric Localization ❌ **MISSING IN STONE SOUP**

**Requirements**:
- Solve target position from multiple bistatic range measurements
- Handle Doppler constraints for velocity estimation
- Robust position solving with measurement uncertainties
- Support for over-determined systems (>3 measurements)

**Stone Soup Assessment**:
- **Missing**: No geometric localization algorithms found
- **Available**: Basic coordinate transformations and state estimation
- **Action Required**: Implement geometric intersection algorithms

**Implementation Path**:
```python
# Extend existing 3lips localization with multi-bistatic support
class MultibistaticLocalizer:
    def localize(self, delay_doppler_measurements, geometries):
        # Solve system of bistatic range equations
        # Include Doppler constraints for velocity
        # Return position and velocity estimates with uncertainties
```

**Required Algorithms**:
- **Spherical Intersection**: Extended for multiple bistatic pairs
- **Least Squares**: Over-determined system solving  
- **Weighted Least Squares**: Measurement uncertainty handling
- **Doppler Velocity Solving**: Velocity estimation from Doppler shifts

### 4. Track-to-Track Fusion ✅ **EXCELLENT IN STONE SOUP**

**Requirements**:
- Fuse tracks from different bistatic geometries
- Handle tracks without truth reference
- Manage track uncertainties and correlations

**Stone Soup Assessment**:
- **✅ Excellent Support**: 
  - **Covariance Intersection**: Fusion without truth reference
  - **Track Stitching**: Connect track segments
  - **Multi-sensor Fusion**: Different sensor type integration

**Implementation Path**:
- Direct integration with existing Stone Soup track fusion
- Minimal custom development required

### 5. Enhanced Track Management ✅ **MOSTLY AVAILABLE**

**Requirements**:
- Robust track initiation from uncertain measurements
- Track merging when multiple solutions converge
- Prediction-heavy tracking without truth validation

**Stone Soup Assessment**:
- **✅ Available**: Advanced tracking with Stone Soup Track classes
- **✅ Available**: Multi-hypothesis track management
- **🔶 Partial**: Track merging (already identified gap in current 3lips)

## Implementation Priority Matrix

| Component | Stone Soup Support | Development Effort | Priority |
|-----------|-------------------|-------------------|----------|
| Bistatic Sensors | ❌ Missing | High | **CRITICAL** |
| Geometric Localization | ❌ Missing | High | **CRITICAL** |
| Multi-dimensional Association | ✅ Excellent | Low | **HIGH** |
| Track-to-Track Fusion | ✅ Excellent | Low | **MEDIUM** |
| Track Management | ✅ Mostly Available | Medium | **MEDIUM** |

## Architecture Changes Required

### New Modules to Create

1. **`algorithm/sensor/`** (NEW)
   - `BistaticSensor.py`: Custom bistatic delay-Doppler sensor models
   - `PassiveRadarGeometry.py`: Transmitter-receiver geometry handling

2. **`algorithm/localization/`** (EXTEND)
   - `MultibistaticLocalizer.py`: Multi-pair geometric localization
   - `DopplerVelocitySolver.py`: Velocity estimation from Doppler

3. **`algorithm/associator/`** (EXTEND)
   - `DelayDopplerAssociator.py`: Multi-dimensional association logic
   - `GeometricGating.py`: Bistatic geometry-aware gating

### Modified Modules

1. **`event/event.py`**: Main processing loop integration
2. **`algorithm/track/Tracker.py`**: Enhanced track management
3. **Configuration**: New parameters for passive radar geometries

## Stone Soup Integration Benefits

**Excellent Foundation**:
- Advanced data association algorithms ready for complex scenarios
- Robust track fusion without requiring truth reference  
- Mature tracking framework with uncertainty management
- Extensible sensor model architecture

**Critical Gaps Requiring Custom Development**:
- Bistatic sensor models for delay-Doppler measurements
- Geometric localization algorithms for multiple bistatic pairs
- Integration layer between custom components and Stone Soup framework

## Conclusion

**Stone Soup provides 60-70% of required functionality** for passive radar support, particularly excelling in data association and track fusion. The main development effort centers on:

1. **Custom bistatic sensor models** (high effort)
2. **Geometric localization algorithms** (high effort)  
3. **Integration and configuration** (medium effort)

The existing 3lips architecture provides an excellent foundation, with the geometry and coordinate transformation utilities in `algorithm/geometry/` directly applicable to passive radar scenarios.