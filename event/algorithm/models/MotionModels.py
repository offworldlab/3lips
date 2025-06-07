import numpy as np
from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, ConstantVelocity


def create_ecef_constant_velocity_model(noise_diff_coeff=0.1):
    """Factory function to create ECEF constant velocity motion model.
    
    Args:
        noise_diff_coeff: Noise diffusion coefficient (process noise intensity)
    
    Returns:
        CombinedLinearGaussianTransitionModel for 3D constant velocity motion.
    """
    # Create three 1D constant velocity models for x, y, z
    model_list = [
        ConstantVelocity(noise_diff_coeff),  # x, vx
        ConstantVelocity(noise_diff_coeff),  # y, vy  
        ConstantVelocity(noise_diff_coeff)   # z, vz
    ]
    
    return CombinedLinearGaussianTransitionModel(model_list)


def create_ecef_constant_acceleration_model(noise_diff_coeff=0.01):
    """Factory function to create ECEF constant acceleration motion model.
    
    Args:
        noise_diff_coeff: Noise diffusion coefficient for acceleration
    
    Returns:
        CombinedLinearGaussianTransitionModel for 3D constant acceleration motion.
    """
    from stonesoup.models.transition.linear import ConstantAcceleration
    
    # Create three 1D constant acceleration models for x, y, z
    model_list = [
        ConstantAcceleration(noise_diff_coeff),  # x, vx, ax
        ConstantAcceleration(noise_diff_coeff),  # y, vy, ay
        ConstantAcceleration(noise_diff_coeff)   # z, vz, az
    ]
    
    return CombinedLinearGaussianTransitionModel(model_list)