import json
import os
import time
import threading
import socket
from typing import Generator, List, Dict

from flask import Flask, Response, jsonify, render_template, render_template_string, send_from_directory, request

import realtime_bus as bus

# Support PaaS environments (Heroku/Render/Railway) that pass PORT
WEB_PORT = int(os.getenv("PORT", os.getenv("WEB_PORT", "8000")))

# Minimal inline template to avoid external files
INDEX_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <title>Real-time Content Export Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans', 'Helvetica Neue', Arial, 'Noto Color Emoji', 'Noto Emoji', sans-serif; margin: 0; padding: 0; background: #111; color: #eee; }
    header { padding: 16px 24px; background: #181818; position: sticky; top: 0; border-bottom: 1px solid #2a2a2a; }
    h1 { margin: 0; font-size: 20px; }
    .stats { display: flex; gap: 16px; margin-top: 8px; font-size: 14px; color: #bbb; }
    .wrap { padding: 16px 24px; }
    .grid { display: grid; grid-template-columns: 1fr 360px; gap: 16px; }
    .panel { background: #181818; border: 1px solid #2a2a2a; border-radius: 10px; padding: 12px; }
    #events { max-height: calc(100vh - 260px); overflow: auto; }
    .e { border-bottom: 1px dashed #2f2f2f; padding: 10px 4px; }
    .e:last-child { border-bottom: 0; }
    .time { color: #aaa; font-size: 12px; }
    .text { font-size: 15px; margin: 6px 0; color: #f3f3f3; }
    .media a { color: #85d0ff; text-decoration: none; margin-right: 10px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #262626; color: #ddd; font-size: 12px; margin-right: 6px; }
    label { display: block; font-size: 12px; color: #bbb; margin-top: 8px; }
    input[type="text"], input[type="number"], select, textarea { width: 100%; background: #121212; border: 1px solid #2a2a2a; color: #eaeaea; border-radius: 6px; padding: 6px 8px; }
    textarea { min-height: 60px; }
    .btn { display: inline-block; background: #2a6bff; color: #fff; border: 0; padding: 6px 10px; border-radius: 6px; cursor: pointer; margin-top: 8px; margin-right: 6px; }
    .btn.alt { background: #444; }
    small { color: #888; }
  </style>
</head>
<body>
  <header>
    <h1>Real-time Content Export Dashboard</h1>
    <div class="stats">
      <div>Status: <span id="status">Connecting...</span></div>
      <div>Total events: <span id="count">0</span></div>
      <div>Last update: <span id="last">-</span></div>
      <div>Providers: <span id="providers"></span></div>
    </div>
  </header>
  <div class="wrap">
    <div class="grid">
      <div class="panel" id="events"></div>
      <div class="panel">
        <div style="font-weight: 600; margin-bottom: 6px;">Latest Media</div>
        <div id="latest-media"></div>
        <hr style="border-color:#2a2a2a; margin:12px 0;">
        <div style="font-weight: 600; margin-bottom: 6px;">Settings</div>
        <label>Post interval (seconds)</label>
        <input id="postInterval" type="number" min="1" placeholder="1" />
        <label>Collect interval (minutes)</label>
        <input id="collectInterval" type="number" min="1" placeholder="1" />
        <label>Providers (comma-separated)</label>
        <input id="providersInput" type="text" placeholder="twitter,facebook,..." />
        <label>Sender name</label>
        <input id="senderName" type="text" placeholder="จัสมิน" />
        <label>TTS language</label>
        <input id="ttsLang" type="text" placeholder="th" />
        <label>Content mode</label>
        <select id="contentMode">
          <option value="">auto</option>
          <option value="generate">generate</option>
          <option value="file">file</option>
          <option value="import">import</option>
        </select>
        <div style="margin-top:6px;">
          <button class="btn" id="saveCfg">Save</button>
          <button class="btn alt" id="reloadSch">Reload schedule</button>
          <button class="btn" id="postNow">Post now</button>
        </div>
        <hr style="border-color:#2a2a2a; margin:12px 0;">
        <div style="font-weight: 600; margin-bottom: 6px;">Add line to tweets.txt</div>
        <textarea id="newLine" placeholder="พิมพ์บรรทัดคอนเทนต์ที่ต้องการเพิ่ม..."></textarea>
        <button class="btn" id="addLine">Append</button>
        <div id="msg" style="margin-top:6px; font-size:12px; color:#9ad;"></div>
      </div>
    </div>
  </div>

  <script>
    const eventsEl = document.getElementById('events');
    const statusEl = document.getElementById('status');
    const countEl = document.getElementById('count');
    const lastEl = document.getElementById('last');
    const providersEl = document.getElementById('providers');
    const latestMediaEl = document.getElementById('latest-media');

    let count = 0;
    function fmtTs(ts) {
      const d = new Date(ts * 1000);
      return d.toLocaleString();
    }

    function addEvent(ev) {
      count++;
      countEl.textContent = count;
      lastEl.textContent = fmtTs(ev.ts || (Date.now()/1000));

      if (ev.type === 'post') {
        if (ev.providers && Array.isArray(ev.providers)) {
          providersEl.textContent = ev.providers.map(p => p.provider + ':' + p.status).join(', ');
        }
        const div = document.createElement('div');
        div.className = 'e';
        const hdr = document.createElement('div');
        hdr.innerHTML = '<span class="badge">POST</span> <span class="time">' + fmtTs(ev.ts) + '</span>';
        const body = document.createElement('div');
        body.className = 'text';
        body.textContent = ev.text || '';
        const media = document.createElement('div');
        media.className = 'media';
        if (ev.media) {
          if (ev.media.audio) media.innerHTML += '<a href="/media/' + ev.media.audio.replace(/^outputs\\//, '') + '" target="_blank">audio</a>';
          if (ev.media.image) media.innerHTML += '<a href="/media/' + ev.media.image.replace(/^outputs\\//, '') + '" target="_blank">image</a>';
          if (ev.media.video) media.innerHTML += '<a href="/media/' + ev.media.video.replace(/^outputs\\//, '') + '" target="_blank">video</a>';
          latestMediaEl.innerHTML = media.innerHTML;
        }
        div.appendChild(hdr);
        div.appendChild(body);
        div.appendChild(media);
        eventsEl.prepend(div);
      } else if (ev.type === 'collect') {
        const div = document.createElement('div');
        div.className = 'e';
        const hdr = document.createElement('div');
        hdr.innerHTML = '<span class="badge">COLLECT</span> <span class="time">' + fmtTs(ev.ts) + '</span>';
        const body = document.createElement('div');
        body.className = 'text';
        body.textContent = 'Metrics collected (' + (ev.organic_count || 0) + ' items; ads: ' + (ev.ads_status || '-') + ')';
        div.appendChild(hdr);
        div.appendChild(body);
        eventsEl.prepend(div);
      }
    }

    function connect() {
      statusEl.textContent = 'Connecting...';
      const es = new EventSource('/events');
      es.onopen = () => { statusEl.textContent = 'Connected'; };
      es.onerror = () => { statusEl.textContent = 'Reconnecting...'; };
      es.onmessage = (e) => {
        if (!e.data) return;
        try {
          const ev = JSON.parse(e.data);
          if (ev.type === 'keepalive') return;
          addEvent(ev);
        } catch (err) {}
      };
    }

    // Load initial recent events
    fetch('/api/recent').then(r => r.json()).then(list => {
      list.forEach(addEvent);
      connect();
    });
  </script>
</body>
</html>
"""

app = Flask(__name__)


@app.get("/")
def index():
    # Prefer template file if available; fallback to inline HTML.
    try:
        return render_template("index.html")
    except Exception:
        return render_template_string(INDEX_HTML)


@app.get("/about")
def about():
    return render_template("about.html")


def _list_media(limit: int = 24) -> List[Dict]:
    base = "outputs"
    imgs_dir = os.path.join(base, "images")
    vids_dir = os.path.join(base, "video")
    items: List[Dict] = []
    try:
        for p in (os.listdir(imgs_dir) if os.path.exists(imgs_dir) else []):
            full = os.path.join(imgs_dir, p)
            if os.path.isfile(full):
                items.append({"type": "image", "name": p, "path": f"images/{p}", "ts": os.path.getmtime(full)})
    except Exception:
        pass
    try:
        for p in (os.listdir(vids_dir) if os.path.exists(vids_dir) else []):
            full = os.path.join(vids_dir, p)
            if os.path.isfile(full):
                items.append({"type": "video", "name": p, "path": f"video/{p}", "ts": os.path.getmtime(full)})
    except Exception:
        pass
    items.sort(key=lambda x: x["ts"], reverse=True)
    return items[:limit]


@app.get("/gallery")
def gallery():
    media = _list_media(48)
    return render_template("gallery.html", media=media)


@app.get("/status")
def status_page():
    try:
        import config_store
        cfg = config_store.get_config()
    except Exception:
        cfg = {}
    recent = bus.recent(20)
    return render_template("status.html", cfg=cfg, recent=recent)


@app.get("/nodes")
def nodes_page():
    try:
        import node_registry as nr
        nodes = nr.list_nodes()
    except Exception:
        nodes = []
    return render_template("nodes.html", nodes=nodes)


@app.get("/api/nodes")
def api_nodes():
    try:
        import node_registry as nr
        return jsonify(nr.list_nodes())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/recent")
def api_recent():
    return jsonify(bus.recent(100))


@app.get("/api/feed")
def api_feed():
    # Return last 200 events for compatibility
    return jsonify(bus.recent(200))


@app.get("/api/latest")
def api_latest():
    # Return the latest post event if available, else the latest event
    events = bus.recent(50)
    latest_post = None
    latest_any = events[-1] if events else {}
    for ev in reversed(events):
        if ev.get("type") == "post":
            latest_post = ev
            break
    return jsonify(latest_post or latest_any)


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


@app.get("/events")
def events() -> Response:
    def gen() -> Generator[str, None, None]:
        for ev in bus.stream():
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
    return Response(gen(), mimetype="text/event-stream")


@app.get("/media/<path:subpath>")
def media(subpath: str):
    # subpath is relative to outputs/
    base = "outputs"
    directory = base
    # security: prevent path traversal
    subpath = subpath.replace("..", "").lstrip("/")
    return send_from_directory(directory, subpath, as_attachment=False)


@app.get("/api/config")
def api_get_config():
    try:
        import config_store
        return jsonify(config_store.get_config())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/config")
def api_set_config():
    try:
        patch = request.get_json(force=True, silent=True) or {}
        import config_store
        cfg = config_store.update_config(patch)
        # Optionally reschedule if intervals provided
        try:
            import scheduler_control
            scheduler_control.reschedule(
                post_interval_seconds=cfg.get("post_interval_seconds"),
                collect_interval_minutes=cfg.get("collect_interval_minutes"),
            )
        except Exception:
            pass
        return jsonify(cfg)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/reload-schedule")
def api_reload_schedule():
    try:
        import config_store
        import scheduler_control
        cfg = config_store.get_config()
        ok = scheduler_control.reschedule(
            post_interval_seconds=cfg.get("post_interval_seconds"),
            collect_interval_minutes=cfg.get("collect_interval_minutes"),
        )
        return jsonify({"ok": bool(ok)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/post-now")
def api_post_now():
    try:
        import scheduler_control
        ok = scheduler_control.trigger_post_now()
        return jsonify({"ok": bool(ok)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/tweets")
def api_tweets_list():
    try:
        from promote_ayutthaya import Config
        path = None
        try:
            import config_store
            path = config_store.get("tweets_file")
        except Exception:
            pass
        path = path or Config().TWEETS_FILE or "tweets.txt"
        lines = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    t = line.strip()
                    if t:
                        lines.append(t)
        return jsonify({"path": path, "count": len(lines), "lines": lines[:100]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/tweets")
def api_tweets_append():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        line = str(payload.get("line", "")).strip()
        if not line:
            return jsonify({"error": "line is required"}), 400
        from promote_ayutthaya import Config
        path = None
        try:
            import config_store
            path = config_store.get("tweets_file")
        except Exception:
            pass
        path = path or Config().TWEETS_FILE or "tweets.txt"
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        return jsonify({"ok": True, "path": path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _start_node_heartbeat():
    try:
        import node_registry as nr
    except Exception:
        return
    node_id = nr.node_id_default()
    try:
        nr.register(node_id, role="web+worker", extra={"host": socket.gethostname()})
    except Exception:
        pass

    def loop():
        while True:
            try:
                nr.heartbeat(node_id)
            except Exception:
                pass
            time.sleep(10)

    t = threading.Thread(target=loop, name="node-heartbeat", daemon=True)
    t.start()


def start_web():
    _start_node_heartbeat()
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)