#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess


def buildStartCommand(
    prefix="ovpnpf",
    name=None,
    localAddress=None,
    remoteAddress=None,
    configPath=None,
    daemon=False,
    repoName="neoatlantis/openvpn-port-forwarding"
):
    if not name: name = os.urandom(6).hex()
    dockerName = "%s-%s" % (prefix, name)
    
    arguments = [
        "--rm",                     # remove container on exit
        "--tty",
        "--interactive",
        "--device=/dev/net/tun",
        "--name=%s" % dockerName,
        "--cap-add=NET_ADMIN",
        "--publish", "%s:1984" % localAddress,
        "--volume", """/etc/openvpn:/etc/openvpn/:ro""",
        "--volume", """%s:/ovpn.conf:ro""" % os.path.realpath(configPath),
        "--sysctl", "net.ipv6.conf.all.disable_ipv6=1",
    ]
    if daemon:
        arguments.append("-d")
    return ["docker", "run"] + arguments + [repoName] + [
        # following arguments are passed to ./boot-vpn.sh over "docker run" cmd
        "60",         # --inactive  $1
        "10",           # --ping      $2
        "30",           # --ping-exit $3
        remoteAddress   # --up "/usr/local/bin/after-vpn-start.sh $4"
    ]


parser = argparse.ArgumentParser()

parser.add_argument(
    "CONFIG_PATH", help="Specify the configure file.")

parser.add_argument(
    "LOCAL_ADDRESS", help="The source host:port which will be forwarded.")

parser.add_argument(
    "DEST_ADDRESS", help="The host:port you want to connect via VPN.")

parser.add_argument(
    "--debug-repo", default="neoatlantis/openvpn-port-forwarding",
    help="""Specify another repo name other than default.
    Ignore this if you don't know what it means."""
)

parser.add_argument(
    "--name", "-n", help="Give the new docker instance a name.")

parser.add_argument(
    "--daemon", "-d", default=False, action="store_true",
    help="Use this flag to make new instance run as a daemon in background.")

args = parser.parse_args()

if not os.path.isfile(args.CONFIG_PATH):
    print("Error: configure file %s does not exist." % args.CONFIG_PATH)
    exit(1)

command = buildStartCommand(
    name=args.name, 
    localAddress=args.LOCAL_ADDRESS,
    remoteAddress=args.DEST_ADDRESS,
    configPath=args.CONFIG_PATH,
    daemon=args.daemon,
    repoName=None if not args.debug_repo else args.debug_repo
)

print(" ".join(command))

subprocess.check_output(command)
