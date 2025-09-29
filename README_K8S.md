# Kubernetes Turnkey (Creates Nodes via k3d)

This guide lets you run the full stack (web + gateway + credit + payment + fortune) locally on a Kubernetes cluster with real "nodes" using k3d.

## Prerequisites
- Docker
- k3d (https://k3d.io/)
- kubectl

## 1) Create the cluster (nodes)
```
scripts/provision_k3d.sh
```
This creates a cluster (1 server, 2 agents), installs ingress-nginx, and maps ports 80/443.

## 2) Build & load images into the cluster
```
scripts/build_images.sh
```

## 3) Deploy manifests
```
scripts/deploy_k8s.sh
```

This applies:
- Namespace, Secrets, ConfigMap
- Deployments & Services (web, gateway, credit, payment, fortune)
- Ingress routes:
  - Web: fortune.local -> web service
  - API: api.fortune.local -> gateway service

Add hosts:
```
127.0.0.1 fortune.local
127.0.0.1 api.fortune.local
```

## 4) Open
- Web: http://fortune.local
- API: http://api.fortune.local/healthz

## Environment & Secrets
Defaults are included in `k8s/secret.yaml` and `k8s/configmap.yaml` for convenience in local dev.
Change before production:
- ADMIN_TOKEN, JWT_SECRET, INTERNAL_TOKEN
- PROMPTPAY_ID

## Notes
- Payment QR will work through the gateway; PUBLIC_BASE_URL is set to `http://payment:8002` inside the cluster.
- For Production, use the Render blueprint in `deploy/render.yaml` or your own k8s cluster with a proper registry and ingress.