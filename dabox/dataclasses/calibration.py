from dataclasses import dataclass

import numpy as np


@dataclass
class CameraCalibration:
    K: np.ndarray
    mat: np.ndarray


@dataclass
class VehicleCalibration:
    cameras: dict[str, CameraCalibration]
    image_size: tuple[int, int]
