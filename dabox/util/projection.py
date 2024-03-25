"""3D projection utilities"""

import numpy as np


def backproject_depth(depth: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Given a depth map and camera intrinsics, backproject the pixels to get a point cloud.

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


def transform_points(points: np.ndarray, mat: np.ndarray) -> np.ndarray:
    n = len(points)
    points_tf = np.hstack((points, np.ones((n, 1), dtype=points.dtype)))
    points_tf = np.matmul(mat, points_tf.T).T
    points_tf = points_tf[:, :3]
    assert points.dtype == points_tf.dtype
    return points_tf
