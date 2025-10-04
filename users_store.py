import os
import json
from typing import Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash

USERS_PATH = os.getenv("USERS_FILE", os.path.join("data", "users.json"))


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)


def load_users() -> Dict[str, Dict]:
    try:
        if os.path.exists(USERS_PATH):
            with open(USERS_PATH, "r", encoding="utf-8") as f:
                return json.load(f) or {}
    except Exception:
        pass
    return {}


def save_users(data: Dict[str, Dict]) -> None:
    _ensure_dir(USERS_PATH)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(username: str) -> Optional[Dict]:
    users = load_users()
    return users.get(username)


def create_user(username: str, password: str) -> Dict:
    username = (username or "").strip()
    if not username or not password:
        raise ValueError("username and password are required")
    users = load_users()
    if username in users:
        raise ValueError("username already exists")
    users[username] = {
        "username": username,
        "password_hash": generate_password_hash(password),
    }
    save_users(users)
    return users[username]


def authenticate(username: str, password: str) -> bool:
    u = get_user(username.strip())
    if not u:
        return False
    return check_password_hash(u.get("password_hash", ""), password)