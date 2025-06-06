# Stone Soup Advanced Tracking Integration Plan

This document outlines the specific changes needed to integrate Stone Soup's advanced multi-dimensional data association, track-to-track fusion, and enhanced tracking framework into 3lips.

## Current State Analysis

### What 3lips Already Has ✅
- **Stone Soup Foundation**: Already using Stone Soup 1.6.0 as dependency
- **Track Extension**: `Track.py` extends `StoneSoupTrack` with custom status management
- **Basic State Management**: Position/velocity state vectors and covariance matrices
- **Simple Association**: Greedy nearest neighbor with Euclidean gating
- **Track Lifecycle**: TENTATIVE → CONFIRMED → COASTING → DELETED states

### What's Missing ❌
- **Advanced Data Association**: Only greedy nearest neighbor implemented
- **Track-to-Track Fusion**: No track merging or fusion capabilities  
- **Multi-Hypothesis Management**: Single hypothesis tracking only
- **Proper Stone Soup Integration**: Custom tracking logic instead of Stone Soup trackers

## Required Changes

### 1. Replace Custom Tracker with Stone Soup MultiTargetTracker

**Current**: `Tracker.py` implements custom tracking logic
**Target**: Use Stone Soup's `MultiTargetTracker` with pluggable components

#### New Architecture:
```python
# event/algorithm/track/StoneSoupTracker.py
from stonesoup.tracker.simple import MultiTargetTracker
from stonesoup.hypothesiser.distance import DistanceHypothesiser  
from stonesoup.measures.mahalanobis import Mahalanobis
from stonesoup.associator.neighbour import GNNWith2DAssignment
from stonesoup.deleter.error import CovarianceBasedDeleter
from stonesoup.initiator.simple import MultiMeasurementInitiator

class StoneSoupTracker:
    def __init__(self, config=None):
        # Configure Stone Soup components
        self.hypothesiser = DistanceHypothesiser(
            predictor=self.predictor,
            updater=self.updater, 
            measure=Mahalanobis(),
            missed_distance=config.get('gating_threshold', 5.0)
        )
        
        self.associator = GNNWith2DAssignment(self.hypothesiser)
        
        self.deleter = CovarianceBasedDeleter(
            delete_threshold=config.get('delete_threshold', 3)
        )
        
        self.initiator = MultiMeasurementInitiator(
            prior_state=self.prior_state,
            measurement_model=self.measurement_model,
            deleter=self.deleter,
            data_associator=self.associator,
            updater=self.updater,
            min_points=config.get('min_hits_to_confirm', 3)
        )
        
        self.tracker = MultiTargetTracker(
            initiator=self.initiator,
            deleter=self.deleter,
            detector=self.detector,
            data_associator=self.associator,
            updater=self.updater
        )
```

### 2. Implement Advanced Data Association Algorithms

#### Create Configurable Association Module:
```python
# event/algorithm/associator/StoneSoupAssociator.py
from stonesoup.associator.neighbour import GNNWith2DAssignment  
from stonesoup.associator.jpda import JPDA
from stonesoup.associator.mfa import MultiFrameAssignment

class ConfigurableAssociator:
    def __init__(self, association_type='gnn', config=None):
        if association_type == 'gnn':
            self.associator = GNNWith2DAssignment(hypothesiser)
        elif association_type == 'jpda':
            self.associator = JPDA(hypothesiser)
        elif association_type == 'mfa':
            self.associator = MultiFrameAssignment(hypothesiser)
        elif association_type == 'mht':
            self.associator = MHTAssociator(hypothesiser)  # If available
```

### 3. Add Track-to-Track Fusion Capabilities

#### Implement Fusion Manager:
```python
# event/algorithm/fusion/TrackFusionManager.py
from stonesoup.tracker.fuse import TrackFuser
from stonesoup.merger.point import PointMerger

class TrackFusionManager:
    def __init__(self, config=None):
        self.merger = PointMerger()
        self.fusion_distance_threshold = config.get('fusion_threshold', 100.0)
        
    def fuse_tracks(self, track_list_1, track_list_2):
        """Fuse tracks from different sources (e.g., different sensor types)"""
        return self.merger.merge_tracks(track_list_1, track_list_2)
        
    def merge_similar_tracks(self, tracks):
        """Merge tracks that represent the same target"""
        # Implement track merging logic using Stone Soup fusion
        pass
```

### 4. Enhanced Multi-Sensor Integration

#### Create Multi-Sensor Tracker:
```python
# event/algorithm/track/MultiSensorTracker.py  
from stonesoup.tracker.multisensor import MultiSensorTracker as SSMultiSensorTracker

class MultiSensorTracker:
    def __init__(self, config=None):
        self.radar_tracker = StoneSoupTracker(config.get('radar_config'))
        self.adsb_tracker = StoneSoupTracker(config.get('adsb_config'))
        self.fusion_manager = TrackFusionManager(config.get('fusion_config'))
        
    def update(self, radar_detections, adsb_detections, timestamp):
        # Update individual trackers
        radar_tracks = self.radar_tracker.update(radar_detections, timestamp)
        adsb_tracks = self.adsb_tracker.update(adsb_detections, timestamp)
        
        # Fuse track results
        fused_tracks = self.fusion_manager.fuse_tracks(radar_tracks, adsb_tracks)
        return fused_tracks
```

