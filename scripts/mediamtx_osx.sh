#!/bin/bash

set -e

INSTALL_DIR=.output/mediamtx_downloads
PLATFORM="darwin_arm64"

mkdir -p $INSTALL_DIR
pushd $INSTALL_DIR
    wget -nc https://github.com/bluenviron/mediamtx/releases/download/v1.6.0/mediamtx_v1.6.0_$PLATFORM.tar.gz
    tar -xvf mediamtx_v1.6.0_$PLATFORM.tar.gz
popd

FFMPEG_INPUT_FORMAT=avfoundation FFMPEG_INPUT_DEVICE=0 $INSTALL_DIR/mediamtx
