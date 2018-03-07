#!/usr/bin/env python

import subprocess
import sys
import time
try:
    import httplib
except:
    import http.client as httplib

def test():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def kill():
    subprocess.call(["killall", "openvpn"])


count = 0
timeout = int(sys.argv[1])
last = time.time()
interval = 10 

while True:
    if not test():
        print "Warning: seems no internet."
        count += time.time() - last
    else:
        count = 0
    last = time.time()
    if count > timeout:
        kill()
        exit()
    time.sleep(interval)

