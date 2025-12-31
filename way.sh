#!/bin/bash

echo "Select Waydroid display mode:"
echo "1) Mobile"
echo "2) PC Windowed"

read -p "Enter your choice [1-2]: " choice

case "$choice" in
  1)
    echo "Setting to Mobile mode..."
    waydroid prop set persist.waydroid.width 506
    waydroid prop set persist.waydroid.height 900
    echo "Mobile mode activated"
    ;;
  2)
    echo "Setting to PC Windowed mode..."
    waydroid prop set persist.waydroid.width 1280
    waydroid prop set persist.waydroid.height 720
    echo "PC Windowed mode activated"
    ;;
  *)
    echo "Invalid choice."
    exit 1
    ;;
esac