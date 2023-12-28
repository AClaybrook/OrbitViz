#!/bin/bash
# Check for sudo privileges
if [ $(id -u) -ne 0 ]; then
    HAS_SUDO=0
else
    HAS_SUDO=1
fi



# Apt get update
if [ "$HAS_SUDO" -eq 1 ]; then
    sudo apt-get update
    sudo apt install make
else
    echo "You don't have sudo privileges, skipping sudo commands"
    echo "To manually perform this action, run: sudo apt-get update"
    echo "To manually perform this action, run: sudo apt install make"
fi

# Other setup tasks...

# Apply custom cron jobs

# Other setup tasks...
