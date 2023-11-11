#!/bin/bash
ffmpeg -i "$1" -acodec mp3 data/taxi.mp3 -y -loglevel warning