#!/usr/bin/env bash

swww-daemon -n "wp-front" &
swww-daemon -n "wp-back"  &

# Blur the image
convert -blur 0x25 "$@" /tmp/blurred-wallpaper.jpg

swww img /tmp/blurred-wallpaper.jpg -n "wp-back"
swww img "$@" -n "wp-front"
