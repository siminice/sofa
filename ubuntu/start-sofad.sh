#!/bin/bash

docker run -d --name sofafetch --restart unless-stopped --init --network host \
  --security-opt seccomp=unconfined -v "$HOME/sofa:/sofa:ro" sofatoken python -u /sofa/fetchd.py
