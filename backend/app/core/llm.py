import json
from typing import Dict, Any, Optional
import httpx
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


def call_llm(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.2,
    max_tokens: int = 2000,
    json_mode: bool = False,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """
    Unified LLM invocation supporting Local Models (Ollama, LM Studio) and Google Gemini.
    Prioritizes local model execution for full privacy and zero cloud dependence.
    """
    provider = (settings.LLM_PROVIDER or "ollama").lower()
    local_model = settings.LOCAL_MODEL_NAME or "qwen3:4b"

    # 1. Attempt Local Ollama / Local Server
    if provider in ("ollama", "local", "auto"):
        try:
            ollama_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
            payload: Dict[str, Any] = {
                "model": local_model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            if json_mode:
                payload["format"] = "json"

            with httpx.Client(timeout=timeout) as client:
                resp = client.post(ollama_url, json=payload)
                if resp.status_code == 200:
                    raw_data = resp.json()
                    text_resp = raw_data.get("response", "").strip()
                    logger.info("Ollama raw response: done=%s, done_reason=%s, raw_len=%d, preview=%r", raw_data.get("done"), raw_data.get("done_reason"), len(text_resp), text_resp[:100])
                    # Strip reasoning tags if present from Qwen models without deleting entire answer
                    if "<think>" in text_resp:
                        import re
                        cleaned = re.sub(r"<think>.*?</think>", "", text_resp, flags=re.DOTALL).strip()
                        if cleaned:
                            text_resp = cleaned
                        else:
                            text_resp = text_resp.replace("<think>", "").replace("</think>", "").strip()
                    logger.info("Local Ollama model '%s' generated response (%d chars)", local_model, len(text_resp))
                    return {
                        "text": text_resp,
                        "provider": "Ollama (Local)",
                        "model": local_model,
                        "success": True,
                    }
                else:
                    logger.warning("Ollama returned HTTP %d: %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.warning("Local Ollama execution failed (%s); trying fallback provider.", e)

    # 2. Attempt Google Gemini if configured
    gemini_key = settings.GEMINI_API_KEY
    if gemini_key:
        try:
            model = settings.LLM_MODEL or "gemini-2.5-flash"
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
            gemini_payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"System Instructions:\n{system_prompt}\n\nTask:\n{prompt}" if system_prompt else prompt}
                        ],
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }
            if json_mode:
                gemini_payload["generationConfig"]["responseMimeType"] = "application/json"

            with httpx.Client(timeout=timeout) as client:
                resp = client.post(gemini_url, json=gemini_payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        logger.info("Google Gemini model '%s' generated response (%d chars)", model, len(text))
                        return {
                            "text": text,
                            "provider": "Google Gemini",
                            "model": model,
                            "success": True,
                        }
        except Exception as e:
            logger.warning("Google Gemini execution failed (%s); returning fallback.", e)

    return {
        "text": "",
        "provider": "Deterministic Fallback",
        "model": "rule-engine",
        "success": False,
    }
