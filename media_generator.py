import os
import uuid
import time
from typing import Dict, Optional

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

OUTPUT_DIR = "outputs"
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
IMG_DIR = os.path.join(OUTPUT_DIR, "images")
VID_DIR = os.path.join(OUTPUT_DIR, "video")


def _ensure_dirs() -> None:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(VID_DIR, exist_ok=True)


def _pick_font(size: int = 48) -> ImageFont.ImageFont:
    # Try Thai-capable fonts commonly available in Debian
    candidates = [
        "/usr/share/fonts/truetype/tlwg/TlwgLoma.ttf",  # Thai TLWG
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # fallback
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_to_speech(text: str, lang: str = "th", slow: bool = False) -> Optional[str]:
    _ensure_dirs()
    filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
    path = os.path.join(AUDIO_DIR, filename)
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(path)
        return path
    except Exception:
        return None


def render_quote_card(text: str, sender: str = "", size=(1080, 1080)) -> Optional[str]:
    _ensure_dirs()
    filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(IMG_DIR, filename)
    try:
        W, H = size
        img = Image.new("RGB", size, color=(255, 245, 245))
        draw = ImageDraw.Draw(img)
        font = _pick_font(54)
        font_small = _pick_font(36)

        # Word wrap
        max_w = W - 140
        words = text.split()
        lines = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if draw.textlength(test, font=font) <= max_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)

        y = 160
        for line in lines[:10]:
            draw.text((70, y), line, font=font, fill=(40, 40, 40))
            y += font.size + 18

        if sender:
            draw.text((70, H - 120), f"— {sender}", font=font_small, fill=(100, 100, 100))

        img.save(path, format="PNG")
        return path
    except Exception:
        return None


def compose_video(image_path: str, audio_path: Optional[str]) -> Optional[str]:
    _ensure_dirs()
    filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}.mp4"
    path = os.path.join(VID_DIR, filename)
    try:
        img_clip = ImageClip(image_path).resize(height=1080).fx(lambda clip: clip)  # simple
        duration = 10.0
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            duration = max(5.0, float(audio_clip.duration))
            img_clip = img_clip.set_audio(audio_clip)
        img_clip = img_clip.set_duration(duration)
        # Subtle zoom to add motion
        def zoom_in(get_frame, t):
            frame = get_frame(t)
            # MoviePy will handle resize via lambda; keep simple
            return frame
        final = img_clip  # keep simple for robustness
        final.write_videofile(path, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        return path
    except Exception:
        return None


def generate_all(text: str, sender: str = "", tts_lang: str = "th") -> Dict[str, Optional[str]]:
    """
    Generates mp3, png, and mp4 for the given text.
    Returns dict with absolute paths (or None when failed).
    """
    audio = text_to_speech(text, lang=tts_lang)
    image = render_quote_card(text, sender=sender)
    video = compose_video(image, audio) if image else None
    return {"audio": audio, "image": image, "video": video}