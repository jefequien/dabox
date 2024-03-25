from dataclasses import dataclass

import numpy as np
from transformations import euler_matrix


@dataclass
class CameraCalibration:
    K: np.ndarray
    mat: np.ndarray
    image_size: tuple[int, int]


@dataclass
class VehicleCalibration:
    cameras: dict[str, CameraCalibration]


def get_default_calibration(
    camera_names: list[str], image_sizes: list[tuple[int, int]]
) -> VehicleCalibration:
    cameras = {}
    for camera_name, image_size in zip(camera_names, image_sizes):
        if camera_name == "camera0":
            camera_calibration = CameraCalibration(
                K=np.array(
                    [
                        [0.5, 0.0, 0.5],
                        [0.0, 0.5 * (image_size[0] / image_size[1]), 0.5],
                        [0.0, 0.0, 1.0],
                    ]
                ),
                mat=np.eye(4),
                image_size=image_size,
            )
        else:
            camera_calibration = CameraCalibration(
                K=np.array(
                    [
                        [0.5, 0.0, 0.5],
                        [0.0, 0.5 * (image_size[0] / image_size[1]), 0.5],
                        [0.0, 0.0, 1.0],
                    ]
                ),
                mat=euler_matrix(0, np.pi / 2, 0),
                image_size=image_size,
            )
        cameras[camera_name] = camera_calibration

    calibration = VehicleCalibration(cameras=cameras)
    return calibration