### 5. Measurement and State Model Integration

#### Create Stone Soup Measurement Models:
```python
# event/algorithm/models/MeasurementModels.py
from stonesoup.models.measurement.linear import LinearGaussian

class ECEFMeasurementModel(LinearGaussian):
    """Measurement model for ECEF position measurements"""
    def __init__(self, noise_covar):
        # H matrix for position-only measurements from 6D state [pos, vel]
        H = np.array([[1, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0], 
                      [0, 0, 1, 0, 0, 0]])
        super().__init__(ndim_state=6, mapping=[0, 1, 2], noise_covar=noise_covar)
```

#### Create Motion Models:
```python
# event/algorithm/models/MotionModels.py
from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, ConstantVelocity

class ECEFMotionModel(CombinedLinearGaussianTransitionModel):
    """3D constant velocity motion model in ECEF coordinates"""
    def __init__(self, noise_diff_coeff=0.1):
        super().__init__([
            ConstantVelocity(noise_diff_coeff),  # X dimension
            ConstantVelocity(noise_diff_coeff),  # Y dimension  
            ConstantVelocity(noise_diff_coeff)   # Z dimension
        ])
```

## Implementation Steps

### Phase 1: Core Integration (HIGH Priority)
1. **Create Stone Soup wrapper classes** preserving existing Track interface
2. **Replace `Tracker._data_association()`** with configurable Stone Soup associators
3. **Integrate measurement and motion models** for proper Stone Soup operation
4. **Maintain backward compatibility** with existing event processing loop

### Phase 2: Advanced Features (MEDIUM Priority)  
1. **Add track-to-track fusion** for merging similar tracks
2. **Implement multi-hypothesis tracking** for complex scenarios
3. **Add configurable association algorithms** (GNN, JPDA, MFA)
4. **Enhanced multi-sensor fusion** capabilities

### Phase 3: Optimization (LOW Priority)
1. **Performance tuning** of Stone Soup components
2. **Memory optimization** for hypothesis management
3. **Real-time processing** optimizations

## File Changes Required

### New Files:
- `event/algorithm/track/StoneSoupTracker.py` - Main Stone Soup tracker wrapper
- `event/algorithm/associator/StoneSoupAssociator.py` - Advanced association algorithms  
- `event/algorithm/fusion/TrackFusionManager.py` - Track fusion capabilities
- `event/algorithm/models/MeasurementModels.py` - Stone Soup measurement models
- `event/algorithm/models/MotionModels.py` - Stone Soup motion models

### Modified Files:
- `event/algorithm/track/Tracker.py` - Refactor to use Stone Soup components
- `event/event.py` - Update main processing loop integration
- `event/algorithm/track/Track.py` - Enhance Stone Soup Track integration

### Configuration Changes:
- Add Stone Soup tracker configuration to environment variables
- Association algorithm selection (GNN/JPDA/MFA/MHT)
- Fusion threshold parameters
- Multi-sensor tracking settings

## Benefits of Integration

### Immediate Gains:
- **Mahalanobis Gating**: Statistically optimal gating vs current Euclidean
- **Optimal Assignment**: Hungarian algorithm vs greedy nearest neighbor
- **Track Merging**: Automatic merging of similar tracks
- **Robust State Estimation**: Proper Kalman filtering implementation

### Advanced Capabilities:
- **Multi-Hypothesis Tracking**: Handle ambiguous associations
- **Joint Probabilistic Data Association**: Statistical association in clutter
- **Multi-Frame Assignment**: Temporal association across scans
- **Track-to-Track Fusion**: Fuse tracks from different sensor types without truth reference

### Architecture Benefits:
- **Modular Design**: Pluggable association/fusion algorithms
- **Industry Standard**: Battle-tested tracking algorithms
- **Extensibility**: Easy to add new tracking capabilities
- **Maintainability**: Reduced custom tracking code

## Compatibility Considerations

### Preserved Interfaces:
- `Track` class API remains compatible with existing serialization
- `Tracker.update_all_tracks()` signature maintained for event loop
- Track status management (TENTATIVE/CONFIRMED/COASTING/DELETED) preserved
- ADS-B integration workflow unchanged

### Migration Strategy:
1. **Gradual Replacement**: Replace components incrementally
2. **Configuration Flags**: Allow switching between old/new implementations
3. **Testing Framework**: Validate tracking performance on existing data
4. **Rollback Capability**: Maintain old implementation as fallback

This integration provides a solid foundation for supporting passive radar scenarios while significantly enhancing the existing ADS-B tracking capabilities.