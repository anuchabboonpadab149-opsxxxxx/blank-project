import json
import os
import time
from typing import Generator

from flask import Flask, Response, jsonify, render_template, render_template_string, send_from_directory, request

import realtime_bus as bus
import node_registry as nreg
import metrics_store as mstore
import circuit_breaker as cbreak
import credentials_store as credstore
import workflow_store as wstore

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
    header { padding: 16px 24px; background: #181818; position: sticky; top: 0; border-bottom: 1px solid #2a2a2a; display:flex; align-items:center; gap:16px; }
    h1 { margin: 0; font-size: 20px; }
    nav a { color:#85d0ff; text-decoration:none; margin-right:10px; font-size:14px; }
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
    <nav>
      <a href="/">Home</a>
      <a href="/about">About</a>
      <a href="/nodes">Nodes</a>
      <a href="/credentials">Credentials</a>
      <a href="/workflows">Workflows</a>
    </nav>
  </header>
  <div class="wrap">
    <div class="stats">
      <div>Status: <span id="status">Connecting...</span></div>
      <div>Total events: <span id="count">0</span></div>
      <div>Last update: <span id="last">-</span></div>
      <div>Providers: <span id="providers"></span></div>
      <div>Visitors: <span id="visitors">0</span></div>
    </div>
    <div class="grid" style="margin-top:12px;">
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
        <label>Import source URL</label>
        <input id="importUrl" type="text" placeholder="https://example.com/posts.txt" />
        <label>Import format</label>
        <select id="importFormat">
          <option value="lines">lines</option>
          <option value="json">json</option>
        </select>
        <label>Hashtags (comma-separated)</label>
        <input id="hashtagsBase" type="text" placeholder="#จัสมิน,#ความรัก,..." />
        <label>Openers (one per line)</label>
        <textarea id="openers"></textarea>
        <label>Core love lines (one per line)</label>
        <textarea id="coreLove"></textarea>
        <label>Playful addons (one per line)</label>
        <textarea id="playfulAddons"></textarea>
        <label>Light spicy (one per line)</label>
        <textarea id="lightSpicy"></textarea>
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
    const visitorsEl = document.getElementById('visitors');

    const postIntervalInput = document.getElementById('postInterval');
    const collectIntervalInput = document.getElementById('collectInterval');
    const providersInput = document.getElementById('providersInput');
    const senderInput = document.getElementById('senderName');
    const ttsLangInput = document.getElementById('ttsLang');
    const contentModeSel = document.getElementById('contentMode');
    const importUrlInput = document.getElementById('importUrl');
    const importFmtSel = document.getElementById('importFormat');
    const hashtagsBaseInput = document.getElementById('hashtagsBase');
    const openersInput = document.getElementById('openers');
    const coreLoveInput = document.getElementById('coreLove');
    const playfulAddonsInput = document.getElementById('playfulAddons');
    const lightSpicyInput = document.getElementById('lightSpicy');
    const msgEl = document.getElementById('msg');

    document.getElementById('saveCfg').onclick = async () => {
      const payload = {
        post_interval_seconds: Number(postIntervalInput.value) || null,
        collect_interval_minutes: Number(collectIntervalInput.value) || null,
        providers: providersInput.value ? providersInput.value.split(',').map(x => x.trim()).filter(Boolean) : null,
        sender_name: senderInput.value || null,
        tts_lang: ttsLangInput.value || 'th',
        content_mode: contentModeSel.value || null,
        import_source_url: importUrlInput.value || null,
        import_format: importFmtSel.value || 'lines',
        hashtags_base: hashtagsBaseInput.value ? hashtagsBaseInput.value.split(',').map(x => x.trim()).filter(Boolean) : null,
        openers: openersInput.value ? openersInput.value.split('\\n').map(x => x.trim()).filter(Boolean) : null,
        core_love: coreLoveInput.value ? coreLoveInput.value.split('\\n').map(x => x.trim()).filter(Boolean) : null,
        playful_addons: playfulAddonsInput.value ? playfulAddonsInput.value.split('\\n').map(x => x.trim()).filter(Boolean) : null,
        light_spicy: lightSpicyInput.value ? lightSpicyInput.value.split('\\n').map(x => x.trim()).filter(Boolean) : null,
      };
      const r = await fetch('/api/config', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      const data = await r.json();
      msgEl.textContent = 'Saved.';
      setTimeout(() => msgEl.textContent = '', 1500);
    };

    document.getElementById('reloadSch').onclick = async () => {
      await fetch('/api/reload-schedule', {method:'POST'});
      msgEl.textContent = 'Scheduler reloaded.';
      setTimeout(() => msgEl.textContent = '', 1500);
    };

    document.getElementById('postNow').onclick = async () => {
      await fetch('/api/post-now', {method:'POST'});
      msgEl.textContent = 'Posting initiated.';
      setTimeout(() => msgEl.textContent = '', 1500);
    };

    document.getElementById('addLine').onclick = async () => {
      const line = document.getElementById('newLine').value.trim();
      if (!line) return;
      const r = await fetch('/api/tweets', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({line})});
      const data = await r.json();
      document.getElementById('newLine').value = '';
      msgEl.textContent = 'Appended.';
      setTimeout(() => msgEl.textContent = '', 1500);
    };

    async function loadConfig() {
      const r = await fetch('/api/config');
      const cfg = await r.json();
      if (cfg.post_interval_seconds != null) postIntervalInput.value = cfg.post_interval_seconds;
      if (cfg.collect_interval_minutes != null) collectIntervalInput.value = cfg.collect_interval_minutes;
      if (Array.isArray(cfg.providers)) providersInput.value = cfg.providers.join(',');
      if (cfg.sender_name) senderInput.value = cfg.sender_name;
      if (cfg.tts_lang) ttsLangInput.value = cfg.tts_lang;
      if (cfg.content_mode) contentModeSel.value = cfg.content_mode;
      if (cfg.import_source_url) importUrlInput.value = cfg.import_source_url;
      if (cfg.import_format) importFmtSel.value = cfg.import_format;
      if (Array.isArray(cfg.hashtags_base)) hashtagsBaseInput.value = cfg.hashtags_base.join(',');
      if (Array.isArray(cfg.openers)) openersInput.value = cfg.openers.join('\\n');
      if (Array.isArray(cfg.core_love)) coreLoveInput.value = cfg.core_love.join('\\n');
      if (Array.isArray(cfg.playful_addons)) playfulAddonsInput.value = cfg.playful_addons.join('\\n');
      if (Array.isArray(cfg.light_spicy)) lightSpicyInput.value = cfg.light_spicy.join('\\n');
    }

    async function loadMetrics() {
      try {
        const r = await fetch('/api/metrics');
        const m = await r.json();
        if (visitorsEl && m && typeof m.total_pageviews === 'number') {
          visitorsEl.textContent = m.total_pageviews;
        }
      } catch (e) {}
    }

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
      loadConfig();
      loadMetrics();
      setInterval(loadMetrics, 10000);
    });
  </script>
