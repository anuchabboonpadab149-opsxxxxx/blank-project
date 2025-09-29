#!/usr/bin/env bash
set -euo pipefail

# Check for k3d
if ! command -v k3d >/dev/null 2>&1; then
  echo "k3d is not installed. Install from: https://k3d.io/"
  exit 1
fi

CLUSTER_NAME=${CLUSTER_NAME:-fortune}

echo "Creating k3d cluster '$CLUSTER_NAME' with 1 server and 2 agents..."
k3d cluster create "$CLUSTER_NAME" \
  --servers 1 --agents 2 \
  --port "80:80@loadbalancer" \
  --port "443:443@loadbalancer" \
  --wait

echo "k3d cluster created."

echo "Installing ingress-nginx..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

echo "Waiting for ingress-nginx controller..."
kubectl -n ingress-nginx rollout status deploy/ingress-nginx-controller --timeout=180s

echo "Cluster ready.

Next steps:
1) Build images and load into k3d: scripts/build_images.sh
2) Deploy manifests:            scripts/deploy_k8s.sh
3) Map hosts:
   - Add to /etc/hosts:
     127.0.0.1 fortune.local
     127.0.0.1 api.fortune.local
4) Open: http://fortune.local and the API at http://api.fortune.local"