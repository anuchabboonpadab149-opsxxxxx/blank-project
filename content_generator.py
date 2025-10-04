import os
import random
from typing import List, Optional

try:
    import config_store
except Exception:
    config_store = None


EMOJIS_SWEET = ["💖", "💕", "🥰", "😚", "💞", "😍"]
EMOJIS_FLIRTY = ["😉", "😏", "🤭", "🤤"]
EMOJIS_PLAYFUL = ["😜", "🙈", "✨", "💫"]
EMOJIS_LIGHT_SAUCE = ["💦"]  # use sparingly

# Default persona (Bee&Bell-like)
HASHTAGS_BASE = [
    "#BeeBell",
    "#รักเบลล์",
    "#จีบเล่นๆ",
    "#ขำขัน",
    "#หวิวเบาๆ",
]
OPENERS = [
    "แอบกระซิบ...",
    "จุ๊ๆ...",
    "ขอหยอดหน่อย...",
    "คืนนี้ขอหวานหน่อย...",
    "เช้านี้คิดถึงเบลล์จัง...",
    "วันนี้หัวใจเป็นของเบลล์นะ...",
]
CORE_LOVE = [
    "รักเบลล์มากกว่ากาแฟแก้วโปรด",
    "เบลล์คือวิตามินใจของเรา",
    "เจอเบลล์ทีไร ใจมันเต้นแรงทุกที",
    "โลกทั้งใบยังแพ้รอยยิ้มของเบลล์",
    "เบลล์คือความละมุนในทุกวัน",
    "ไม่ได้คิดถึง... แค่คิดถึงมากมากมาก",
]
PLAYFUL_ADDONS = [
    "ทำตัวน่ารักแบบนี้ ระวังโดนหยอดทุกวันนะ",
    "อย่าท้าทายความหวาน เดี๋ยวโดนขอหอมจริงๆ",
    "ถ้ารักคือเกม... เราขอเป็นผู้เล่นข้างๆเบลล์ตลอดไป",
    "ถ้ากอดได้หนึ่งครั้ง จะกอดจนรู้ว่าใจเราเต้นเพื่อใคร",
    "ยอมแพ้ให้ทุกอย่างที่ชื่อว่าเบลล์",
    "เราไม่เก่งเลข แต่เก่งรักเบลล์นะ",
]
LIGHT_SPICY = [
    "ขอหอมแก้มหนึ่งทีได้ไหม",
    "ทำเบาๆหน่อย เดี๋ยวใจเราไหวไม่ทัน",
    "คืนนี้ดาวอาจไม่พอ... ขอเบลล์แทนได้ไหม",
    "กอดแน่นๆจนเช้าเลยดีไหม",
    "ชอบความละมุน... แต่ขี้เล่นนิดๆนะ",
]

# Jasmine x Salmon persona
SALMON_HASHTAGS = [
    "#จัสมินชอบกินแซลมอน",
    "#แซลมอน",
    "#ซาชิมิ",
    "#salmonlover",
    "#อาหารญี่ปุ่น",
    "#วาซาบิ",
]
SALMON_OPENERS = [
    "กระซิบเบาๆ ตอนนี้หิวแซลมอนมาก",
    "คืนนี้ซาชิมิเข้าฝันอีกแล้ว",
    "วันนี้ใจมันเรียกหาโชยุวาซาบิ...",
    "ยิ้มให้หน่อย เดี๋ยวป้อนแซลมอนคำโต",
    "ขอความรักที่ละมุนเหมือนแซลมอนซาชิมิหน่อย",
]
SALMON_CORE = [
    "รักเธอเหนียวแน่นกว่าเนื้อแซลมอนลายสวย",
    "หัวใจก็เหมือนโชยุ—ขาดเธอไม่ได้เหมือนขาดแซลมอน",
    "ทุกคำของเธอคือวาซาบิอ่อนๆ อุ่นหัวใจ",
    "ให้แซลมอนทั้งท้องทะเล ยังไม่เท่ารอยยิ้มเธอ",
    "ถ้าเธอคือแซลมอน เราคือตะเกียบที่อยากจับไว้ตลอดไป",
]
SALMON_PLAYFUL = [
    "ขอจองที่ข้างๆ ในร้านโอมากาเสะใจเธอได้ไหม",
    "เดี๋ยวปั้นข้าวหน้าปลาให้—เธอปั้นยิ้มกลับมาให้เราหน่อย",
    "ระวังนะ เราแพ้ทางคนชอบแซลมอน... โดยเฉพาะเธอ",
    "ทีมซาชิมิหรือซูชิ—เราทีมเธอทุกเมนู",
    "ถ้าเงินเดือนหมดเพราะแซลมอน รับผิดชอบหัวใจเราด้วยนะ",
]
SALMON_SPICY = [
    "ขอแซลมอนละลายบนลิ้น พร้อมหัวใจละลายบนไหล่เธอ",
    "ขอหนึ่งคำที่ปาก กับอีกหนึ่งคำที่ใจได้ไหม",
    "คืนนี้ไม่ต้องเผ็ดมาก ขอละมุนแบบแซลมอนสดๆ ก็พอ",
    "เติมวาซาบินิด ใส่รักเราหน่อย ละมุนกำลังดี",
]


