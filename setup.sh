#!/bin/bash

# Colors
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_mpv() {
  if command_exists mpv; then
    echo -e "${GREEN}[•] MPV is already installed.${NC}"
    return 0
  fi

  echo -e "${BLUE}[•] Installing mpv...${NC}"
  if command_exists pkg; then
    pkg update -y && pkg install -y mpv
  elif command_exists apt; then
    sudo apt update && sudo apt install -y mpv
  elif command_exists dnf; then
    sudo dnf install -y mpv
  elif command_exists pacman; then
    sudo pacman -Sy --noconfirm mpv
  elif command_exists brew; then
    brew install mpv
  else
    echo -e "${RED}[•] No supported package manager found to install mpv!!!${NC}"
    return 1
  fi
}

install_requirements() {
  if [ -f requirements.txt ]; then
    echo -e "${BLUE}[•] Installing requirements.txt...${NC}"
    python3 -m pip install -r requirements.txt
  else
    echo -e "${RED}[•] requirements.txt not found!!!${NC}"
  fi
}

install_mpv

if ! command_exists mpv; then
  echo -e "${RED}[!] Failed to install mpv. Aborting setup.${NC}"
  exit 1
fi

install_requirements

chmod +x main.py

echo -e "${ORANGE}Now Run ./main.py${NC}"
