#!/usr/bin/env python3

import argparse
import os
import signal
import sys
import subprocess

PREFIX="ovpnpf"

def buildStartCommand(
    name=None,
    configPath=None,
    daemon=False,
    portForwardingEntry=False,
    socks5Entry=False,
    repoName="neoatlantis/openvpn-port-forwarding",
    inactive=30 
):
    assert name != None

    if portForwardingEntry:
        portForwardingLocal, portForwardingRemote = portForwardingEntry
    else:
        portForwardingLocal, portForwardingRemote = None, None
    
    arguments = [
        "--rm",                     # remove container on exit
        "--device=/dev/net/tun",
        "--name=%s" % name,
        "--cap-add=NET_ADMIN",
        "--volume", """/etc/openvpn:/etc/openvpn/:ro""",
        "--volume", """%s:/ovpn.conf:ro""" % os.path.realpath(configPath),
        "--sysctl", "net.ipv6.conf.all.disable_ipv6=1",
    ]
    
    if daemon: arguments.append("-d")
    
    if portForwardingLocal:
        arguments += ["--publish", "%s:1984" % portForwardingLocal]
    if socks5Entry:
        arguments += ["--publish", "%s:1080" % socks5Entry]
        
    cmd = ["docker", "run"] + arguments + [repoName] + [
        # following arguments are passed to ./boot-vpn.sh over "docker run" cmd
        "%d" % inactive,          # --inactive  $1
        "5",                      # --ping      $2
        "30",                     # --ping-exit $3
    ]
    if portForwardingRemote:
        cmd += [
            portForwardingRemote  # --up "/usr/local/bin/after-vpn-start.sh $4"
        ]
    else:
        cmd += ["none"]

    return cmd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "CONFIG_PATH", help="Specify the configure file.")

    parser.add_argument(
        "--debug-repo", default="neoatlantis/openvpn-port-forwarding",
        help="""Specify another repo name other than default.
        Ignore this if you don't know what it means."""
    )

    parser.add_argument(
        "--name", "-n", help="Give the new docker instance a name.")

    parser.add_argument(
        "--daemon", "-d", default=False, action="store_true",
        help="""Use this flag to make new instance run as a daemon in
        background.""")

    action = parser.add_argument_group()

    action.add_argument(
        "--socks5", "-s5",
        help="""Specify a SOCKS5 proxy entry point. Traffic will be proxied
        using VPN."""
    )

    action.add_argument(
        "--port-forwarding", "-pf",
        help="""Specify in format <SRC_ADDR>:<SRC_PORT>:<DEST_ADDR>:<DEST_PORT>
        to enable port forwarding."""
    )


    args = parser.parse_args()

    if not os.path.isfile(args.CONFIG_PATH):
        print("Error: configure file %s does not exist." % args.CONFIG_PATH)
        exit(1)

    if not args.socks5 and not args.port_forwarding:
        print("Error: either SOCKS5 or Port Forwarding or both must be choosen.")
        exit(1)

    if args.port_forwarding:
        pfArguments = args.port_forwarding.split(":")
        if len(pfArguments) == 3:
            pfArguments = ["0.0.0.0"] + pfArguments
        if len(pfArguments) != 4:
            print("Error: bad arguments for port forwarding.")
            exit(1)
        pfArguments = tuple(pfArguments)
        pfArguments = (
            ("%s:%s" % pfArguments[0:2]), ("%s:%s" % pfArguments[2:4]))
    else:
        pfArguments = None

    dockerName = args.name
    if not dockerName: 
        dockerName = os.urandom(6).hex()
    dockerName = "%s-%s" % (PREFIX, dockerName)


    command = buildStartCommand(
        name=dockerName,
        configPath=args.CONFIG_PATH,
        daemon=args.daemon,
        socks5Entry=args.socks5,
        portForwardingEntry=pfArguments,
        repoName=None if not args.debug_repo else args.debug_repo
    )

    print(" ".join(command))

    p = subprocess.Popen(command)
    pid = p.pid

    try:
        p.wait()
    except:
        if not args.daemon:
            subprocess.run(["docker", "container", "kill", dockerName])
            p.terminate()
            try:
                os.kill(pid, signal.SIGKILL)
                p.kill()
                print("Docker killed.")
            except:
                print("Docker terminated.")
