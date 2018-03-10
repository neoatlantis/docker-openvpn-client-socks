#!/usr/bin/env python3

import requests
import time
import os
import sys
import re
import base64
import random
import tempfile
import subprocess
import hashlib

# TODO: detect connectivity in this script instead of docker inside.

from start_single import buildStartCommand



_BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
LOCALPATH = lambda *i: os.path.join(_BASEPATH, *i)
CACHE_TIME = 7200
TIMEOUT = 30
INTERVAL = 10


if len(sys.argv) < 2:
    print("Usage: python3 vpngate.py [<LOCAL_ADDR>:]<LOCAL_PORT>")
    exit(1)

PROXY = sys.argv[1]
if ":" not in PROXY:
    PROXY = "127.0.0.1:" + PROXY

##############################################################################

def testConnectivity(proxy):
    global TIMEOUT
    try:
        subprocess.check_output([
            "curl",
            "--proxy", "socks5h://%s" % proxy,
            "--max-time", str(TIMEOUT),
            "--head",
            "--silent",
            "www.google.com"
        ])
        return True
    except FileNotFoundError:
        print("Install `curl` for testing connectivity.")
        exit(1)
    except:
        return False

def getName(target):
    return "vpngate-" + \
        base64.b32encode(\
            hashlib.sha512(target.encode('utf-8')).digest()[:12]
        ).decode('ascii').rstrip("=")

def getList():
    global CACHE_TIME

    cache = LOCALPATH("vpngate.cache")
    try:
        mtime = os.path.getmtime(cache)
        now = time.time()
        if now - mtime < CACHE_TIME:
            return open(cache, 'r').read()
    except:
        pass

    URL = "http://www.vpngate.net/api/iphone/"
    r = requests.get(URL)
    if r.status_code != 200:
        print("Failed fetching newest VPNGate list.")
        return None

    open(cache, "wb+").write(r.content)
    return r.text 

def read(l):
    lb = l.split(",")
    try:
        HostName, IP ,Score, Ping, Speed, CountryLong, CountryShort,\
        NumVpnSessions, Uptime, TotalUsers, TotalTraffic, LogType, \
        Operator, Message, OpenVPN_ConfigData_Base64 = lb
        return {
            "hostname": HostName,
            "ip": IP,
            "score": int(Score),
            "ping": int(Ping),
            "speed": int(Speed),
            "ovpn": base64.b64decode(OpenVPN_ConfigData_Base64),
        }
    except:
        return None

def killDocker(name):
    print("Try to kill and remove docker container [%s]." % name)
    try:
        subprocess.run(["docker", "container", "kill", name])
    except Exception as e:
        print(e)
    try:
        subprocess.run(["docker", "container", "rm", name])
    except Exception as e:
        print(e)


##############################################################################

# Get available VPNGate providers

items = [read(l) for l in getList().split("\n")[2:] if len(l) > 1000]
items = sorted([i for i in items if i], key=lambda e: e["score"])

# Pick a server. The probability of a server being choosen is proportional
# to it's score: higher scores are favoured.

sumScores = sum([each["score"] for each in items])
pickPlace = random.randrange(0, sumScores)
pickSum = 0
for picked in items:
    pickSum += picked["score"]
    if pickSum >= pickPlace:
        break

# Create a temp file and start OVPN

with tempfile.NamedTemporaryFile(mode="wb+", delete=True) as tempconfig:
    tempconfig.write(picked["ovpn"])
    tempconfig.flush()

    dockerName = getName(PROXY)

    killDocker(dockerName) # if any docker exists, kill that first

    cmd = buildStartCommand(
        name=dockerName,
        configPath=tempconfig.name,
        daemon=False,
        socks5Entry=PROXY,
        inactive=TIMEOUT
    )

    print(" ".join(cmd))

    p = subprocess.Popen(cmd)
    pid = p.pid

    try:
        # test connectivity of this VPNGATE
        count = 0
        last = time.time()
        while True:
            if not testConnectivity(PROXY):
                print("Warning: seems no internet.")
                count += time.time() - last
            else:
                count = 0
            last = time.time()
            if count > TIMEOUT:
                break
            time.sleep(INTERVAL)

    finally:
        killDocker(dockerName)
        p.terminate()
        try:
            os.kill(pid, signal.SIGKILL)
            p.kill()
            print("Docker killed.")
        except:
            print("Docker terminated.")
