import json
import os

from flask import Flask, jsonify, render_template, request, redirect, url_for

import realtime_bus as bus
import metrics_store as mstore

# Support PaaS environments (Heroku/Render/Railway) that pass PORT
WEB_PORT = int(os.getenv("PORT", os.getenv("WEB_PORT", "8000")))

app = Flask(__name__)

# CORS: allow cross-origin calls (optional)
@app.after_request
def _add_cors(resp):
    try:
        resp.headers["Access-Control-Allow-Origin"] = os.getenv("CORS_ALLOW_ORIGIN", "*")
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = request.headers.get("Access-Control-Request-Headers", "*") or "*"
        resp.headers["Access-Control-Allow-Credentials"] = "false"
    except Exception:
        pass
    return resp

@app.route("/__options__", methods=["OPTIONS"])
def _options_probe():
    return ("", 204)

# Homepage: redirect to fortune
@app.get("/")
def index():
    try:
        mstore.pageview("index")
    except Exception:
        pass
    return redirect(url_for("fortune_page"))

# Fortune (ดูดวง)
@app.get("/fortune")
def fortune_page():
    try:
        mstore.pageview("fortune")
    except Exception:
        pass
    return render_template("fortune.html", user=None)

@app.post("/fortune")
def fortune_post():
    try:
        payload = request.get_json(force=True, silent=True) or {}
    except Exception:
        payload = {}
    name = (payload.get("name") or request.form.get("name") or "").strip()
    birth = (payload.get("birth") or request.form.get("birth") or "").strip()  # YYYY-MM-DD
    topic = (payload.get("topic") or request.form.get("topic") or "ภาพรวม").strip()

    import datetime, hashlib, random
    today = datetime.date.today().isoformat()
    seed_str = f"{name}|{birth}|{topic}|{today}"
    seed = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16) % (10**8)
    rnd = random.Random(seed)

    fortunes = {
        "ภาพรวม": [
            "วันนี้พลังงานดี มีโอกาสใหม่เข้ามา",
            "ระวังความใจร้อนเล็กน้อย ตั้งสติแล้วไปต่อ",
            "เหมาะกับการเริ่มต้นสิ่งใหม่ ๆ",
            "มีเกณฑ์ได้รับข่าวดีจากคนไกล",
            "พักใจสักนิด แล้วสิ่งดี ๆ จะตามมา",
        ],
        "การงาน": [
            "งานคืบหน้าเร็ว ได้แรงสนับสนุนจากทีม",
            "ระวังรายละเอียดสัญญา ทบทวนให้ครบถ้วน",
            "เหมาะกับการวางแผนระยะยาว",
            "มีโอกาสโชว์ผลงานและเป็นที่ยอมรับ",
            "อย่ากลัวการเปลี่ยนแปลง มันพาคุณไปสู่โอกาส",
        ],
        "การเงิน": [
            "รายรับ-รายจ่ายสมดุลขึ้นกว่าเดิม",
            "ระวังการใช้จ่ายฟุ่มเฟือย คุมงบประมาณให้ดี",
            "มีโชคเล็ก ๆ น้อย ๆ จากการเจรจา",
            "เหมาะกับการลงทุนระยะยาวแบบปลอดภัย",
            "ตรวจสอบบิล/สัญญา เพื่อเลี่ยงค่าใช้จ่ายแอบแฝง",
        ],
        "ความรัก": [
            "คนโสดมีเกณฑ์พบคนที่ถูกใจ",
            "คู่รักสื่อสารมากขึ้น เข้าใจกันดี",
            "อย่าเก็บเรื่องเล็กเป็นเรื่องใหญ่ พูดคุยด้วยเหตุผล",
            "มีโอกาสออกเดต/ทำกิจกรรมร่วมกัน",
            "ความสัมพันธ์ก้าวหน้าอย่างเป็นธรรมชาติ",
        ],
        "สุขภาพ": [
            "ร่างกายต้องการการพักผ่อนที่มีคุณภาพ",
            "เหมาะกับการออกกำลังกายเบา ๆ และเข้ากลางแจ้ง",
            "ดื่มน้ำมากขึ้น ระบบภายในจะดีขึ้น",
            "ฟังสัญญาณร่างกาย อย่าฝืนจนเกินไป",
            "เติมอาหารที่มีประโยชน์ ลดหวาน/เค็ม",
        ],
    }
    chosen_list = fortunes.get(topic, fortunes["ภาพรวม"])
    msg = rnd.choice(chosen_list)
    lucky_color = rnd.choice(["น้ำเงิน","เขียว","ทอง","ขาว","ม่วง","ชมพู","ดำ","แดง"])
    lucky_number = rnd.randint(1, 99)

    result = {
        "name": name or "คุณ",
        "birth": birth,
        "topic": topic,
        "message": msg,
        "lucky_color": lucky_color,
        "lucky_number": lucky_number,
        "date": today,
    }

    try:
        bus.publish({"type": "fortune", "ts": int(datetime.datetime.now().timestamp()), "name": name or "", "topic": topic, "message": msg})
    except Exception:
        pass

    return jsonify(result)

