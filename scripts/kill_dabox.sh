#!/bin/bash

set -e

# Kill MediaMTX server if up
if [[ $(lsof -t -i:8000) ]]; then
    echo "Killing MediaMTX server"
    kill $(lsof -t -i:8000)
fi

# Kill GUI if up
if [[ $(lsof -t -i:8080) ]]; then
    echo "Killing DaBox gui"
    kill $(lsof -t -i:8080)
fi

# Kill all ffmpeg
pkill -x ffmpeg
