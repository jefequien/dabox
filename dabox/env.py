"""Environment Variables"""

import os
import platform
from pathlib import Path

# -----------------------------------------------------------------------------
# Global Directories
# -----------------------------------------------------------------------------

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME_DIR = Path(os.path.expanduser("~"))

DABOX_CACHE_DIR = HOME_DIR / ".cache" / "dabox"
ASSETS_DIR = ROOT_DIR / "dabox" / "assets"

PLATFORM = "linux" if "Linux" in platform.platform() else "osx"
FFMPEG_INPUT_FORMAT = "v4l2" if PLATFORM == "linux" else "avfoundation"

GUI_PORT = 8080
RTSP_PORT = 8554
HLS_PORT = 8888
WEBRTC_PORT = 8443
