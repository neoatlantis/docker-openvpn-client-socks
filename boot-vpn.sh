#!/bin/bash


cd /etc/openvpn

echo "---- Starting VPN..."

echo "Start ping monitor..."

echo "/usr/local/bin/ping-monitor.py $1 &"

/usr/local/bin/ping-monitor.py $1 &

echo "Start OpenVPN..."

echo "/usr/sbin/openvpn --config /ovpn.conf --script-security 2 --inactive 3600 --ping $2 --ping-exit $3 --up \"/usr/local/bin/after-vpn-start.sh $4\""

/usr/sbin/openvpn\
    --config /ovpn.conf\
    --script-security 2\
    --inactive 3600 --ping $2 --ping-exit $3\
    --up "/usr/local/bin/after-vpn-start.sh $4"
