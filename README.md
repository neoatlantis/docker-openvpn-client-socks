# OpenVPN backboned Port Forwarder

This is a docker image of an OpenVPN client tied to a port forwarder. It is
useful to isolate network changes (so the host is not affected by the modified
routing).

## Usage

Preferably, using `start` in this repository:

```bash
./start /path/to/openvpn/config/file TARGET_ADDR:TARGET_PORT
```

You have to specify a single OpenVPN config file containing all necessary
items. References to other files cannot be resolved.

Alternatively, using `docker run` directly:

```bash
docker run --rm --tty --interactive \
--device=/dev/net/tun \
--name=openvpn-client \
--cap-add=NET_ADMIN \
--publish <TARGET_ADDR>:<TARGET_PORT>:1984 \  # change this
--volume "/etc/openvpn:/etc/openvpn/:ro" \
--volume "<ABSOLUTE PATH TO OPENVPN CONFIG FILE>:/ovpn.conf:ro" \ # change this too
--sysctl net.ipv6.conf.all.disable_ipv6=1 \
neoatlantis/openvpn-port-forwarding
```
