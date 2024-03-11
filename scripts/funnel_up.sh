#!/bin/bash

set -e

sudo tailscale funnel --bg --https=443 8080
sudo tailscale funnel --bg --https=8443 8443
