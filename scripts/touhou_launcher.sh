#!/bin/bash

# Define path to directory where all game's directories are:
games_dir_path="$HOME/.wine/drive_c/Program Files/Touhou/"

# Change to the games directory:
cd "$games_dir_path" || { echo "Failed to change directory to $games_dir_path"; exit 1; }
pwd

# List all directories in path and let user choose using fzf:
choice=$(find . -maxdepth 1 -type d -not -path '.' | fzf --height 60% --border --ansi --preview "cat {}/des.md 2> /dev/null | sed 's/^#/\x1b[31m&#\x1b[0m/' | fold -s || echo 'No des.md file found'")

# Check if user made a choice
if [ -z "$choice" ]; then
  echo "No directory chosen. Exiting."
    exit 1
fi

# Remove leading './' from the choice
choice="${choice#./}"

# Change to the chosen directory:
cd "$choice" || { echo "Failed to change directory to $choice"; exit 1; }

# Run the vpatch.exe file using wine:
wine vpatch.exe

