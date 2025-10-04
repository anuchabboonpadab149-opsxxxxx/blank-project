import json
import os
from typing import Generator

from flask import Flask, Response, jsonify, render_template_string, send_from_directory, request

import realtime_bus as bus

WEB_PORT = int(os.getenv("WEB_PORT", "8000"))

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
    .grid { display: grid; grid-template-columns: 1fr 320px; gap: 16px; }
    .panel { background: #181818; border: 1px solid #2a2a2a; border-radius: 10px; padding: 12px; }
    #events { max-height: calc(100vh - 160px); overflow: auto; }
    .e { border-bottom: 1px dashed #2f2f2f; padding: 10px 4px; }
    .e:last-child { border-bottom: 0; }
    .time { color: #aaa; font-size: 12px; }
    .text { font-size: 15px; margin: 6px 0; color: #f3f3f3; }
    .media a { color: #85d0ff; text-decoration: none; margin-right: 10px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #262626; color: #ddd; font-size: 12px; margin-right: 6px; }
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
    return render_template_string(INDEX_HTML)


@app.get("/api/recent")
def api_recent():
    return jsonify(bus.recent(100))


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


def start_web():
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)