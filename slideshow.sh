#!/bin/bash

IMAGE_DIR="/home/fr0.gg/Desktop/img"
SLIDESHOW_DELAY=15 # Time in seconds to refresh the slideshow

# Start feh slideshow
feh --quiet --recursive --reload $SLIDESHOW_DELAY --fullscreen --hide-pointer $IMAGE_DIR
