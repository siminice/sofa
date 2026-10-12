#!/bin/bash
# Opens a separate Chrome window the server can fetch through, and keeps the tunnel up.
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-sofa" --no-first-run \
  https://www.sofascore.com/ >/dev/null 2>&1 &
sleep 3
echo "Bridge open. Leave this running while the server scrapes; Ctrl-C to stop."
caffeinate -i ssh -N -R 9222:localhost:9222 radu@67.166.164.112
