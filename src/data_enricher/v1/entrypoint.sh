#!/bin/bash

# CREDITS
# https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743#issuecomment-1969761541
function keepUpScreen() {
    echo "running keepUpScreen()"
    while true; do
        sleep 1
        if [ -z "$(pidof -x Xvfb)" ]; then
            Xvfb $DISPLAY -screen $DISPLAY 1920x1080x16 &
        fi
    done
}

export DISPLAY=:1
rm -f /tmp/.X1-lock &>/dev/null
keepUpScreen &
echo "running: $@"
exec $@
