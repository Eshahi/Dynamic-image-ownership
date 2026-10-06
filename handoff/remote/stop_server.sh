#!/bin/bash
# Stops this vast.ai instance with its own container key. GPU billing ends; the disk is kept until the owner destroys it.
V=$(command -v vastai || echo /opt/instance-tools/bin/vastai)
"$V" stop instance "$CONTAINER_ID" --api-key "$CONTAINER_API_KEY"
