#!/bin/bash


cd /etc/openvpn
/usr/sbin/openvpn --config /ovpn.conf --script-security 2 --up "/usr/local/bin/after-vpn-start.sh $1"
