#!/usr/bin/env bash

# Exit on any error 
set -e


# Install required stuff (on WSL side)
sudo apt update -y 
sudo apt install -y python3 python3-pip 
sudo apt autoremove -y 

# Install pip-tools (on WSL side)
python3 -m pip install --root-user-action=ignore --quiet --upgrade pip-tools


# Resolve directories
: '
    Relative path breaks, when we run this script from a different parent directory 
    Hence, safest is to stick with absolute paths 
    So that script can be run from anywhere
'
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.." # One directory higher 
REQ_DIR="${PROJECT_ROOT}/.requirements" 
IN_FILE="${REQ_DIR}/requirements.in"
OUT_FILE="${REQ_DIR}/requirements.txt"


# Generate full requirements
python3 -m piptools compile "$IN_FILE" \
        --strip-extras \
        --output-file "$OUT_FILE"


# Remove all auto-generated comments
tmp="$(mktemp)" # Creates a uniquely named temp file
grep -vE '^[[:space:]]*#' "$OUT_FILE" > "$tmp"


# Add user-friendly comments at the top
{
  echo "# Project full dependencies (with versions)"
  echo $'# Generated by pip-compile --strip-extras requirements.in\n'
  cat "$tmp"
} > "$OUT_FILE"
