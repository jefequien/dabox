#!/bin/bash

set -e

INSTALL_DIR=.output/mediamtx_downloads
PLATFORM="linux_amd64"

mkdir -p $INSTALL_DIR
wget -nc -O $INSTALL_DIR/mediamtx.tar.gz https://github.com/bluenviron/mediamtx/releases/download/v1.6.0/mediamtx_v1.6.0_$PLATFORM.tar.gz
tar -xf $INSTALL_DIR/mediamtx.tar.gz --directory $INSTALL_DIR

FFMPEG_INPUT_FORMAT=v4l2 FFMPEG_INPUT_DEVICE0=/dev/video0 FFMPEG_INPUT_DEVICE1=/dev/video2 $INSTALL_DIR/mediamtx
