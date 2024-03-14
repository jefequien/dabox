#!/bin/bash

set -e

# Kill all ffmpeg
pkill -x ffmpeg

# Kill MediaMTX server if up
if [[ $(lsof -t -i:8000) ]]; then
    echo "Killing MediaMTX server"
    kill $(lsof -t -i:8000)
fi

# Kill inference server if up
if [[ $(lsof -t -i:5001) ]]; then
    echo "Killing inference server"
    kill $(lsof -t -i:5001)
fi

# Kill zmq if up
if [[ $(lsof -t -i:5555) ]]; then
    echo "Killing zmq"
    kill $(lsof -t -i:5555)
fi

if [[ $(lsof -t -i:5556) ]]; then
    echo "Killing zmq"
    kill $(lsof -t -i:5556)
fi

# Kill gui if up
if [[ $(lsof -t -i:8080) ]]; then
    echo "Killing gui"
    kill $(lsof -t -i:8080)
fi
