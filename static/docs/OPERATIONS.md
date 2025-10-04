# Operations Playbook

This playbook covers common operations, runbooks, and tips for running the Jasmine x Salmon autonomous system.

---

## Bring-up

Start the stack:
```bash
docker compose up -d --build
```

Check health:
```bash
curl http://localhost:8000/healthz
```

Live events:
```bash
curl -N http://localhost:8000/events
```

---

## Credentials Injection

Use the UI:
- Open `/credentials`, paste provider keys, Save.

Or API:
```bash
curl -X POST http://localhost:8000/api/credentials \
  -H "Content-Type: application/json" \
  -d @your-credentials.json
```

Verify (masked):
```bash
curl http://localhost:8000/api/credentials
```

---

## Reschedule at Runtime

Change intervals/providers:
```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"post_interval_seconds": 10, "providers": ["twitter","facebook"]}'
```

Reload scheduler:
```bash
curl -X POST http://localhost:8000/api/reload-schedule
```

Trigger an immediate post:
```bash
curl -X POST http://localhost:8000/api/post-now
```

---

## Logs and Files

- Docker logs:
  ```
  docker compose logs -f
  ```
- Outputs:
  - `outputs/audio/*.mp3`
  - `outputs/images/*.png`
  - `outputs/video/*.mp4`
  - `outputs/events.jsonl`

---

## Troubleshooting

- Health failing:
  - Ensure container is up: `docker compose ps`
  - Review logs: `docker compose logs -f`
- Posts not appearing:
  - Check `/events` and `/api/feed`
  - Verify credentials at `/credentials`
  - Check CB states at `/api/circuit-states`
- Mixed Content (HTTPS front, HTTP backend):
  - Open backend via LAN (http://LAN_IP:8000)
  - Or add HTTPS to backend (reverse proxy)
- Rate limits:
  - Increase `POST_INTERVAL_SECONDS` (e.g., 10–30s)
  - Circuit breaker will reduce immediate failures

---

## Backup

- Back up `credentials.json`, `runtime_config.json`, `nodes_registry.json`, and `outputs/events.jsonl` regularly.
- Do not commit secrets into the repository.