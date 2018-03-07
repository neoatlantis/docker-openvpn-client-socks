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

from start_single import buildStartCommand

_BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
LOCALPATH = lambda *i: os.path.join(_BASEPATH, *i)
CACHE_TIME = 7200


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

    dockerName = "vpngate-%s" % os.urandom(16).hex()

    cmd = buildStartCommand(
        name=dockerName,
        configPath=tempconfig.name,
        daemon=False,
        socks5Entry="0.0.0.0:1080"
    )

    print(" ".join(cmd))

    p = subprocess.Popen(cmd)
    pid = p.pid

    try:
        p.wait()
    except:
        subprocess.run(["docker", "container", "kill", dockerName])
        p.terminate()
        try:
            os.kill(pid, signal.SIGKILL)
            p.kill()
            print("Docker killed.")
        except:
            print("Docker terminated.")
