#!/bin/bash
# deploy.sh - this script runs ON THE APP SERVER (Jenkins starts it over SSH).
# Usage: bash deploy.sh <image-with-tag> <aws-region> <ecr-registry>
set -euo pipefail
 
IMAGE="$1"
REGION="$2"
REGISTRY="$3"
 
cd /home/ubuntu/app
 
echo ">>> Logging in to Amazon ECR"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"
 
echo ">>> Pulling the new image: $IMAGE"
export IMAGE
docker compose pull app
 
echo ">>> Starting / updating the containers"
docker compose up -d --remove-orphans
 
echo ">>> Removing old unused images"
docker image prune -f
 
echo ">>> Running containers:"
docker compose ps