def pick(seq: List[str]) -> str:
    return random.choice(seq)


def _override_list(name: str, default: List[str]) -> List[str]:
    if config_store:
        val = config_store.get(name)
        if isinstance(val, list) and val:
            return [str(x) for x in val if str(x).strip()]
    return default


def _use_salmon_persona(sender: str) -> bool:
    s = (sender or "").lower()
    return ("จัสมิน" in s) or ("jasmine" in s) or ("แซลมอน" in s) or ("salmon" in s)


def _get_canonical_line() -> Optional[str]:
    # Priority: runtime config override -> env -> default phrase (Thai)
    try:
        if config_store:
            line = config_store.get("canonical_line")
            if isinstance(line, str) and line.strip():
                return line.strip()
    except Exception:
        pass
    env_line = os.getenv("CANONICAL_LINE", "").strip()
    if env_line:
        return env_line
    # Default canonical message (requested)
    return "บีรักจัสมินชอบกินแซลมอนนะ ขอบคุณที่เคยซัพพอตกันเสมออยู่ข้างๆตลอด💖💍"


def build_hashtags(default_tags: List[str]) -> str:
    tags = _override_list("hashtags_base", default_tags)[:]
    random.shuffle(tags
)
    return " ".join(tags[:random.randint(2, 4)])


def generate_caption(sender_name: Optional[str] = None) -> str:
    if config_store and not sender_name:
        sender_name = config_store.get("sender_name") or "Bee&Bell"
    elif not sender_name:
        sender_name = "Bee&Bell"

    # Select persona defaults first (overrides still win if provided)
    if _use_salmon_persona(sender_name):
        base_openers = SALMON_OPENERS
        base_core = SALMON_CORE
        base_playful = SALMON_PLAYFUL
        base_spicy = SALMON_SPICY
        base_tags = SALMON_HASHTAGS
    else:
        base_openers = OPENERS
        base_core = CORE_LOVE
        base_playful = PLAYFUL_ADDONS
        base_spicy = LIGHT_SPICY
        base_tags = HASHTAGS_BASE

    openers = _override_list("openers", base_openers)
    core_love = _override_list("core_love", base_core)
    playful_addons = _override_list("playful_addons", base_playful)
    light_spicy = _override_list("light_spicy", base_spicy)

    opener = pick(openers)
    core = pick(core_love)
    playful = pick(playful_addons)
    spicy = pick(light_spicy) if random.random() < 0.8 else ""

    emojis = []
    emojis += random.sample(EMOJIS_SWEET, k=2)
    if random.random() < 0.85:
        emojis.append(pick(EMOJIS_FLIRTY))
    if random.random() < 0.6:
        emojis.append(pick(EMOJIS_PLAYFUL))
    if spicy and random.random() < 0.35:
        emojis.append(pick(EMOJIS_LIGHT_SAUCE))

    canonical = _get_canonical_line()

    # Compose body
    lines: List[str] = []
    # With high probability include canonical line first
    if canonical and random.random() < 0.9:
        lines.append(canonical)
    lines.append(f"{opener} {core} {' '.join(emojis)}")
    if playful:
        lines.append(playful)
    if spicy:
        lines.append(spicy)
    lines.append(build_hashtags(base_tags))
    lines.append(f"— {sender_name}")

    text = " ".join([p for p in lines if p])
    if len(text) > 270:
        text = text[:267] + "..."
    return text