</body>
</html>
"""

NODES_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <title>Nodes — จัสมินชอบกินแซลมอน</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans', 'Helvetica Neue', Arial, 'Noto Color Emoji', 'Noto Emoji', sans-serif; margin:0; padding:0; background:#111; color:#eee; }
    a { color:#85d0ff; text-decoration:none; }
    header { padding: 16px 24px; background:#181818; border-bottom:1px solid #2a2a2a; display:flex; align-items:center; gap: 16px; }
    h1 { margin:0; font-size:20px; }
    .wrap { padding: 16px 24px; }
    table { width:100%; border-collapse: collapse; }
    th, td { padding: 8px 10px; border-bottom: 1px solid #2a2a2a; font-size: 14px; }
    .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; }
    .ok { background:#16391f; color:#a7f3d0; }
    .off { background:#3a1e1e; color:#fecaca; }
    .small { color:#aaa; font-size:12px; }
    .grid { display:grid; grid-template-columns: 1fr 360px; gap:16px; }
    .panel { background:#181818; border:1px solid #2a2a2a; border-radius:10px; padding:12px; }
    input[type="text"] { width:100%; background:#121212; border:1px solid #2a2a2a; color:#eaeaea; border-radius:6px; padding:6px 8px; }
    .btn { display:inline-block; background:#2a6bff; color:#fff; border:0; padding:6px 10px; border-radius:6px; cursor:pointer; margin-top:8px; }
  </style>
</head>
<body>
  <header>
    <h1>Nodes — จัสมินชอบกินแซลมอน</h1>
    <a href="/">กลับสู่แดชบอร์ด</a>
    <a href="/about">About</a>
  </header>
  <div class="wrap">
    <div class="grid">
      <div class="panel">
        <div style="font-weight: 600; margin-bottom: 8px;">รายการโหนด</div>
        <table id="tbl">
          <thead><tr><th>ชื่อ</th><th>URL</th><th>สถานะ</th><th>last_seen</th><th>beats</th></tr></thead>
          <tbody></tbody>
        </table>
        <div class="small">รีเฟรชอัตโนมัติทุก 5 วินาที</div>
      </div>
      <div class="panel">
        <div style="font-weight: 600; margin-bottom: 8px;">ลงทะเบียนโหนด (manual)</div>
        <label>ชื่อโหนด</label>
        <input id="name" type="text" placeholder="node-01" />
        <label>URL</label>
        <input id="url" type="text" placeholder="https://node-01.example.com" />
        <button class="btn" id="btnReg">Register</button>
        <div id="msg" class="small" style="margin-top:8px;"></div>
      </div>
    </div>
  </div>
  <script>
    async function load() {
      const res = await fetch('/api/nodes');
      const list = await res.json();
      const tb = document.querySelector('#tbl tbody');
      tb.innerHTML = '';
      for (const n of list) {
        const tr = document.createElement('tr');
        const st = n.status === 'online' ? '<span class="badge ok">online</span>' : '<span class="badge off">offline</span>';
        const d = new Date((n.last_seen || 0) * 1000).toLocaleString();
        tr.innerHTML = '<td>'+ (n.name||'') +'</td><td>'+ (n.url||'') +'</td><td>'+ st +'</td><td>'+ d +'</td><td>'+ (n.beats||0) +'</td>';
        tb.appendChild(tr);
      }
    }
    setInterval(load, 5000);
    load();

    document.getElementById('btnReg').onclick = async () => {
      const name = document.getElementById('name').value.trim();
      const url = document.getElementById('url').value.trim();
      if (!name || !url) return;
      const r = await fetch('/api/nodes/register', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name, url})});
      const data = await r.json();
      const msg = document.getElementById('msg');
      if (data.id) { msg.textContent = 'ลงทะเบียนสำเร็จ: ' + data.id; } else { msg.textContent = JSON.stringify(data); }
      load();
      setTimeout(() => msg.textContent = '', 2000);
    };
  </script>
</body>
</html>
"""

