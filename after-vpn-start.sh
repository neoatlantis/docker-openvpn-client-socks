#!/bin/bash

# This scripts will run automatically after OpenVPN has established connection.

set -e

echo "---- VPN started! Start tunnel..."

echo "/usr/bin/sockd -D"
/usr/sbin/sockd -D &

if [ "$1" != "none" ]; then
    echo "socat TCP-LISTEN:1984,fork,reuseaddr TCP:$1"
    socat TCP-LISTEN:1984,fork,reuseaddr TCP:$1 &
fi
