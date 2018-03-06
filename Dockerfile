# OpenVPN client + SOCKS proxy
# Usage:
# Create configuration (.ovpn), mount it in a volume
# docker run --volume=something.ovpn:/ovpn.conf:ro --device=/dev/net/tun --cap-add=NET_ADMIN
# Connect to (container):1080
# Note that the config must have embedded certs
# See `start` in same repo for more ideas

FROM alpine

COPY sockd.conf /etc/
COPY boot-vpn.sh /usr/local/bin/
COPY after-vpn-start.sh /usr/local/bin/

RUN true \
    && echo "http://dl-4.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
    && apk add --update-cache openvpn dante-server bash openresolv openrc socat \
    && rm -rf /var/cache/apk/* \
    && chmod a+x /usr/local/bin/boot-vpn.sh \
    && chmod a+x /usr/local/bin/after-vpn-start.sh \
    && true

ENTRYPOINT ["/usr/local/bin/boot-vpn.sh"]
