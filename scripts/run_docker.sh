#!/bin/bash

docker build -t tmp-delta-debugging . && docker run --rm -it tmp-delta-debugging
docker image rm -f tmp-delta-debugging
