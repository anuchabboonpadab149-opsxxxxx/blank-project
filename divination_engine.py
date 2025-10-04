import random
import datetime
from typing import Dict, Any, List, Tuple

# Lightweight rule/template-based divination engine with optional LLM integration.
# If LLM keys are configured, the engine will call OpenAI/Gemini with prompt templates from config_store.
try:
    import config_store
except Exception:
    config_store = None
try:
    import llm_client
except Exception:
    llm_client = None

MAJOR_ARCANA = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

TAROT_HINTS = {
    "The Fool": "การเริ่มต้นใหม่ การก้าวออกจากพื้นที่ปลอดภัย เปิดรับโอกาส",
    "The Magician": "พลังในการสร้างสรรค์ ใช้ความสามารถเปลี่ยนสถานการณ์",
    "The High Priestess": "ฟังสัญชาตญาณ ความลับ ปัญญาภายใน",
    "The Empress": "ความอุดมสมบูรณ์ ความรัก การดูแลเอาใจใส่",
    "The Emperor": "ความมั่นคง กฎระเบียบ อำนาจ และการวางแผน",
    "The Hierophant": "ประเพณี ผู้ใหญ่ที่ให้คำแนะนำ การเรียนรู้จากระบบ",
    "The Lovers": "การตัดสินใจด้วยหัวใจ ความสัมพันธ์ พันธะสัญญา",
    "The Chariot": "ความมุ่งมั่น ควบคุมสถานการณ์ เดินหน้าอย่างมั่นใจ",
    "Strength": "ความกล้าหาญ อ่อนน้อมแต่ทรงพลัง ควบคุมอารมณ์",
    "The Hermit": "ถอยไปพิจารณา มองหาแสงนำทางในตัวเอง",
    "Wheel of Fortune": "การเปลี่ยนแปลงตามโชคชะตา วัฏจักร ช่วงเวลาที่หมุนเปลี่ยน",
    "Justice": "ความยุติธรรม การตัดสินอย่างมีเหตุผล ผลลัพธ์สมดุล",
    "The Hanged Man": "มองจากมุมใหม่ การเสียสละชั่วคราวเพื่อสิ่งที่ดีกว่า",
    "Death": "จบเพื่อเริ่มใหม่ ปล่อยวางสิ่งเก่า ยอมรับการเปลี่ยนแปลง",
    "Temperance": "ความพอดี การประสานความต่าง จังหวะที่เหมาะสม",
    "The Devil": "พันธนาการ ความหลง การยึดติดสิ่งไม่จำเป็น",
    "The Tower": "การเปลี่ยนแปลงฉับพลัน พังเพื่อสร้างใหม่ ความจริงที่ปรากฏ",
    "The Star": "ความหวัง การเยียวยา แรงบันดาลใจ",
    "The Moon": "ความสับสน ภาพลวงตา เชื่อในสัญชาตญาณ",
    "The Sun": "ความสำเร็จ ความชัดเจน พลังงานบวกและการเฉลิมฉลอง",
    "Judgement": "การตัดสินใจครั้งใหญ่ การฟื้นคืนชีพ บทเรียนเดิมกลับมา",
    "The World": "การสมบูรณ์ ครบถ้วน จบภารกิจและพร้อมเริ่มบทใหม่"
}

def _reduce_to_single_digit(n: int) -> int:
    n = abs(n)
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def _lucky_colors(n: int) -> List[str]:
    palettes = {
        1: ["แดง", "ทอง"], 2: ["ฟ้า", "เงิน"], 3: ["เขียว", "น้ำตาล"],
        4: ["น้ำเงินเข้ม", "เทา"], 5: ["เหลือง", "ขาว"], 6: ["ชมพู", "ครีม"],
        7: ["ม่วง", "กรมท่า"], 8: ["ส้ม", "เทอร์คอยซ์"], 9: ["เขียวมรกต", "ทอง"]
    }
    return palettes.get(n, ["ขาว", "ดำ"])

