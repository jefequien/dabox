![DaBox](docs/viser_logo.svg)

Building robots is hard. If we want to live in a future where there are robots everywhere, robots need to be a lot easier to build.

# Installation

## Create environment

`dabox` requires `python >= 3.10`. We recommend using conda to manage dependencies. Make sure to install [Conda](https://docs.conda.io/miniconda.html) before proceeding.

```bash
conda create --name dabox -y python=3.10
conda activate dabox
pip install --upgrade pip setuptools
```

## Install from source

The current recommended way to install `dabox` is from source.

```bash
git clone https://github.com/jefequien/dabox.git
cd dabox
pip install -e .'[dev]'
```

# Usage

Start DaBox!
```bash
dabox-export-yolov8
dabox-up
```
