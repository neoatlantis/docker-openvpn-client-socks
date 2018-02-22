#!/bin/bash

# This scripts will run automatically after OpenVPN has established connection.

set -e

echo "---- VPN started! Start tunnel..."
echo "socat TCP-LISTEN:1984,fork,reuseaddr TCP:$1"

socat TCP-LISTEN:1984,fork,reuseaddr TCP:$1 &