def _fortune_level(seed: int) -> str:
    # simple mapping by modulus
    r = seed % 100
    if r < 20:
        return "ดีมาก"
    if r < 50:
        return "ดี"
    if r < 80:
        return "ปานกลาง"
    return "ควรระวัง"

def _cfg_get(key: str, default: str = "") -> str:
    try:
        if config_store:
            v = config_store.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
    except Exception:
        pass
    return default

def _try_llm(system: str, prompt: str, vision_path: str = "") -> str:
    if not llm_client:
        raise RuntimeError("llm_client_unavailable")
    # raises if not configured; the caller should handle and fallback
    if vision_path:
        return llm_client.call_llm_vision(prompt=prompt, image_path=vision_path, system=system)
    return llm_client.call_llm_text(prompt=prompt, system=system)

def analyze_astrology(dob: str, tob: str = "", question: str = "") -> Dict[str, Any]:
    # If LLM configured, use LLM with template
    sys = _cfg_get("prompt_astrology", "คุณคือหมอดูโทนี่ วิเคราะห์ดวงแบบโครงสร้าง ขั้นตอน กระชับ")
    user_prompt = f"ข้อมูลวันเกิด: {dob or '-'} เวลาเกิด: {tob or '-'}\\nคำถาม: {question or '-'}\\nโปรดสรุป: โฟกัสหลัก / ระดับดวง / คำแนะนำปฏิบัติ"
    try:
        text = _try_llm(sys, user_prompt)
        if text:
            return {"llm": True, "result": text}
    except Exception:
        pass

    # fallback rule-based
    try:
        dt = datetime.datetime.strptime(dob, "%Y-%m-%d")
    except Exception:
        # fallback try DD/MM/YYYY
        try:
            dd, mm, yy = dob.split("/")
            dt = datetime.datetime(int(yy), int(mm), int(dd))
        except Exception:
            dt = datetime.datetime.now()
    seed = dt.year * 10000 + dt.month * 100 + dt.day
    digit = _reduce_to_single_digit(seed)
    colors = _lucky_colors(digit)
    level = _fortune_level(seed + len(question or ""))
    themes = {
        1: "ภาวะผู้นำและการเริ่มต้นสิ่งใหม่",
        2: "การทำงานเป็นทีมและความสัมพันธ์",
        3: "ความคิดสร้างสรรค์และการสื่อสาร",
        4: "ความมั่นคง ระเบียบ วางระบบ",
        5: "การเปลี่ยนแปลงและการเรียนรู้",
        6: "ความรัก ความกลมเกลียว และบ้าน",
        7: "การค้นหาความหมายภายใน",
        8: "การเงิน อำนาจ และการจัดการทรัพยากร",
        9: "การให้ การเยียวยา และภาพรวมชีวิต",
    }
    advice = {
        "ดีมาก": "ช่วงนี้เหมาะในการเริ่มต้น/ยกระดับ เป้าหมายชัดลงมือทันที",
        "ดี": "ราบรื่นถ้าจัดลำดับดี เน้นสื่อสารและประสานงาน",
        "ปานกลาง": "ค่อยเป็นค่อยไป แก้ทีละจุด อย่ากังวลกับรายละเอียดเล็กน้อย",
        "ควรระวัง": "ชะลอการตัดสินใจสำคัญ เตรียมแผนสำรองและเก็บพลัง",
    }
    return {
        "score": digit,
        "fortune_level": level,
        "lucky_colors": colors,
        "focus_theme": themes.get(digit),
        "advice": advice.get(level),
        "note": "การวิเคราะห์นี้เป็นแนวทางภาพรวม โปรดใช้วิจารณญาณ",
    }

