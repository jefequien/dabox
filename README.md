![DaBox](docs/viser_logo.svg)

Building robots is hard. If we want to live in a future where there are robots everywhere, robots need to be a lot easier to build.

Getting neural networks to run in real-time with low-latency on video streams is notoriously difficult. DaBox is designed to be a ML-friendly, easy-to-install application with several features that every robot needs.

# Features available out of "DaBox"
- Low-latency inference with FFMpeg, ZMQ, and ONNX Runtime
- GUI with 3D viewer and WebRTC streams

# Installation

## Create environment

`dabox` requires `python >= 3.10`. We recommend using conda to manage dependencies. Make sure to install [Conda](https://docs.conda.io/miniconda.html) before proceeding.

```bash
conda create --name dabox -y python=3.10 && conda activate dabox
```

## Install from source

The current recommended way to install `dabox` is from source.

```bash
git clone https://github.com/jefequien/dabox.git && cd dabox
pip install -e .'[dev]'
```

# Usage

Start DaBox!
```bash
dabox-up
```
