from dataclasses import dataclass

import numpy as np
from transformations import euler_matrix


@dataclass
class CameraCalibration:
    K: np.ndarray
    mat: np.ndarray


@dataclass
class VehicleCalibration:
    cameras: dict[str, CameraCalibration]
    image_size: tuple[int, int]


def get_default_calibration(camera_names: list[str]) -> VehicleCalibration:
    cameras = {}
    for camera_name in camera_names:
        if camera_name == "camera0":
            camera_calibration = CameraCalibration(
                K=np.array(
                    [[0.5, 0.0, 0.5], [0.0, 0.5 * (640 / 480), 0.5], [0.0, 0.0, 1.0]]
                ),
                mat=np.eye(4),
            )
        else:
            camera_calibration = CameraCalibration(
                K=np.array(
                    [[0.5, 0.0, 0.5], [0.0, 0.5 * (640 / 480), 0.5], [0.0, 0.0, 1.0]]
                ),
                mat=euler_matrix(0, np.pi / 2, 0),
            )
        cameras[camera_name] = camera_calibration

    calibration = VehicleCalibration(
        cameras=cameras,
        image_size=(640, 480),
    )
    return calibration
