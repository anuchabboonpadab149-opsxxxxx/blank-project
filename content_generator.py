import random


EMOJIS_SWEET = ["💖", "💕", "🥰", "😚", "💞", "😍"]
EMOJIS_FLIRTY = ["😉", "😏", "🤭", "🤤"]
EMOJIS_PLAYFUL = ["😜", "🙈", "✨", "💫"]
EMOJIS_LIGHT_SAUCE = ["💦"]  # use sparingly

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


def pick(seq):
    return random.choice(seq)


def build_hashtags():
    tags = HASHTAGS_BASE[:]
    random.shuffle(tags)
    return " ".join(tags[:random.randint(2, 4)])


def generate_caption(sender_name="Bee&Bell"):
    opener = pick(OPENERS)
    core = pick(CORE_LOVE)
    playful = pick(PLAYFUL_ADDONS)
    spicy = pick(LIGHT_SPICY) if random.random() < 0.7 else ""
    emojis = []
    emojis += random.sample(EMOJIS_SWEET, k=2)
    if random.random() < 0.8:
        emojis.append(pick(EMOJIS_FLIRTY))
    if random.random() < 0.5:
        emojis.append(pick(EMOJIS_PLAYFUL))
    if spicy and random.random() < 0.3:
        emojis.append(pick(EMOJIS_LIGHT_SAUCE))

    parts = [
        f"{opener} {core} {' '.join(emojis)}",
        playful,
        spicy,
        build_hashtags(),
        f"— {sender_name}",
    ]
    # Remove empty parts and join
    text = " ".join([p for p in parts if p])
    # Trim to ~270 chars for safety
    if len(text) > 270:
        text = text[:267] + "..."
    return text