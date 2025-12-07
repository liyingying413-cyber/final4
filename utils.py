
import hashlib
from typing import Dict, List, Tuple

import numpy as np

RGB = Tuple[int, int, int]


def _hex_to_rgb_list(hex_list: List[str]) -> List[RGB]:
    out: List[RGB] = []
    for hx in hex_list:
        h = hx.lstrip("#")
        if len(h) != 6:
            continue
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        out.append((r, g, b))
    return out


def _emotion_from_text(text: str) -> str:
    t = text.lower()
    pos = ["warm", "sun", "spring", "smile", "friends", "love", "cozy", "light"]
    sad = ["winter", "cold", "alone", "rain", "snow", "goodbye", "leaving", "empty"]
    tense = ["crowded", "traffic", "noise", "anxious", "lost", "rush", "late"]
    joy_score = sum(w in t for w in pos)
    sad_score = sum(w in t for w in sad)
    tense_score = sum(w in t for w in tense)
    if joy_score >= sad_score and joy_score >= tense_score:
        return "warm"
    if sad_score >= joy_score and sad_score >= tense_score:
        return "melancholic"
    return "tense"


def local_analyze(city: str, memory_text: str) -> Dict:
    """Light‑weight local 'AI analysis' without any external API."""
    base_title = f"Memory of {city.strip() or 'the city'}"

    mood_label = _emotion_from_text(memory_text + " " + city)
    if mood_label == "warm":
        palette_hex = ["#FFE3C2", "#FFB7C5", "#FFF5D6"]
        intensity = 0.45
        mood_desc = "warm / hopeful"
    elif mood_label == "melancholic":
        palette_hex = ["#A9C8FF", "#D5E0F2", "#6E8BB5"]
        intensity = 0.6
        mood_desc = "calm / nostalgic"
    else:
        palette_hex = ["#F8E078", "#FF9E6B", "#F4F1E8"]
        intensity = 0.7
        mood_desc = "tense / vibrant"

    palette_rgb = _hex_to_rgb_list(palette_hex)

    # crude 'city keywords' for report only
    city_kw = []
    lower = (city + " " + memory_text).lower()
    for kw in ["river", "bridge", "station", "market", "subway", "cafe", "beach", "mountain"]:
        if kw in lower:
            city_kw.append(kw)

    summary = (
        f"In this {city or 'city'} memory, the dominant feeling is {mood_desc} "
        f"with an intensity of about {intensity:.2f}."
    )

    return {
        "title": base_title,
        "subtitle": "An abstract emotional poster based purely on your text description.",
        "mood": mood_desc,
        "intensity": intensity,
        "palette_hex": palette_hex,
        "palette_rgb": palette_rgb,
        "city_keywords": city_kw,
        "typography_focus": "balanced",
        "summary": summary,
    }


def auto_seed(city: str, memory_text: str) -> int:
    """Deterministic seed from city + memory text."""
    s = (city.strip() + "|" + memory_text.strip()).encode("utf-8")
    h = hashlib.sha256(s).hexdigest()
    return int(h[:8], 16) % 100000
