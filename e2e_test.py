import os
import sys
import time
import json
import tempfile
import requests

"""
End-to-end test runner for Tony platform with real LLM.

Usage:

  # Set these environment variables before running:
  export BASE_URL=http://localhost:8000
  export ADMIN_SECRET=adm_....                   # from .env
  # Choose ONE provider:
  export LLM_PROVIDER=openai
  export OPENAI_API_KEY=sk-...                   # OpenAI key
  export OPENAI_MODEL=gpt-4o-mini                # optional (default)

  # OR
  export LLM_PROVIDER=gemini
  export GEMINI_API_KEY=...                      # Gemini key
  export GEMINI_MODEL=gemini-1.5-flash           # optional (default)

  python3 e2e_test.py

This script will:
- POST /api/credentials to set LLM keys
- Register + login a test user
- Create a top-up request (no slip), approve it via ADMIN_SECRET
- Call services: astrology, tools:tarot, analysis-upload (palm image), numbers:phone
- Fetch history
"""

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# a sample palm image (public domain/CC) — fallback to a small placeholder if download fails
SAMPLE_IMAGE_URL = os.getenv("SAMPLE_IMAGE_URL", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Palmistry_diagram.png/640px-Palmistry_diagram.png")

def _get(path: str, **kw):
    return requests.get(BASE_URL + path, timeout=20, **kw)

def _post(path: str, **kw):
    return requests.post(BASE_URL + path, timeout=30, **kw)

def wait_health(timeout=60):
    print("[*] Waiting for healthz ...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = _get("/healthz")
            if r.ok and r.json().get("ok"):
                print("[*] Health ok")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("[!] Health not OK within timeout")
    return False

def set_llm_credentials():
    print("[*] Setting LLM credentials ...")
    payload = {}
    if LLM_PROVIDER == "openai":
        assert OPENAI_API_KEY, "OPENAI_API_KEY required"
        payload = {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": OPENAI_API_KEY, "OPENAI_MODEL": OPENAI_MODEL}
    elif LLM_PROVIDER == "gemini":
        assert GEMINI_API_KEY, "GEMINI_API_KEY required"
        payload = {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": GEMINI_API_KEY, "GEMINI_MODEL": GEMINI_MODEL}
    else:
        raise RuntimeError("LLM_PROVIDER must be 'openai' or 'gemini'")

    r = _post("/api/credentials", json=payload)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError("Setting credentials failed: " + json.dumps(data))
    print("[*] LLM credentials applied")

def register_and_login(sess: requests.Session, username: str, password: str):
    print(f"[*] Registering user: {username}")
    r = sess.post(BASE_URL + "/api/tony/register", json={"username": username, "password": password}, timeout=20)
    # ignore if username taken
    if not r.ok:
        print("[!] register:", r.status_code, r.text)
    print("[*] Logging in ...")
    r = sess.post(BASE_URL + "/api/tony/login", json={"username": username, "password": password}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError("Login failed: " + json.dumps(data))
    print("[*] Logged in")

def topup(sess: requests.Session, amount: int = 100):
    print("[*] Creating top-up request ...")
    fd = {"package_id": (None, "p100"), "amount": (None, str(amount))}
    r = sess.post(BASE_URL + "/api/tony/topup-request", files=fd, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError("Top-up request failed: " + json.dumps(data))
    tid = data["request"]["id"]
    print("[*] Approving top-up ...")
    r = _post("/api/tony/topup-approve", json={"topup_id": tid, "admin_secret": ADMIN_SECRET})
    r.raise_for_status()
    d2 = r.json()
    if not d2.get("ok"):
        raise RuntimeError("Top-up approve failed: " + json.dumps(d2))
    print("[*] Top-up approved")

def download_sample_image() -> str:
    try:
        print("[*] Downloading sample image ...")
        r = requests.get(SAMPLE_IMAGE_URL, timeout=30)
        r.raise_for_status()
        fd, path = tempfile.mkstemp(prefix="tony_palm_", suffix=".png")
        with os.fdopen(fd, "wb") as f:
            f.write(r.content)
        print("[*] Saved sample image to", path)
        return path
    except Exception as e:
        print("[!] Could not download sample image:", e)
        return ""

def call_services(sess: requests.Session):
    print("[*] Calling astrology ...")
    r = sess.post(BASE_URL + "/api/tony/astrology", json={"dob": "1994-07-15", "tob": "09:30", "question": "งานและการเงินช่วงนี้"}, timeout=30)
    print("    ->", r.status_code, r.text[:200])

    print("[*] Calling tools: tarot (3) ...")
    r = sess.post(BASE_URL + "/api/tony/tools", json={"kind": "tarot", "cards": 3, "question": "ความรักครึ่งปีหลัง"}, timeout=30)
    print("    ->", r.status_code, r.text[:200])

    print("[*] Calling analysis-upload: palm ...")
    img_path = download_sample_image()
    files = {"kind": (None, "palm")}
    if img_path and os.path.exists(img_path):
        files["image"] = (os.path.basename(img_path), open(img_path, "rb"), "image/png")
    r = sess.post(BASE_URL + "/api/tony/analysis-upload", files=files, timeout=60)
    print("    ->", r.status_code, r.text[:200])

    print("[*] Calling numbers: phone ...")
    r = sess.post(BASE_URL + "/api/tony/numbers", json={"kind": "phone", "number": "0891234567"}, timeout=30)
    print("    ->", r.status_code, r.text[:200])

def fetch_history(sess: requests.Session):
    print("[*] Fetching history ...")
    r = sess.get(BASE_URL + "/api/tony/history", timeout=20)
    print("    ->", r.status_code)
    try:
        data = r.json()
        print("    count:", len(data.get("items", [])))
    except Exception:
        print("    body:", r.text[:200])

def main():
    if not ADMIN_SECRET:
        print("ERROR: ADMIN_SECRET is required in environment")
        sys.exit(1)

    if not wait_health():
        print("ERROR: /healthz not OK")
        sys.exit(2)

    set_llm_credentials()

    sess = requests.Session()
    # session cookie will be maintained automatically
    register_and_login(sess, username="demo_user", password="demo_pass123")
    topup(sess, amount=100)
    call_services(sess)
    fetch_history(sess)

    print("[*] E2E completed.")

if __name__ == "__main__":
    main()