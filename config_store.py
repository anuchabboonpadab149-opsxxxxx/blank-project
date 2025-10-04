import json
import os
import threading
from typing import Any, Dict, Optional

_PATH = os.getenv("RUNTIME_CONFIG_PATH", "runtime_config.json")
_LOCK = threading.Lock()

_DEFAULTS: Dict[str, Any] = {
    "post_interval_seconds": None,    # None -> use env/cli/default
    "collect_interval_minutes": None, # None -> use env/cli/default
    "providers": None,                # list[str] or None to use env
    "sender_name": None,              # override SENDER_NAME
    "tts_lang": "th",
    "content_mode": None,             # "generate" | "file" | "import" | None -> fallback
    "tweets_file": None,              # override tweets file path
    "import_source_url": None,
    "import_format": "lines",
    # Optional content overrides
    "hashtags_base": None,
    "openers": None,
    "core_love": None,
    "playful_addons": None,
    "light_spicy": None,

    # Prompt templates per science (LLM)
    "prompt_astrology": "คุณคือหมอดูโทนี่ จงวิเคราะห์ดวงชะตาจากข้อมูลวันเกิด/เวลาเกิด และคำถามของผู้ใช้ ด้วยภาษาที่น่าเชื่อถือ กระชับ เป็นขั้นตอน สรุป: โฟกัสหลัก, ระดับดวง, คำแนะนำปฏิบัติ",
    "prompt_tarot": "คุณคือหมอดูโทนี่ ใช้ผลการสุ่มไพ่ยิปซีเพื่อสรุปแนวโน้มและคำแนะนำตามบริบทคำถาม",
    "prompt_dice": "คุณคือหมอดูโทนี่ วิเคราะห์ผลทอยลูกเต๋าและสรุปความหมายเชิงแนวโน้ม",
    "prompt_siamsee": "คุณคือหมอดูโทนี่ ตีความเซียมซีตามเลขและสรุปข้อควรทำ",
    "prompt_pok": "คุณคือหมอดูโทนี่ ตีความไพ่ป๊อกแบบทำนายแนวโน้ม",
    "prompt_palm": "คุณคือหมอดูโทนี่ วิเคราะห์ลายมือจากภาพ: เส้นชีวิต เส้นสมอง เส้นหัวใจ และสรุปคำแนะนำ",
    "prompt_face": "คุณคือหมอดูโทนี่ วิเคราะห์โหงวเฮ้งจากภาพใบหน้า: ดวงตา จมูก ปาก โหนกแก้ม หน้าผาก",
    "prompt_dream": "คุณคือหมอดูโทนี่ ตีความความฝันของผู้ใช้โดยเชื่อมโยงสัญลักษณ์สำคัญ",
    "prompt_phone": "คุณคือหมอดูโทนี่ วิเคราะห์เบอร์โทรศัพท์ด้วยหลักตัวเลขและให้คำแนะนำ",
    "prompt_license": "คุณคือหมอดูโทนี่ วิเคราะห์เลขทะเบียนรถในมุมมงคลและวันดี",
    "prompt_name": "คุณคือหมอดูโทนี่ วิเคราะห์ชื่อ-นามสกุลให้คำแนะนำด้านภาพรวมชีวิต/งาน/ความรัก",

    # Admin-configurable brand and shop
    "brand_name": "อ.โทนี่สะท้อนกรรม",
    "theme_primary": "#2a6bff",
    "brand_logo_path": None,   # relative under outputs/branding or absolute URL if served locally
    "payment_info": "โอนเข้าบัญชี/พร้อมเพย์: SCB 8162785073 ชื่อบัญชี พิรุฬห์วัฒน์ ชยมาฒย์",
    "packages": [
        {"id": "p100", "price": 100, "credits": 10},
        {"id": "p300", "price": 300, "credits": 35},
        {"id": "p500", "price": 500, "credits": 60},
    ],
}


def _load() -> Dict[str, Any]:
    if not os.path.exists(_PATH):
        return {}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, Any]) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def get_config() -> Dict[str, Any]:
    with _LOCK:
        cfg = _DEFAULTS.copy()
        cfg.update(_load())
        return cfg


def get(key: str, default: Any = None) -> Any:
    return get_config().get(key, default)


def update_config(patch: Dict[str, Any]) -> Dict[str, Any]:
    with _LOCK:
        cur = _load()
        # Only update keys we know
        for k in list(patch.keys()):
            if k not in _DEFAULTS:
                patch.pop(k, None)
        cur.update(patch)
        _save(cur)
        return get_config()