app = Flask(__name__)

# CORS: allow cross-origin calls from static dashboards (e.g., cosine.page)
@app.after_request
def _add_cors(resp):
    try:
        resp.headers["Access-Control-Allow-Origin"] = os.getenv("CORS_ALLOW_ORIGIN", "*")
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = request.headers.get("Access-Control-Request-Headers", "*") or "*"
        # EventSource does not use credentials; keep simple
        resp.headers["Access-Control-Allow-Credentials"] = "false"
    except Exception:
        pass
    return resp

@app.route("/__options__", methods=["OPTIONS"])
def _options_probe():
    return ("", 204)


@app.get("/")
def index():
    # Log pageview
    try:
        mstore.pageview("index")
    except Exception:
        pass
    # Prefer template file if available; fallback to inline HTML.
    try:
        return render_template("index.html")
    except Exception:
        return render_template_string(INDEX_HTML)


@app.get("/about")
def about():
    try:
        mstore.pageview("about")
    except Exception:
        pass
    return render_template("about.html")


@app.get("/tony")
def tony_page():
    try:
        mstore.pageview("tony")
    except Exception:
        pass
    try:
        return render_template("tony.html")
    except Exception:
        return "<html><body><h1>อ.โทนี่สะท้อนกรรม</h1><p>Template missing.</p></body></html>"


@app.get("/nodes")
def nodes_page():
    return render_template_string(NODES_HTML)


