# Architecture — Jasmine x Salmon Autonomous System

This document provides a deeper look at the architecture, data flow, and modules in the project.

---

## High-level Overview

Components:
- Web App (Flask)
  - HTTP APIs
  - SSE event stream
  - Credentials UI and runtime config
  - Nodes/Workflows/Metrics pages
- Scheduler (APScheduler)
  - Posting job
  - Collecting job (organic + ads)
- Content/Media Pipeline
  - Text generator (persona)
  - Audio (gTTS)
  - Image (Pillow, Thai fonts)
  - Video (moviepy, ffmpeg)
- Dispatcher Layer
  - Providers with Circuit Breaker + retry backoff
  - Optional simulation
- State Stores
  - JSONL events feed (outputs/events.jsonl)
  - Credentials (credentials.json)
  - Runtime config (runtime_config.json)
  - Nodes registry (nodes_registry.json)

---

## Module Map

- `cli.py`:
  - Loads env & credentials
  - Starts web dashboard in a background thread (when `WEB_DASHBOARD=true`)
  - Defines `post_job()` and `collect_job()`
  - Registers jobs on APScheduler (interval/cron)
  - Sends SSE events via `realtime_bus.publish()`

- `web_dashboard.py`:
  - Flask app with routes for:
    - `/` dashboard (index)
    - `/events` SSE stream
    - `/api/recent`, `/api/feed`, `/api/latest`
    - `/api/config`, `/api/reload-schedule`, `/api/post-now`
    - `/api/credentials`
    - `/api/metrics`, `/api/circuit-states`
    - `/api/nodes*`
    - `/healthz`
  - CORS relaxed to allow static front-ends to consume backend

- `realtime_bus.py`:
  - In-memory queue + JSONL persistence
  - `publish(event)` used across app
  - `/events` consumes this bus

- `content_generator.py`:
  - Runtime persona selection; defaults to “Jasmine x Salmon”
  - Allows overrides via config store

- `media_generator.py`:
  - gTTS voice generation (Thai)
  - Pillow quote-card image with Thai fonts
  - moviepy to mux audio + image into short video

- `social_dispatcher.py`:
  - Wraps all providers with Circuit Breaker
  - Calls each provider in a controlled way
  - Simulation hooks (`SIMULATE_*`) to avoid real posts when keys missing

- `circuit_breaker.py`:
  - Manages provider state machine (closed, half-open, open)
  - Exposes `should_allow()` and `on_success/on_failure()`
  - Publishes CB events for visibility

- `credentials_store.py`:
  - Reads/writes `credentials.json`
  - Applies values to `os.environ` on update
  - Masks values for readback

- `scheduler_control.py`:
  - Exposes scheduler registration + rescheduling logic
  - Provides `POST /api/reload-schedule`, trigger endpoints

- `promote_ayutthaya.py`:
  - Handles X/Twitter posting/ads utilities
  - Collects ads analytics

---

## Data Flow

1) Scheduler triggers `post_job()` every second:
   - Generate text (and media when configured)
   - Attempt to dispatch to providers
   - Publish event to SSE + JSONL

2) Scheduler triggers `collect_job()` every minute:
   - Pulls organic + ads metrics
   - Publish event to SSE + JSONL

3) Live dashboard (browser) subscribes to `/events` to render:
   - Last post
   - Providers results
   - Visitor metrics
   - Circuit breaker changes
   - Nodes heartbeats

---

## Observability

- `/events` SSE provides a live event feed
- `/api/metrics` for visitor/pageview metrics
- `/api/circuit-states` to see provider CB states
- JSONL persisted in `outputs/events.jsonl` (best-effort, non-blocking)

---

## Extending

- Add a provider: implement under `providers/` and register in `social_dispatcher.py`
- Add a new persona: extend `content_generator.py` or load via `config_store`
- Add media effects: add image/video filters in `media_generator.py`

---

## Constraints

- Posting every second may hit rate limits for certain platforms; circuit breaker + retry reduce impact. Consider raising intervals in production.
- Instagram requires images; the system auto-generates a quote card for that purpose.