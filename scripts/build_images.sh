#!/usr/bin/env bash
set -euo pipefail

TAG=${TAG:-local}
CLUSTER_NAME=${CLUSTER_NAME:-fortune}

echo "Building images with tag '$TAG'..."

# Build backend services
docker build -t fortune-gateway:$TAG -f services/gateway/Dockerfile .
docker build -t fortune-credit:$TAG  -f services/credit/Dockerfile .
docker build -t fortune-payment:$TAG -f services/payment/Dockerfile .
docker build -t fortune-fortune:$TAG -f services/fortune/Dockerfile .

# Build web static
docker build -t fortune-web:$TAG -f web/Dockerfile web

echo "Importing images into k3d cluster '$CLUSTER_NAME'..."
k3d image import \
  fortune-gateway:$TAG \
  fortune-credit:$TAG \
  fortune-payment:$TAG \
  fortune-fortune:$TAG \
  fortune-web:$TAG \
  -c "$CLUSTER_NAME"

echo "All images built and imported."