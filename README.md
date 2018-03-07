# OpenVPN backboned Port Forwarder

This is a docker image of an OpenVPN client tied to a port forwarder. It is
useful to isolate network changes (so the host is not affected by the modified
routing).

## Usage

You have to specify a single OpenVPN config file containing all necessary
items. References to other files cannot be resolved.

Then, use

```bash
./start_single.py /path/to/openvpn/config/file -s5 1080 -pf 1090:REMOTE_ADDR:REMOTE_PORT
```

to start a new docker container. `-s5` or `--socks5` option, will enable the
SOCKS5 proxy access from host, where as `-pf` or `--port-forwarding` enables a
single port forwarding connection. At least one of these options must be
specified.
