import json
import os
import threading
import time
import uuid
import hashlib
from typing import Dict, Optional, Any, List, Tuple

# DB optional
USE_DB = False
try:
    import db as _db
    if _db.DB_URL:
        USE_DB = _db.init_db()
except Exception:
    USE_DB = False

# Simple file-based user + credit + topup stores (fallback)
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

def _maybe_migrate_files_to_db():
    if not USE_DB:
        return
    try:
        with _db.get_session() as s:
            cnt = s.query(_db.User).count()
            if cnt > 0:
                return
        # migrate users
        users = _load(USERS_PATH, [])
        with _db.get_session() as s:
            for u in users:
                uu = _db.User(
                    id=u.get("id") or uuid.uuid4().hex,
                    username=u.get("username"),
                    pw_hash=u.get("pw_hash") or "",
                    salt=u.get("salt") or "",
                    credits=int(u.get("credits", 0)),
                    created_ts=float(u.get("created_ts") or 0.0),
                    last_login_ts=u.get("last_login_ts"),
                    is_admin=bool(u.get("is_admin", False)),
                    role="admin" if u.get("is_admin") else "member",
                )
                s.merge(uu)
            s.commit()
        # migrate history
        try:
            with open(HISTORY_LOG, "r", encoding="utf-8") as f:
                with _db.get_session() as s:
                    for line in f:
                        try:
                            obj = json.loads(line)
                            h = _db.History(
                                ts=float(obj.get("ts") or 0.0),
                                user_id=obj.get("user_id") or "",
                                service=obj.get("service") or "",
                                inputs=json.dumps(obj.get("inputs") or {}, ensure_ascii=False),
                                result=json.dumps(obj.get("result") or {}, ensure_ascii=False),
                            )
                            s.add(h)
                        except Exception:
                            continue
                    s.commit()
        except Exception:
            pass
        # migrate transactions
        try:
            with open(TRANSACTIONS_LOG, "r", encoding="utf-8") as f:
                with _db.get_session() as s:
                    for line in f:
                        try:
                            obj = json.loads(line)
                            t = _db.Transaction(
                                ts=float(obj.get("ts") or 0.0),
                                type=str(obj.get("type") or ""),
                                user_id=obj.get("user_id") or "",
                                delta=int(obj.get("delta") or 0),
                                new_balance=int(obj.get("new_balance") or 0),
                                reason=obj.get("reason"),
                                meta=json.dumps(obj.get("meta") or {}, ensure_ascii=False),
                            )
                            s.add(t)
                        except Exception:
                            continue
                    s.commit()
        except Exception:
            pass
    except Exception:
        pass

_maybe_migrate_files_to_db()

def list_users() -> List[Dict[str, Any]]:
    if USE_DB:
        with _db.get_session() as s:
            rows = s.query(_db.User).all()
            out = []
            for u in rows:
                out.append({
                    "id": u.id, "username": u.username, "credits": u.credits,
                    "created_ts": u.created_ts, "last_login_ts": u.last_login_ts,
                    "is_admin": u.is_admin, "role": u.role
                })
            return out
    with _LOCK:
        users = _load(USERS_PATH, [])
        return users

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    username = (username or "").strip().lower()
    if not username:
        return None
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).filter(_db.User.username.ilike(username)).one_or_none()
            if not u:
                return None
            return {
                "id": u.id, "username": u.username, "credits": u.credits,
                "created_ts": u.created_ts, "last_login_ts": u.last_login_ts,
                "is_admin": u.is_admin, "role": u.role
            }
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if (u.get("username") or "").lower() == username:
                return u
    return None

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            if not u:
                return None
            return {
                "id": u.id, "username": u.username, "credits": u.credits,
                "created_ts": u.created_ts, "last_login_ts": u.last_login_ts,
                "is_admin": u.is_admin, "role": u.role
            }
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
    if USE_DB:
        with _db.get_session() as s:
            exist = s.query(_db.User).filter(_db.User.username.ilike(username)).count()
            if exist:
                raise ValueError("username_taken")
            pw_hash, salt = _hash_password(password)
            u = _db.User(
                id=uuid.uuid4().hex, username=username, pw_hash=pw_hash, salt=salt,
                credits=0, created_ts=_now(), last_login_ts=None, is_admin=False, role="member"
            )
            s.add(u); s.commit()
            return {"id": u.id, "username": u.username, "credits": 0, "created_ts": u.created_ts, "last_login_ts": None, "is_admin": False, "role": "member"}
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).filter(_db.User.username.ilike(username)).one_or_none()
            if not u:
                return None
            pw_hash, _ = _hash_password(password, u.salt or "")
            if pw_hash != u.pw_hash:
                return None
            u.last_login_ts = _now()
            s.commit()
            return {"id": u.id, "username": u.username, "credits": u.credits, "created_ts": u.created_ts, "last_login_ts": u.last_login_ts, "is_admin": u.is_admin, "role": u.role}
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            return int(u.credits) if u else 0
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            if not u:
                raise KeyError("user_not_found")
            new_val = int(u.credits) + credits
            u.credits = new_val
            # transaction log
            tr = _db.Transaction(ts=_now(), type="add", user_id=user_id, delta=credits, new_balance=new_val, reason=None, meta=json.dumps(meta or {}, ensure_ascii=False))
            s.add(tr); s.commit()
            return new_val
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            if not u:
                raise KeyError("user_not_found")
            bal = int(u.credits)
            if bal < 1:
                raise RuntimeError("insufficient_credits")
            u.credits = bal - 1
            tr = _db.Transaction(ts=_now(), type="deduct", user_id=user_id, delta=-1, new_balance=int(u.credits), reason=reason, meta=None)
            s.add(tr); s.commit()
            return int(u.credits)
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
    if USE_DB:
        with _db.get_session() as s:
            h = _db.History(ts=_now(), user_id=user_id, service=service, inputs=json.dumps(inputs, ensure_ascii=False), result=json.dumps(result, ensure_ascii=False))
            s.add(h); s.commit()
            return
    _append_log(HISTORY_LOG, {
        "ts": _now(),
        "user_id": user_id,
        "service": service,
        "inputs": inputs,
        "result": result,
    })

