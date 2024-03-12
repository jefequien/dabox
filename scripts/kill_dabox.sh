#!/bin/bash

set -e

# Kill MediaMTX server if up
if [[ $(lsof -t -i:8000) ]]; then
    kill $(lsof -t -i:8000)
fi

# Kill all ffmpeg
pkill -x ffmpeg
