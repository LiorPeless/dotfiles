#!/bin/bash

# Directory where .desktop files are located
DESKTOP_FILES="/usr/share/applications"

# Use find to list all .desktop files and grep to extract the "Name=" line
APPS=$(find "$DESKTOP_FILES" -name '*.desktop' | xargs grep -h '^Name=' | sed 's/^Name=//')

# Use fzf to select an application
SELECTED_APP=$(echo "$APPS" | fzf --prompt="Launch: " --height=60% --border --reverse)

# If an application was selected, find its corresponding .desktop file and execute it
if [ -n "$SELECTED_APP" ]; then
    APP_PATH=$(grep -l "Name=$SELECTED_APP" "$DESKTOP_FILES"/*.desktop)
    EXEC_CMD=$(grep '^Exec=' "$APP_PATH" | head -n 1 | sed 's/^Exec=//;s/%.//')
    eval "$EXEC_CMD" &
fi