def draw_tarot(n: int = 3) -> List[Tuple[str, str]]:
    n = max(1, min(10, n))
    cards = random.sample(MAJOR_ARCANA, k=min(n, len(MAJOR_ARCANA)))
    out = []
    for c in cards:
        hint = TAROT_HINTS.get(c, "")
        if random.random() < 0.5:
            c = c + " (กลับหัว)"
            hint = hint + " — มีเงื่อนไข/ต้องทบทวนบทเรียนเดิม"
        out.append((c, hint))
    return out

def analyze_tarot(n: int, question: str = "") -> Dict[str, Any]:
    cards = draw_tarot(n)
    sys = _cfg_get("prompt_tarot", "คุณคือหมอดูโทนี่ ตีความไพ่ยิปซีแบบโครงสร้าง")
    try:
        prompt = f"คำถาม: {question or '-'}\\nผลการสุ่มไพ่: " + \\
                 ", ".join([c for c, _ in cards]) + "\\nโปรดสรุปแนวโน้มและคำแนะนำ"
        text = _try_llm(sys, prompt)
        if text:
            return {"llm": True, "cards": cards, "result": text}
    except Exception:
        pass
    # fallback
    summary = "คำถาม: " + (question or "-") + " | สาระ: "
    if any("Sun" in c[0] or "Star" in c[0] or "Wheel" in c[0] for c in cards):
        trend = "แนวโน้มบวก เปิดทางก้าวหน้า"
    elif any("Tower" in c[0] or "Devil" in c[0] or "Moon" in c[0] for c in cards):
        trend = "มีจุดเปราะบาง ต้องตั้งสติและค่อยๆ ปรับ"
    else:
        trend = "สมดุล ต้องจัดการรายละเอียดให้ลงตัว"
    return {"cards": cards, "trend": trend, "summary": summary}

def analyze_dice(rolls: int = 3) -> Dict[str, Any]:
    rolls = max(1, min(6, rolls))
    nums = [random.randint(1, 6) for _ in range(rolls)]
    try:
        sys = _cfg_get("prompt_dice", "")
        if sys and llm_client:
            prompt = f"ผลทอยลูกเต๋า: {nums} โปรดสรุปแนวโน้มและคำแนะนำ"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "dice": nums, "result": txt}
    except Exception:
        pass
    s = sum(nums)
    if s <= 7:
        meaning = "คำตอบเอนเอียงไปทาง 'ชะลอ/ทบทวน' ก่อน"
    elif s <= 13:
        meaning = "มีโอกาสก้าวหน้า หากเตรียมแผนและทีมให้พร้อม"
    else:
        meaning = "โอกาสดี กล้าเริ่มได้ แต่รักษาวินัย"
    return {"dice": nums, "sum": s, "meaning": meaning}

def analyze_siamsee() -> Dict[str, Any]:
    num = random.randint(1, 100)
    try:
        sys = _cfg_get("prompt_siamsee", "")
        if sys and llm_client:
            prompt = f"เลขเซียมซี: {num} โปรดตีความระดับดวงและข้อควรทำ"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "stick": num, "result": txt}
    except Exception:
        pass
    level = _fortune_level(num)
    brief = {
        "ดีมาก": "ดวงขึ้น งาน/รัก/เงินเดินหน้า",
        "ดี": "คืบหน้าได้ แต่ต้องสม่ำเสมอ",
        "ปานกลาง": "วางแผนเพิ่ม คุมค่าใช้จ่าย",
        "ควรระวัง": "อย่าใจร้อน ระวังสัญญา/เอกสาร",
    }
    return {"stick": num, "fortune_level": level, "meaning": brief[level]}

def analyze_pok(n: int = 3) -> Dict[str, Any]:
    # Simulate Thai 'pok deng' fortune: ranks and hints
    ranks = ["ดอกจิก", "โพธิ์แดง", "ข้าวหลามตัด", "โพธิ์ดำ"]
    values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    cards = [random.choice(values) + " " + random.choice(ranks) for _ in range(max(1, min(5, n)))]
    try:
        sys = _cfg_get("prompt_pok", "")
        if sys and llm_client:
            prompt = f"ชุดไพ่ป๊อก: {cards} โปรดสรุปแนวโน้มและคำแนะนำ"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "cards": cards, "result": txt}
    except Exception:
        pass
    total_hint = "แต้มรวมอยู่ในเกณฑ์ " + random.choice(["ดี", "พอใช้", "ควรระวัง"])
    return {"cards": cards, "summary": total_hint}

