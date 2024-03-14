```
_|_|_|      _|_|    _|_|_|      _|_|    _|      _| 
_|    _|  _|    _|  _|    _|  _|    _|    _|  _|   
_|    _|  _|_|_|_|  _|_|_|    _|    _|      _|     
_|    _|  _|    _|  _|    _|  _|    _|    _|  _|   
_|_|_|    _|    _|  _|_|_|      _|_|    _|      _| 
```

Building robots is hard. If we want to live in a future where there are robots everywhere, robots need to be a lot easier to build.

Getting neural networks to run with low-latency on video streams is notoriously difficult. `dabox` is a machine learning-friendly, easy-to-install Python application with several features that every robot needs.

## Features available out of "dabox"
- Low-latency inference with [FFmpeg](https://ffmpeg.org/), [ZMQ](https://zeromq.org/), and [ONNX Runtime](https://onnxruntime.ai/)
- Web-based 3D visualization by [viser](https://github.com/nerfstudio-project/viser)
- Real-time RTSP, LL-HLS, WebRTC streams by [MediaMTX](https://github.com/bluenviron/mediamtx)
- Automatic camera discovery and multi-camera support
- Supported on Mac, Linux, and x86+dGPU systems

# Installation

## Create environment

`dabox` requires `python >= 3.10`. We recommend using conda to manage dependencies. Make sure to install [Miniconda](https://docs.conda.io/miniconda.html) before proceeding.

```bash
conda create --name dabox -y python=3.10 && conda activate dabox
```

Install from pypi

```
pip install dabox-project
```

**OR** install from `dabox` from source. 

```bash
git clone https://github.com/jefequien/dabox.git && cd dabox
pip install -e .'[dev]'
```

# Usage

Start DABOX!
```bash
dabox-up

# Visit http://localhost:8080
# Ctrl+C to stop server

# Sometimes DABOX does not stop cleanly. 
# Run this command in another window to kill it.
dabox-kill
```
