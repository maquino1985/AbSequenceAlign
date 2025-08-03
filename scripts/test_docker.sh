#!/bin/bash

# Option 1: Use the test script
./scripts/test_docker.sh

# Option 2: Use make commands
make docker-test

# Option 3: Build and test manually
docker-compose build
docker-compose up -d
docker-compose exec absequencealign python test_docker_internal.py
docker-compose down