@app.get("/credentials")
def credentials_page():
    # Log pageview
    try:
        mstore.pageview("credentials")
    except Exception:
        pass
    try:
        return render_template("credentials.html")
    except Exception:
        # Minimal fallback if template missing
        return "<html><body><h1>Credentials</h1><p>Use the API at /api/credentials to GET/POST values.</p></body></html>"


@app.get("/workflows")
def workflows_page():
    try:
        mstore.pageview("workflows")
    except Exception:
        pass
    try:
        return render_template("workflows.html")
    except Exception:
        return "<html><body><h1>Workflows</h1><p>Use the API at /api/workflows to view summary.</p></body></html>"


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


@app.get("/events")
def events() -> Response:
    # Count SSE subscribers as visits too
    try:
        mstore.pageview("events")
    except Exception:
        pass

    def gen() -> Generator[str, None, None]:
        for ev in bus.stream(keepalive_sec=1.0):
            try:
                yield "data: " + json.dumps(ev, ensure_ascii=False) + "\n\n"
            except Exception:
                # continue even if a single event cannot be serialized
                continue

    headers = {"Cache-Control": "no-cache"}
    return Response(gen(), mimetype="text/event-stream", headers=headers)


@app.get("/api/metrics")
def api_metrics():
    try:
        return jsonify(mstore.get_metrics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/circuit-states")
def api_circuit_states():
    try:
        return jsonify(cbreak.states())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/workflows")
def api_workflows_summary():
    try:
        return jsonify(wstore.summary())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/workflows/reset")
def api_workflows_reset():
    try:
        wstore.reset()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/events")
def events_stream():
    try:
        last_id = request.args.get("last_id", default=None, type=int)
    except Exception:
        last_id = None

    def _gen():
        for ev in bus.stream(last_id=last_id, keepalive_sec=1.0):
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"

    return Response(_gen(), mimetype="text/event-stream")


@app.get("/api/nodes")
def api_nodes_list():
    return jsonify(nreg.list_nodes())


@app.post("/api/nodes/register")
def api_nodes_register():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        name = str(payload.get("name", "")).strip()
        url = str(payload.get("url", "")).strip()
        if not name or not url:
            return jsonify({"error": "name and url are required"}), 400
        node = nreg.register(name=name, url=url, meta={"user": "web"})
        try:
            bus.publish({"type": "node", "action": "register", "node": {"id": node["id"], "name": node["name"], "url": node["url"]}})
        except Exception:
            pass
        return jsonify(node)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/nodes/heartbeat")
def api_nodes_heartbeat():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        node_id = str(payload.get("id", "")).strip()
        metrics = payload.get("metrics") or {}
        if not node_id:
            return jsonify({"error": "id is required"}), 400
        node = nreg.heartbeat(node_id, metrics=metrics)
        try:
            bus.publish({"type": "node", "action": "heartbeat", "node": {"id": node["id"], "name": node["name"]}, "metrics": metrics})
        except Exception:
            pass
        return jsonify(node)
    except KeyError:
        return jsonify({"error": "node not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/nodes/summary")
def api_nodes_summary():
    return jsonify(nreg.summary())


@app.get("/api/credentials")
def api_credentials_get():
    try:
        return jsonify(credstore.get_masked())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/credentials")
def api_credentials_post():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        masked = credstore.update(payload)
        # Optionally publish event
        try:
            bus.publish({"type": "config", "action": "credentials_update", "keys": list(payload.keys())})
        except Exception:
            pass
        return jsonify({"ok": True, "credentials": masked})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/circuit")
def api_circuit_states():
    try:
        return jsonify(cbreak.states())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/metrics")
def api_metrics():
    try:
        return jsonify(mstore.get_metrics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


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


# ===== Credits APIs =====
@app.get("/api/credits")
def api_get_credits():
    try:
        user = request.args.get("user", default="guest")
    except Exception:
        user = "guest"
    try:
        import credits_store as cstore
        return jsonify({"user": user, "credits": cstore.get(user)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/credits/use")
def api_use_credit():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
    except Exception:
        user = "guest"
    try:
        import credits_store as cstore
        left = cstore.use(user)
        if left is None:
            return jsonify({"ok": False, "error": "insufficient_credits"}), 400
        return jsonify({"ok": True, "credits_left": left})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/credits/add")
def api_add_credit():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
        delta = int(payload.get("delta", 0))
    except Exception:
        user = "guest"
        delta = 0
    try:
        import credits_store as cstore
        newv = cstore.add(user, delta)
        return jsonify({"ok": True, "credits": newv})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Payment notify (mock webhook) =====
@app.post("/api/payment/notify")
def api_payment_notify():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
        amount = float(payload.get("amount", 0))
        # simple mapping: 100 THB -> 5 credits
        credits = 0
        if amount >= 100:
            credits = 5
        elif amount >= 50:
            credits = 2
        import credits_store as cstore
        newv = cstore.add(user, credits)
        try:
            bus.publish({"type": "payment", "user": user, "amount": amount, "credits_added": credits, "ts": time.time()})
        except Exception:
            pass
        return jsonify({"ok": True, "credits_added": credits, "credits": newv})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Divination API (calls AI or mocked) =====
@app.post("/api/divination")
def api_divination():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
        div_type = str(payload.get("type", "general")).strip() or "general"
        text = str(payload.get("text", "")).strip()
        if not text:
            return jsonify({"error": "text is required"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Consume credit first
    try:
        import credits_store as cstore
        left = cstore.use(user)
        if left is None:
            return jsonify({"error": "insufficient_credits"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Generate via AI provider (Gemini) or fallback
    try:
        from providers.ai_divination import generate_divination
        result = generate_divination(user, div_type, text)
    except Exception:
        # fallback as last resort
        try:
            import content_generator as cg
            base = cg.make_text(sender=os.getenv("SENDER_NAME", "อ.โทนี่สะท้อนกรรม"))
            result = f"({div_type}) ผลคำทำนายจำลอง:\n{base}"
        except Exception:
            result = f"({div_type}) ผลคำทำนายจำลองสำหรับ: \"{text}\" — โปรดเชื่อมต่อโมเดล AI จริง"

    # Save history
    try:
        import divination_store as dstore
        item = dstore.append(user_id=user, div_type=div_type, input_text=text, result_text=result)
        try:
            bus.publish({"type": "divination", "user": user, "div_type": div_type, "ts": time.time(), "text": result[:140]})
        except Exception:
            pass
        return jsonify({"ok": True, "credits_left": left, "item": item})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/api/divination/history")
def api_divination_history():
    try:
        user = request.args.get("user", default=None)
    except Exception:
        user = None
    try:
        import divination_store as dstore
        hist = dstore.recent(50)
        if user:
            hist = [h for h in hist if h.get("user_id") == user]
        return jsonify(hist)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def start_web():
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)
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


# ===== Credits APIs =====
@app.get("/api/credits")
def api_get_credits():
    try:
        user = request.args.get("user", default="guest")
    except Exception:
        user = "guest"
    try:
        import credits_store as cstore
        return jsonify({"user": user, "credits": cstore.get(user)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/credits/use")
def api_use_credit():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
    except Exception:
        user = "guest"
    try:
        import credits_store as cstore
        left = cstore.use(user)
        if left is None:
            return jsonify({"ok": False, "error": "insufficient_credits"}), 400
        return jsonify({"ok": True, "credits_left": left})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/credits/add")
def api_add_credit():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
        delta = int(payload.get("delta", 0))
    except Exception:
        user = "guest"
        delta = 0
    try:
        import credits_store as cstore
        newv = cstore.add(user, delta)
        return jsonify({"ok": True, "credits": newv})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Payment notify (mock webhook) =====
@app.post("/api/payment/notify")
def api_payment_notify():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        user = str(payload.get("user", "guest")).strip() or "guest"
        amount = float(payload.get("amount", 0))
        # simple mapping: 100 THB -> 5 credits
        credits = 0
        if amount >= 100:
            credits = 5
        elif amount >= 50:
            credits = 2
        import credits_store as cstore
        newv = cstore.add(user, credits)
        try:
            bus.publish({"type": "payment", "user": user, "amount": amount, "credits_added": credits, "ts": time.time()})
        except Exception:
            pass
        return jsonify({"ue)