def analyze_palm_face(kind: str) -> Dict[str, Any]:
    sys = _cfg_get("prompt_palm" if kind == "palm" else "prompt_face", "")
    try:
        if sys and llm_client:
            # vision path should be provided by caller via payload["image_path"] if needed, but engine_dispatch wraps it.
            # here we just return a marker for vision to handle in engine_dispatch
            pass
    except Exception:
        pass
    if kind == "palm":
        traits = [
            "เส้นวาสนาชัด มีโอกาสเติบโตในงาน",
            "เส้นหัวใจลึก ให้ความสำคัญกับความสัมพันธ์",
            "เส้นสมองเรียว สื่อถึงวิธีคิดเป็นระบบ",
        ]
    else:
        traits = [
            "ตาเป็นประกาย มีแรงบันดาลใจและพลังใจ",
            "โหนกแก้มชัด มีภาวะผู้นำและการผลักดัน",
            "ริมฝีปากอิ่ม มีเสน่ห์และการสื่อสาร",
        ]
    return {"traits": traits, "advice": "การอ่านจากภาพเป็นเพียงแนวโน้ม ต้องดูองค์รวมและสภาพแวดล้อม"}

def analyze_dream(text: str) -> Dict[str, Any]:
    sys = _cfg_get("prompt_dream", "")
    if sys and llm_client:
        try:
            prompt = f"ความฝัน: {text}"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "result": txt}
        except Exception:
            pass
    text_l = (text or "").lower()
    if any(k in text_l for k in ["งู", "snake"]):
        meaning = "งูมักสื่อถึงการเปลี่ยนแปลง/คู่ครอง/ปมในใจ"
    elif any(k in text_l for k in ["ฟัน", "tooth", "ฟันหัก"]):
        meaning = "ฟันสะท้อนความกังวลเรื่องภาพลักษณ์/การสื่อสาร"
    elif any(k in text_l for k in ["ทะเล", "น้ำ", "คลื่น"]):
        meaning = "น้ำหมายถึงอารมณ์ที่กำลังเคลื่อนไหว ควรตั้งหลัก"
    else:
        meaning = "เป็นสัญญาณให้สำรวจอารมณ์ลึกๆ ก่อนตัดสินใจสำคัญ"
    return {"meaning": meaning, "note": "บันทึกความฝันต่อเนื่องจะช่วยให้ตีความแม่นยำขึ้น"}

def analyze_phone(number: str) -> Dict[str, Any]:
    sys = _cfg_get("prompt_phone", "")
    if sys and llm_client:
        try:
            prompt = f"เบอร์โทรศัพท์: {number} โปรดวิเคราะห์ในเชิงตัวเลขพร้อมคำแนะนำ"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "result": txt}
        except Exception:
            pass
    digits = [int(ch) for ch in number if ch.isdigit()]
    total = sum(digits)
    root = _reduce_to_single_digit(total)
    areas = {
        1: "ผู้นำ/ความกล้าหาญ",
        2: "ทีมเวิร์ก/ความสัมพันธ์",
        3: "สื่อสาร/ความคิดสร้างสรรค์",
        4: "วินัย/ระบบ/ความมั่นคง",
        5: "เรียนรู้/ปรับตัว",
        6: "รัก/ครอบครัว/เสน่ห์",
        7: "ค้นหาความหมาย/ปัญญา",
        8: "การเงิน/อำนาจ/ธุรกิจ",
        9: "เมตตา/ภาพรวม/จิตวิญญาณ"
    }
    return {
        "sum": total,
        "root": root,
        "focus": areas.get(root),
        "advice": "เน้นใช้เบอร์นี้ในงานที่สอดคล้องกับจุดแข็ง จะส่งพลังบวกมากขึ้น"
    }

