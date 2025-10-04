import os
from typing import Optional

# Optional Gemini (google-generativeai)
_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _gemini_predict(prompt: str) -> Optional[str]:
    if not _GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=_GEMINI_API_KEY)
        model = genai.GenerativeModel(_GEMINI_MODEL)
        resp = model.generate_content(prompt)
        # google-generativeai returns text in resp.text for simple usage
        return getattr(resp, "text", None) or None
    except Exception:
        return None


def generate_divination(user: str, div_type: str, text: str) -> str:
    """Return AI-generated divination text or fallback."""
    base_prompt = f"""คุณคือหมอดูไทยชื่อ 'อ.โทนี่สะท้อนกรรม' เชี่ยวชาญ {div_type}.
ผู้ใช้: {user}
คำถาม/ข้อมูล: {text}
รูปแบบคำตอบ: กระชับ, นุ่มนวล, ให้กำลังใจ, มีเหตุผลเชิงโหราศาสตร์/ตัวเลข/ไพ่ยิปซีตามประเภทที่ระบุ, ปิดท้ายด้วยข้อเสนอแนะเชิงปฏิบัติ 2-3 ข้อ.
ภาษา: ไทย.
"""
    result = None
    if _PROVIDER == "gemini":
        result = _gemini_predict(base_prompt)

    # Fallback to local content generator (playful style) if AI not available
    if not result:
        try:
            import content_generator as cg
            result = cg.make_text(sender=os.getenv("SENDER_NAME", "อ.โทนี่สะท้อนกรรม"))
            result = f"({div_type}) ผลคำทำนายจำลอง:\n{result}"
        except Exception:
            result = f"({div_type}) ผลคำทำนายจำลองสำหรับ: \"{text}\" — โปรดเชื่อมต่อโมเดล AI จริง"

    return result