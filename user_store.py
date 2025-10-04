import json
import os
import threading
import time
import uuid
import hashlib
from typing import Dict, Optional, Any, List, Tuple

# Simple file-based user + credit + topup stores
USERS_PATH = os.getenv("USERS_PATH", "users.json")
TOPUPS_PATH = os.getenv("TOPUPS_PATH", "topups.json")
HISTORY_LOG = os.getenv("TONY_HISTORY_LOG", os.path.join("outputs", "tony_history.jsonl"))
TRANSACTIONS_LOG = os.getenv("TONY_TX_LOG", os.path.join("outputs", "tony_transactions.jsonl"))

_LOCK = threading.Lock()

def _ensure_dirs() -> None:
    os.makedirs(os.path.dirname(HISTORY_LOG) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(TRANSACTIONS_LOG) or ".", exist_ok=True)

_ensure_dirs()

def _now() -> float:
    return time.time()

def _load(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save(path: str, data) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    s = salt or uuid.uuid4().hex
    h = hashlib.sha256((s + "::" + password).encode("utf-8")).hexdigest()
    return h, s

def _mask(s: Optional[str], keep: int = 2) -> str:
    if not s:
        return ""
    if len(s) <= keep * 2:
        return "*" * len(s)
    return s[:keep] + ("*" * (len(s) - keep * 2)) + s[-keep:]

def list_users() -> List[Dict[str, Any]]:
    with _LOCK:
        users = _load(USERS_PATH, [])
        return users

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    username = (username or "").strip().lower()
    if not username:
        return None
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if (u.get("username") or "").lower() == username:
                return u
    return None

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if u.get("id") == user_id:
                return u
    return None

def register(username: str, password: str) -> Dict[str, Any]:
    username = (username or "").strip()
    if not username or not password or len(password) < 6:
        raise ValueError("invalid username/password")
    with _LOCK:
        users = _load(USERS_PATH, [])
        low = username.lower()
        for u in users:
            if (u.get("username") or "").lower() == low:
                raise ValueError("username_taken")
        pw_hash, salt = _hash_password(password)
        user = {
            "id": uuid.uuid4().hex,
            "username": username,
            "pw_hash": pw_hash,
            "salt": salt,
            "credits": 0,
            "created_ts": _now(),
            "last_login_ts": None,
            "is_admin": False,
        }
        users.append(user)
        _save(USERS_PATH, users)
        return {k: v for k, v in user.items() if k not in ("pw_hash", "salt")}

def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    username = (username or "").strip()
    if not username or not password:
        return None
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if (u.get("username") or "").lower() == username.lower():
                pw_hash, _ = _hash_password(password, u.get("salt") or "")
                if pw_hash == u.get("pw_hash"):
                    u["last_login_ts"] = _now()
                    _save(USERS_PATH, users)
                    return {k: v for k, v in u.items() if k not in ("pw_hash", "salt")}
    return None

def get_balance(user_id: str) -> int:
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if u.get("id") == user_id:
                return int(u.get("credits", 0))
    return 0

def _append_log(path: str, obj: Dict[str, Any]) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception:
        pass

def add_credits(user_id: str, credits: int, meta: Optional[Dict[str, Any]] = None) -> int:
    if credits <= 0:
        return get_balance(user_id)
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if u.get("id") == user_id:
                current = int(u.get("credits", 0))
                new_val = current + credits
                u["credits"] = new_val
                _save(USERS_PATH, users)
                _append_log(TRANSACTIONS_LOG, {
                    "ts": _now(),
                    "type": "add",
                    "user_id": user_id,
                    "delta": credits,
                    "new_balance": new_val,
                    "meta": meta or {}
                })
                return new_val
    raise KeyError("user_not_found")

def deduct_credit(user_id: str, reason: str) -> int:
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if u.get("id") == user_id:
                bal = int(u.get("credits", 0))
                if bal < 1:
                    raise RuntimeError("insufficient_credits")
                u["credits"] = bal - 1
                _save(USERS_PATH, users)
                _append_log(TRANSACTIONS_LOG, {
                    "ts": _now(),
                    "type": "deduct",
                    "user_id": user_id,
                    "delta": -1,
                    "new_balance": bal - 1,
                    "reason": reason
                })
                return bal - 1
    raise KeyError("user_not_found")

def record_history(user_id: str, service: str, inputs: Dict[str, Any], result: Dict[str, Any]) -> None:
    _append_log(HISTORY_LOG, {
        "ts": _now(),
        "user_id": user_id,
        "service": service,
        "inputs": inputs,
        "result": result,
    })

def list_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    try:
        with open(HISTORY_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("user_id") == user_id:
                        items.append(obj)
                except Exception:
                    continue
        items.sort(key=lambda x: x.get("ts", 0), reverse=True)
        return items[:limit]
    except Exception:
        return []

# Top-up management (manual confirmation flow)
DEFAULT_PACKAGES = [
    {"id": "p100", "price": 100, "credits": 10},
    {"id": "p300", "price": 300, "credits": 35},
    {"id": "p500", "price": 500, "credits": 60},
]

def list_packages() -> List[Dict[str, Any]]:
    return DEFAULT_PACKAGES

def create_topup_request(user_id: str, package_id: str, amount: int, slip_path: Optional[str]) -> Dict[str, Any]:
    with _LOCK:
        topups = _load(TOPUPS_PATH, [])
        pkg = None
        for p in DEFAULT_PACKAGES:
            if p["id"] == package_id:
                pkg = p
                break
        if not pkg:
            # Allow custom amount mapping to nearest pkg credits proportionally
            pkg = {"id": "custom", "price": amount, "credits": max(1, int(amount / 10))}
        req = {
            "id": uuid.uuid4().hex,
            "user_id": user_id,
            "package_id": pkg["id"],
            "price": amount,
            "credits_on_approve": pkg["credits"],
            "status": "pending",
            "slip_path": slip_path,
            "created_ts": _now(),
            "approved_ts": None,
            "approved_by": None,
        }
        topups.append(req)
        _save(TOPUPS_PATH, topups)
        _append_log(TRANSACTIONS_LOG, {
            "ts": _now(),
            "type": "topup_request",
            "user_id": user_id,
            "amount": amount,
            "package_id": pkg["id"],
            "slip_path": slip_path,
            "status": "pending"
        })
        return req

def list_topups(user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    with _LOCK:
        topups = _load(TOPUPS_PATH, [])
        out = []
        for t in topups:
            if user_id and t.get("user_id") != user_id:
                continue
            if status and t.get("status") != status:
                continue
            out.append(t)
        out.sort(key=lambda x: x.get("created_ts", 0), reverse=True)
        return out

def approve_topup(topup_id: str, admin_name: str) -> Dict[str, Any]:
    with _LOCK:
        topups = _load(TOPUPS_PATH, [])
        found = None
        for t in topups:
            if t.get("id") == topup_id:
                found = t
                break
        if not found:
            raise KeyError("topup_not_found")
        if found.get("status") == "approved":
            return found
        # credit user
        uid = found["user_id"]
        credits = int(found.get("credits_on_approve") or 0)
        # update status first for durability; then add credits
        found["status"] = "approved"
        found["approved_ts"] = _now()
        found["approved_by"] = admin_name
        _save(TOPUPS_PATH, topups)
        try:
            add_credits(uid, credits, meta={"topup_id": topup_id})
        except Exception:
            # revert? keep status but log
            pass
        return found

def set_admin(username: str, is_admin: bool = True) -> bool:
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if (u.get("username") or "").lower() == username.lower():
                u["is_admin"] = bool(is_admin)
                _save(USERS_PATH, users)
                return True
        return False