@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})

def start_web():
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)

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
    <a href="/qr">QR</a>
    <span style="margin-left:8px;color:#888;">{{ 'เข้าสู่ระบบแล้ว: ' + (user or '') if user else '' }}</span>
    {% if user %}<a href="/logout" style="margin-left:12px;">Logout</a>{% else %}<a href="/login" style="margin-left:12px;">Login</a>{% endif %}
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
app.secret_key = SECRET_KEY

def current_user():
    return session.get("user")

def require_login_api():
    if not AUTH_REQUIRED:
        return None
    if current_user():
        return None
    return jsonify({"error": "login required"}), 401

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

# Authentication pages
@app.get("/login")
def login_page():
    return render_template("login.html")

@app.post("/login")
def login_post():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        # If traditional form, fallback to form fields
        username = payload.get("username") or request.form.get("username") or ""
        password = payload.get("password") or request.form.get("password") or ""
        from users_store import authenticate
        if authenticate(username, password):
            session["user"] = username
            return jsonify({"ok": True, "user": username})
        return jsonify({"error": "invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/signup")
def signup_page():
    return render_template("signup.html")

@app.post("/signup")
def signup_post():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        username = (payload.get("username") or request.form.get("username") or "").strip()
        password = (payload.get("password") or request.form.get("password") or "").strip()
        from users_store import create_user
        user = create_user(username, password)
        session["user"] = username
        return jsonify({"ok": True, "user": user.get("username")})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/logout")
def logout)


@app.get("/")
def index():
    # Log pageview
    try:
        mstore.pageview("index")
    except Exception:
        pass
    # Redirect homepage to fortune page (ธีมเหลือแค่ดูดวง)
    return redirect(url_for("fortune_page"))


@app.get("/about")
def about():
    try:
        mstore.pageview("about")
    except Exception:
        pass
    return render_template("about.html", user=current_user())


@app.get("/nodes")
def nodes_page():
    return render_template_string(NODES_HTML, user=current_user())


@app.get("/credentials")
def credentials_page():
    # Log pageview
    try:
        mstore.pageview("credentials")
    except Exception:
        pass
    try:
        return render_template("credentials.html", user=current_user())
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
        return render_template("workflows.html", user=current_user())
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

# Pages: status and gallery
@app.get("/status")
def status_page():
    try:
        mstore.pageview("status")
    except Exception:
        pass
    try:
        import config_store
        cfg = config_store.get_config()
    except Exception:
        cfg = {}
    recent = []
    try:
        recent = bus.recent(50)
    except Exception:
        recent = []
    return render_template("status.html", cfg=cfg, recent=recent, user=current_user())

@app.get("/gallery")
def gallery_page():
    try:
        mstore.pageview("gallery")
    except Exception:
        pass
    media = []
    base = "outputs"
    # Prefer structured subdirs as documented: outputs/images, outputs/video, outputs/audio
    dirs_to_scan = [
        os.path.join(base, "images"),
        os.path.join(base, "video"),
    ]
    try:
        for d in dirs_to_scan:
            if not os.path.isdir(d):
                continue
            for fname in os.listdir(d):
                full = os.path.join(d, fname)
                if not os.path.isfile(full):
                    continue
                lower = fname.lower()
                mtype = None
                if lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
                    mtype = "image"
                elif lower.endswith((".mp4", ".mov", ".mkv", ".webm")):
                    mtype = "video"
                if not mtype:
                    continue
                try:
                    mtime = os.path.getmtime(full)
                except Exception:
                    mtime = 0
                rel = os.path.relpath(full, base)
                media.append({"type": mtype, "path": rel, "name": fname, "mtime": mtime})
        # newest first by mtime
        media.sort(key=lambda m: m.get("mtime", 0), reverse=True)
        media = media[:60]
    except Exception:
        media = []
    return render_template("gallery.html", media=media, user=current_user())

# Fortune (ดูดวง) page
@app.get("/fortune")
def fortune_page():
    try:
        mstore.pageview("fortune")
    except Exception:
        pass
    return render_template("fortune.html", user=current_user())

