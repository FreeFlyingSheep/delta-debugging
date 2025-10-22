#!/bin/bash
# This script builds and runs a Docker container for delta debugging.
# It will remove the container after it exits.

docker build -t tmp-delta-debugging . && docker run --rm -it tmp-delta-debugging