def list_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    if USE_DB:
        with _db.get_session() as s:
            rows = s.query(_db.History).filter(_db.History.user_id == user_id).order_by(_db.History.ts.desc()).limit(limit).all()
            out = []
            for h in rows:
                out.append({
                    "ts": h.ts, "user_id": h.user_id, "service": h.service,
                    "inputs": json.loads(h.inputs or "{}"), "result": json.loads(h.result or "{}")
                })
            return out
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
    # allow override via runtime config
    try:
        import config_store
        pkgs = config_store.get("packages")
        if isinstance(pkgs, list) and pkgs:
            # validate shape minimally
            out = []
            for p in pkgs:
                pid = str(p.get("id", "")).strip() or None
                price = int(p.get("price", 0))
                credits = int(p.get("credits", 0))
                if pid and price > 0 and credits > 0:
                    out.append({"id": pid, "price": price, "credits": credits})
            if out:
                return out
    except Exception:
        pass
    return DEFAULT_PACKAGES

def create_topup_request(user_id: str, package_id: str, amount: int, slip_path: Optional[str]) -> Dict[str, Any]:
    if USE_DB:
        # find package credits
        credits_map = {p["id"]: p["credits"] for p in list_packages()}
        credits = credits_map.get(package_id)
        if credits is None:
            credits = max(1, int(amount / 10))
            package_id = "custom"
        with _db.get_session() as s:
            req = _db.Topup(
                id=uuid.uuid4().hex,
                user_id=user_id, package_id=package_id, price=int(amount),
                credits_on_approve=int(credits),
                status="pending",
                slip_path=slip_path,
                created_ts=_now(), approved_ts=None, approved_by=None
            )
            s.add(req)
            tr = _db.Transaction(ts=_now(), type="topup_request", user_id=user_id, delta=0, new_balance=int(get_balance(user_id)), reason="topup", meta=json.dumps({"package_id": package_id, "amount": amount}, ensure_ascii=False))
            s.add(tr)
            s.commit()
            return {
                "id": req.id, "user_id": req.user_id, "package_id": req.package_id, "price": req.price,
                "credits_on_approve": req.credits_on_approve, "status": req.status, "slip_path": req.slip_path,
                "created_ts": req.created_ts, "approved_ts": req.approved_ts, "approved_by": req.approved_by
            }
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
    if USE_DB:
        with _db.get_session() as s:
            q = s.query(_db.Topup)
            if user_id:
                q = q.filter(_db.Topup.user_id == user_id)
            if status:
                q = q.filter(_db.Topup.status == status)
            rows = q.order_by(_db.Topup.created_ts.desc()).all()
            out = []
            for t in rows:
                out.append({
                    "id": t.id, "user_id": t.user_id, "package_id": t.package_id, "price": t.price,
                    "credits_on_approve": t.credits_on_approve, "status": t.status, "slip_path": t.slip_path,
                    "created_ts": t.created_ts, "approved_ts": t.approved_ts, "approved_by": t.approved_by
                })
            return out
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
    if USE_DB:
        with _db.get_session() as s:
            t = s.query(_db.Topup).get(topup_id)
            if not t:
                raise KeyError("topup_not_found")
            if t.status == "approved":
                return {
                    "id": t.id, "user_id": t.user_id, "package_id": t.package_id, "price": t.price,
                    "credits_on_approve": t.credits_on_approve, "status": t.status, "slip_path": t.slip_path,
                    "created_ts": t.created_ts, "approved_ts": t.approved_ts, "approved_by": t.approved_by
                }
            uid = t.user_id
            credits = int(t.credits_on_approve)
            t.status = "approved"
            t.approved_ts = _now()
            t.approved_by = admin_name
            s.commit()
            # add credits
            try:
                new_bal = add_credits(uid, credits, meta={"topup_id": topup_id})
            except Exception:
                new_bal = get_balance(uid)
            return {
                "id": t.id, "user_id": t.user_id, "package_id": t.package_id, "price": t.price,
                "credits_on_approve": t.credits_on_approve, "status": t.status, "slip_path": t.slip_path,
                "created_ts": t.created_ts, "approved_ts": t.approved_ts, "approved_by": t.approved_by,
                "new_balance": new_bal
            }
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).filter(_db.User.username.ilike(username)).one_or_none()
            if not u:
                return False
            u.is_admin = bool(is_admin)
            u.role = "admin" if is_admin else "member"
            s.commit()
            return True
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if (u.get("username") or "").lower() == username.lower():
                u["is_admin"] = bool(is_admin)
                _save(USERS_PATH, users)
                return True
        return False

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
    if USE_DB:
        with _db.get_session() as s:
            rows = s.query(_db.User).all()
            out = []
            for u in rows:
                out.append({
                    "id": u.id, "username": u.username, "credits": u.credits,
                    "created_ts": u.created_ts, "last_login_ts": u.last_login_ts,
                    "is_admin": u.is_admin, "role": u.role
                })
            return out
    with _LOCK:
        users = _load(USERS_PATH, [])
        return users

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    username = (username or "").strip().lower()
    if not username:
        return None
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).filter(_db.User.username.ilike(username)).one_or_none()
            if not u:
                return None
            return {
                "id": u.id, "username": u.username, "credits": u.credits,
                "created_ts": u.created_ts, "last_login_ts": u.last_login_ts,
                "is_admin": u.is_admin, "role": u.role
            }
    with _LOCK:
        users = _load(USERS_PATH, [])
        for u in users:
            if (u.get("username") or "").lower() == username:
                return u
    return None

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            if not u:
                return None
            return {
                "id": u.id, "username": u.username, "credits": u.credits,
                "created_ts": u.created_ts, "last_login_ts": u.last_login_ts,
                "is_admin": u.is_admin, "role": u.role
            }
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
    if USE_DB:
        with _db.get_session() as s:
            exist = s.query(_db.User).filter(_db.User.username.ilike(username)).count()
            if exist:
                raise ValueError("username_taken")
            pw_hash, salt = _hash_password(password)
            u = _db.User(
                id=uuid.uuid4().hex, username=username, pw_hash=pw_hash, salt=salt,
                credits=0, created_ts=_now(), last_login_ts=None, is_admin=False, role="member"
            )
            s.add(u); s.commit()
            return {"id": u.id, "username": u.username, "credits": 0, "created_ts": u.created_ts, "last_login_ts": None, "is_admin": False, "role": "member"}
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).filter(_db.User.username.ilike(username)).one_or_none()
            if not u:
                return None
            pw_hash, _ = _hash_password(password, u.salt or "")
            if pw_hash != u.pw_hash:
                return None
            u.last_login_ts = _now()
            s.commit()
            return {"id": u.id, "username": u.username, "credits": u.credits, "created_ts": u.created_ts, "last_login_ts": u.last_login_ts, "is_admin": u.is_admin, "role": u.role}
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            return int(u.credits) if u else 0
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            if not u:
                raise KeyError("user_not_found")
            new_val = int(u.credits) + credits
            u.credits = new_val
            # transaction log
            tr = _db.Transaction(ts=_now(), type="add", user_id=user_id, delta=credits, new_balance=new_val, reason=None, meta=json.dumps(meta or {}, ensure_ascii=False))
            s.add(tr); s.commit()
            return new_val
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
    if USE_DB:
        with _db.get_session() as s:
            u = s.query(_db.User).get(user_id)
            if not u:
                raise KeyError("user_not_found")
            bal = int(u.credits)
            if bal < 1:
                raise RuntimeError("insufficient_credits")
            u.credits = bal - 1
            tr = _db.Transaction(ts=_now(), type="deduct", user_id=user_id, delta=-1, new_balance=int(u.credits), reason=reason, meta=None)
            s.add(tr); s.commit()
            return int(u.credits)
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
    if USE_DB:
        with _db.get_session() as s:
            h = _db.History(ts=_now(), user_id=user_id, service=service, inputs=json.dumps(inputs, ensure_ascii=False), result=json.dumps(result, ensure_ascii=False))
            s.add(h); s.commit()
            return
    _append_log(HISTORY_LOG, {
        "ts": _now(),
        "user_id": user_id,
        "service": service,
        "inputs": inputs,
        "result": result,
    })

def list_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    if USE_DB:
        with _db.get_session() as s:
            rows = s.query(_db.History).filter(_db.History.user_id == user_id).order_by(_db.History.ts.desc()).limit(limit).all()
            out = []
            for h in rows:
                out.append({
                    "ts": h.ts, "user_id": h.user_id, "service": h.service,
                    "inputs": json.loads(h.inputs or "{}"), "result": json.loads(h.result or "{}")
                })
            return out
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
    # allow override via runtime config
    try:
        import config_store
        pkgs = config_store.get("packages")
        if isinstance(pkgs, list) and pkgs:
            # validate shape minimally
            out = []
            for p in pkgs:
                pid = str(p.get("id", "")).strip() or None
                price = int(p.get("price", 0))
                credits = int(p.get("credits", 0))
                if pid and price > 0 and credits > 0:
                    out.append({"id": pid, "price": price, "credits": credits})
            if out:
                return out
    except Exception:
        pass
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