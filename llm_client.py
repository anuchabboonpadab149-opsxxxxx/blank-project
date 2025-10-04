import os
import base64
import json
import requests
from typing import Optional, Dict, Any, List

# Minimal LLM client supporting OpenAI (chat.completions) and Gemini (generative language) via HTTP.
# Uses environment variables set via credentials dashboard:
#   LLM_PROVIDER=openai|gemini
#   OPENAI_API_KEY, OPENAI_MODEL (default: gpt-4o-mini)
#   GEMINI_API_KEY, GEMINI_MODEL (default: gemini-1.5-flash)
#
# For vision, we support:
#   - OpenAI: content array with image_url or image base64
#   - Gemini: "inline_data" with base64 image

def _provider() -> str:
    p = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    if p in ("openai", "gemini"):
        return p
    # auto-detect
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    return ""

def _openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def call_llm_text(prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 800) -> str:
    prov = _provider()
    if prov == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise RuntimeError("OPENAI_API_KEY missing")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": _openai_model(),
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        return (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    elif prov == "gemini":
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise RuntimeError("GEMINI_API_KEY missing")
        model = _gemini_model()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [
                {"parts": ([{"text": system}] if system else []) + [{"text": prompt}]}
            ],
            "generationConfig": {"temperature": float(temperature), "maxOutputTokens": int(max_tokens)}
        }
        r = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        cands = data.get("candidates") or []
        parts = (cands[0].get("content", {}).get("parts") if cands else []) or []
        out = "".join(p.get("text", "") for p in parts)
        return out.strip()
    else:
        raise RuntimeError("No LLM provider configured")

def _read_image_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def call_llm_vision(prompt: str, image_path: Optional[str], system: Optional[str] = None, temperature: float = 0.6, max_tokens: int = 800) -> str:
    prov = _provider()
    if not image_path:
        # fallback to text call
        return call_llm_text(prompt, system=system, temperature=temperature, max_tokens=max_tokens)
    if prov == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise RuntimeError("OPENAI_API_KEY missing")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        img_b64 = _read_image_b64(image_path)
        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        })
        payload = {"model": _openai_model(), "messages": messages, "temperature": float(temperature), "max_tokens": int(max_tokens)}
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=90)
        r.raise_for_status()
        data = r.json()
        return (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    elif prov == "gemini":
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise RuntimeError("GEMINI_API_KEY missing")
        model = _gemini_model()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        mime = "image/jpeg"
        img_b64 = _read_image_b64(image_path)
        parts = []
        if system:
            parts.append({"text": system})
        parts.append({"text": prompt})
        parts.append({"inline_data": {"mime_type": mime, "data": img_b64}})
        payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": float(temperature), "maxOutputTokens": int(max_tokens)}}
        r = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=90)
        r.raise_for_status()
        data = r.json()
        cands = data.get("candidates") or []
        parts = (cands[0].get("content", {}).get("parts") if cands else []) or []
        out = "".join(p.get("text", "") for p in parts)
        return out.strip()
    else:
        raise RuntimeError("No LLM provider configured")