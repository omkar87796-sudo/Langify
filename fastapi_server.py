"""
FastAPI Translation Server
Run with: python fastapi_server.py
API Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import urllib.request
import urllib.parse
import json

app = FastAPI(
    title="LinguaAI Translation API",
    description="Google Translate NMT pretrained model",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGUAGES = {
    "af": "Afrikaans",        "sq": "Albanian",         "ar": "Arabic",
    "hy": "Armenian",         "az": "Azerbaijani",      "eu": "Basque",
    "be": "Belarusian",       "bn": "Bengali",          "bs": "Bosnian",
    "bg": "Bulgarian",        "ca": "Catalan",          "zh-cn": "Chinese Simplified",
    "zh-tw": "Chinese Traditional", "hr": "Croatian",   "cs": "Czech",
    "da": "Danish",           "nl": "Dutch",            "en": "English",
    "et": "Estonian",         "fi": "Finnish",          "fr": "French",
    "gl": "Galician",         "ka": "Georgian",         "de": "German",
    "el": "Greek",            "gu": "Gujarati",         "ht": "Haitian Creole",
    "ha": "Hausa",            "he": "Hebrew",           "hi": "Hindi",
    "hu": "Hungarian",        "is": "Icelandic",        "id": "Indonesian",
    "ga": "Irish",            "it": "Italian",          "ja": "Japanese",
    "kn": "Kannada",          "kk": "Kazakh",           "ko": "Korean",
    "lv": "Latvian",          "lt": "Lithuanian",       "mk": "Macedonian",
    "ms": "Malay",            "ml": "Malayalam",        "mt": "Maltese",
    "mr": "Marathi",          "mn": "Mongolian",        "ne": "Nepali",
    "no": "Norwegian",        "fa": "Persian",          "pl": "Polish",
    "pt": "Portuguese",       "pa": "Punjabi",          "ro": "Romanian",
    "ru": "Russian",          "sr": "Serbian",          "si": "Sinhala",
    "sk": "Slovak",           "sl": "Slovenian",        "es": "Spanish",
    "sw": "Swahili",          "sv": "Swedish",          "tl": "Filipino",
    "ta": "Tamil",            "te": "Telugu",           "th": "Thai",
    "tr": "Turkish",          "uk": "Ukrainian",        "ur": "Urdu",
    "uz": "Uzbek",            "vi": "Vietnamese",       "cy": "Welsh",
    "yi": "Yiddish",          "zu": "Zulu",
}


# ── Pydantic Models ──────────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str
    dest: str = "en"
    src: Optional[str] = "auto"

class TranslateResponse(BaseModel):
    original: str
    translated: str
    src_lang_code: str
    src_lang_name: str
    dest_lang_code: str
    dest_lang_name: str

class DetectRequest(BaseModel):
    text: str

class DetectResponse(BaseModel):
    lang_code: str
    lang_name: str
    confidence: Optional[float] = None


# ── Core translation using Google Translate API directly ─────────────────────

def google_translate(text: str, dest: str, src: str = "auto") -> dict:
    """
    Call Google Translate using urllib (no third-party library needed).
    Returns dict with keys: translated, src_lang
    """
    base_url = "https://translate.googleapis.com/translate_a/single"
    params = urllib.parse.urlencode({
        "client": "gtx",
        "sl": src,
        "tl": dest,
        "dt": "t",
        "q": text,
    })
    url = f"{base_url}?{params}"

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0"
    })

    with urllib.request.urlopen(req, timeout=10) as response:
        raw = response.read().decode("utf-8")

    data = json.loads(raw)

    # Extract translated text
    translated = ""
    for block in data[0]:
        if block[0]:
            translated += block[0]

    # Extract detected source language
    src_lang = data[2] if len(data) > 2 and data[2] else src

    return {
        "translated": translated,
        "src_lang": src_lang,
    }


def google_detect(text: str) -> dict:
    """Detect language using Google Translate API."""
    result = google_translate(text, dest="en", src="auto")
    return {"lang_code": result["src_lang"]}


# ── Helper ───────────────────────────────────────────────────────────────────

def resolve_lang_code(code_or_name: str) -> str:
    val = code_or_name.lower().strip()
    if val in LANGUAGES:
        return val
    for k, v in LANGUAGES.items():
        if v.lower() == val:
            return k
    return val


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "LinguaAI Translation API is running!"}


@app.get("/languages")
def get_languages():
    langs = sorted(
        [{"code": k, "name": v} for k, v in LANGUAGES.items()],
        key=lambda x: x["name"]
    )
    return {"languages": langs, "count": len(langs)}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    dest_code = resolve_lang_code(req.dest)
    if dest_code not in LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unknown language: '{req.dest}'")

    src_arg = "auto" if not req.src or req.src == "auto" else resolve_lang_code(req.src)

    try:
        result = google_translate(text, dest=dest_code, src=src_arg)

        src_code = result["src_lang"]
        src_name = LANGUAGES.get(src_code, src_code.upper())
        dest_name = LANGUAGES.get(dest_code, dest_code.upper())

        return TranslateResponse(
            original=text,
            translated=result["translated"],
            src_lang_code=src_code,
            src_lang_name=src_name,
            dest_lang_code=dest_code,
            dest_lang_name=dest_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@app.post("/detect", response_model=DetectResponse)
def detect(req: DetectRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        result = google_detect(text)
        lang_code = result["lang_code"]
        lang_name = LANGUAGES.get(lang_code, lang_code.upper())

        return DetectResponse(
            lang_code=lang_code,
            lang_name=lang_name,
            confidence=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  ⚡  FastAPI server starting...")
    print("  📡  API:      http://localhost:8000")
    print("  📖  Swagger:  http://localhost:8000/docs\n")
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8000, reload=True)
