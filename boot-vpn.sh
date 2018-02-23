#!/bin/bash


cd /etc/openvpn
/usr/sbin/openvpn\
    --config /ovpn.conf\
    --script-security 2\
    --inactive $1 --ping $2 --ping-exit $3\
    --up "/usr/local/bin/after-vpn-start.sh $4"
