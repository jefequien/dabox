#!/bin/bash

set -e

INSTALL_DIR=.output/mediamtx_downloads
PLATFORM="linux_amd64"

mkdir -p $INSTALL_DIR
pushd $INSTALL_DIR
    wget -nc https://github.com/bluenviron/mediamtx/releases/download/v1.6.0/mediamtx_v1.6.0_$PLATFORM.tar.gz
    tar -xvf mediamtx_v1.6.0_$PLATFORM.tar.gz
popd

FFMPEG_INPUT_FORMAT=v4l2 FFMPEG_INPUT_DEVICE=/dev/video0 $INSTALL_DIR/mediamtx
