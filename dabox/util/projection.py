"""
Utilities for projecting points from 3d to 2d (and back).
"""

import numpy as np


def backproject_depth(depth: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Given a depth map and camera intrinsics, backproject each pixel to get a point cloud.

    Args:
        depth (np.ndarray): depth map with shape (h, w)
        K (np.ndarray): normalized camera intrinsic with shape (3, 3)

    Returns:
        np.ndarray: points with shape (h * w, 3)
    """
    h, w = depth.shape[:2]
    k_scaled = K.copy()
    k_scaled[0, :] *= w
    k_scaled[1, :] *= h

    grid = np.mgrid[0:h, 0:w]
    u, v = grid[1], grid[0]
    z = depth
    x = (u - k_scaled[0, 2]) * z / k_scaled[0, 0]
    y = (v - k_scaled[1, 2]) * z / k_scaled[1, 1]
    points: np.ndarray = np.stack([x, y, z], axis=-1).reshape(-1, 3)
    return points