def analyze_license(text: str) -> Dict[str, Any]:
    sys = _cfg_get("prompt_license", "")
    if sys and llm_client:
        try:
            prompt = f"เลขทะเบียนรถ: {text} โปรดแปลความหมาย, วันมงคล และข้อควรระวัง"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "result": txt}
        except Exception:
            pass
    digits = [int(ch) for ch in text if ch.isdigit()]
    total = sum(digits)
    root = _reduce_to_single_digit(total)
    good_days = ["จันทร์", "พุธ", "ศุกร์"] if root % 2 == 1 else ["อังคาร", "พฤหัส", "เสาร์"]
    return {
        "sum": total,
        "root": root,
        "good_days": good_days,
        "tip": "หมั่นตรวจสภาพรถและทำบุญเสริมดวงการเดินทาง"
    }

def analyze_name(name: str, dob: str = "") -> Dict[str, Any]:
    sys = _cfg_get("prompt_name", "")
    if sys and llm_client:
        try:
            prompt = f"ชื่อ-นามสกุล: {name} วันเกิด: {dob or '-'} โปรดวิเคราะห์ภาพรวมชีวิต/งาน/ความรัก และคำแนะนำ"
            txt = _try_llm(sys, prompt)
            if txt:
                return {"llm": True, "result": txt}
        except Exception:
            pass
    if not name:
        return {"score": 0, "meaning": "กรุณาระบุชื่อ"}
    # Simple latin-thai mapping by codepoints
    s = sum(ord(ch) for ch in name if ch.isalpha())
    score = _reduce_to_single_digit(s)
    themes = {
        1: "ผู้นำ/เริ่มต้น", 2: "ร่วมมือ/สัมพันธ์", 3: "สื่อสาร/แสดงออก",
        4: "มั่นคง/วางระบบ", 5: "เรียนรู้/เดินทาง", 6: "เมตตา/ดูแล",
        7: "ลึกซึ้ง/วิจัย", 8: "อำนาจ/ธุรกิจ", 9: "อุดมการณ์/เสียสละ",
    }
    return {"score": score, "theme": themes.get(score), "advice": "เลือกลายเซ็น/นามบัตรให้สะท้อนธีมนี้"}

def engine_dispatch(service: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    service:
      - astrology
      - tools: tarot|dice|siamsee|pok
      - analysis: palm|face|dream
      - numbers: phone|license|name
    """
    if service == "astrology":
        return analyze_astrology(payload.get("dob", ""), payload.get("tob", ""), payload.get("question", ""))
    if service == "tools":
        kind = (payload.get("kind") or "tarot").lower()
        if kind == "tarot":
            n = int(payload.get("cards", 3) or 3)
            return analyze_tarot(n, payload.get("question", ""))
        if kind == "dice":
            r = int(payload.get("rolls", 3) or 3)
            return analyze_dice(r)
        if kind == "siamsee":
            return analyze_siamsee()
        if kind == "pok":
            n = int(payload.get("cards", 3) or 3)
            return analyze_pok(n)
        return {"error": "unknown tools kind"}
    if service == "analysis":
        kind = (payload.get("kind") or "palm").lower()
        if kind in ("palm", "face"):
            # If LLM + vision available, use it
            sys = _cfg_get("prompt_palm" if kind == "palm" else "prompt_face", "")
            image_path = payload.getysis kind"}
    if service == "numbers":
        kind = (payload.get("kind") or "phone").lower()
        if kind == "phone":
            return analyze_phone(payload.get("number", ""))
        if kind == "license":
            return analyze_license(payload.get("text", ""))
        if kind == "name":
            return analyze_name(payload.get("name", ""), payload.get("dob", ""))
        return {"error": "unknown numbers kind"}
    return {"error": "unknown service"}