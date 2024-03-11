#!/bin/bash

set -e

sudo tailscale funnel --https=443 off
sudo tailscale funnel --https=8443 off
