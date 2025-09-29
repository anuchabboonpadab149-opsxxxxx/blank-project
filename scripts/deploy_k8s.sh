#!/usr/bin/env bash
set -euo pipefail

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/credit.yaml
kubectl apply -f k8s/payment.yaml
kubectl apply -f k8s/fortune.yaml
kubectl apply -f k8s/gateway.yaml
kubectl apply -f k8s/web.yaml
kubectl apply -f k8s/ingress.yaml

echo "Waiting for deployments..."
kubectl -n fortune rollout status deploy/credit --timeout=180s || true
kubectl -n fortune rollout status deploy/payment --timeout=180s || true
kubectl -n fortune rollout status deploy/fortune --timeout=180s || true
kubectl -n fortune rollout status deploy/gateway --timeout=180s || true
kubectl -n fortune rollout status deploy/web --timeout=180s || true

echo "Done.

Add hosts:
  127.0.0.1 fortune.local
  127.0.0.1 api.fortune.local

Open:
  - Web:  http://fortune.local
  - API:  http://api.fortune.local/healthz"