@app.post("/fortune")
def fortune_post():
    # Accept JSON or form; generate deterministic fortune for today
    try:
        payload = request.get_json(force=True, silent=True) or {}
    except Exception:
        payload = {}
    name = (payload.get("name") or request.form.get("name") or "").strip()
    birth = (payload.get("birth") or request.form.get("birth") or "").strip()  # YYYY-MM-DD
    topic = (payload.get("topic") or request.form.get("topic") or "ภาพรวม").strip()

    import datetime, hashlib, random
    today = datetime.date.today().isoformat()
    seed_str = f"{name}|{birth}|{topic}|{today}"
    seed = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16) % (10**8)
    rnd = random.Random(seed)

    fortunes = {
        "ภาพรวม": [
            "วันนี้พลังงานดี มีโอกาสใหม่เข้ามา",
            "ระวังความใจร้อนเล็กน้อย ตั้งสติแล้วไปต่อ",
            "เหมาะกับการเริ่มต้นสิ่งใหม่ ๆ",
            "มีเกณฑ์ได้รับข่าวดีจากคนไกล",
            "พักใจสักนิด แล้วสิ่งดี ๆ จะตามมา",
        ],
        "การงาน": [
            "งานคืบหน้าเร็ว ได้แรงสนับสนุนจากทีม",
            "ระวังรายละเอียดสัญญา ทบทวนให้ครบถ้วน",
            "เหมาะกับการวางแผนระยะยาว",
            "มีโอกาสโชว์ผลงานและเป็นที่ยอมรับ",
            "อย่ากลัวการเปลี่ยนแปลง มันพาคุณไปสู่โอกาส",
        ],
        "การเงิน": [
            "รายรับ-รายจ่ายสมดุลขึ้นกว่าเดิม",
            "ระวังการใช้จ่ายฟุ่มเฟือย คุมงบประมาณให้ดี",
            "มีโชคเล็ก ๆ น้อย ๆ จากการเจรจา",
            "เหมาะกับการลงทุนระยะยาวแบบปลอดภัย",
            "ตรวจสอบบิล/สัญญา เพื่อเลี่ยงค่าใช้จ่ายแอบแฝง",
        ],
        "ความรัก": [
            "คนโสดมีเกณฑ์พบคนที่ถูกใจ",
            "คู่รักสื่อสารมากขึ้น เข้าใจกันดี",
            "อย่าเก็บเรื่องเล็กเป็นเรื่องใหญ่ พูดคุยด้วยเหตุผล",
            "มีโอกาสออกเดต/ทำกิจกรรมร่วมกัน",
            "ความสัมพันธ์ก้าวหน้าอย่างเป็นธรรมชาติ",
        ],
            "สุขภาพ": [
            "ร่างกายต้องการการพักผ่อนที่มีคุณภาพ",
            "เหมาะกับการออกกำลังกายเบา ๆ และเข้ากลางแจ้ง",
            "ดื่มน้ำมากขึ้น ระบบภายในจะดีขึ้น",
            "ฟังสัญญาณร่างกาย อย่าฝืนจนเกินไป",
            "เติมอาหารที่มีประโยชน์ ลดหวาน/เค็ม",
        ],
    }
    chosen_list = fortunes.get(topic, fortunes["ภาพรวม"])
    msg = rnd.choice(chosen_list)
    lucky_color = rnd.choice(["น้ำเงิน","เขียว","ทอง","ขาว","ม่วง","ชมพู","ดำ","แดง"])
    lucky_number = rnd.randint(1, 99)

    result = {
        "name": name or "คุณ",
        "birth": birth,
        "topic": topic,
        "message": msg,
        "lucky_color": lucky_color,
        "lucky_number": lucky_number,
        "date": today,
    }

    try:
        bus.publish({"type": "fortune", "ts": int(datetime.datetime.now().timestamp()), "name": name or "", "topic": topic, "message": msg})
    except Exception:
        pass

    return jsonify(result)


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
    guarded = require_login_api()
    if guarded:
        return guarded
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
    guarded = require_login_api()
    if guarded:
        return guarded
    try:
        payload = request.get_json(force=True, silent=True) or {}
        name = str(payload.get("name", "")).strip()
        url = str(payload.get("url", "")).strip()
        if not name or not url:
            return jsonify({"error": "name and url are required"}),})
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
    guarded = require_login_api()
    if guarded:
        return guarded
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
        return


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
    guarded = require_login_api()
    if guarded:
        return guarded
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
        return jsonify({"error": str(e)}),


@app.post("/api/post-now")
def api_post_now():
    guarded = require_login_api()
    if guarded:
        return guarded
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
    guarded = require_login_api()
    if guarded:
        return guarded
    try:
        payload = request.get_json(force=True, silent=True) or {}
        line = str(payload.getrror": "line is required"}), 400
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


def start_web():
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, threaded=True)