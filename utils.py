import numpy as np
import colorsys


def generate_palette(mood: str, intensity: float):
    """
    Generate a soft color palette (3–5 colors) based on mood and intensity.
    Output format: [(r, g, b), ...] with values 0–255.
    """

    # Base HSV for different moods
    mood_to_hsv = {
        "calm":      (200 / 360, 0.25, 0.95),  # blue-green
        "nostalgic": (35  / 360, 0.35, 0.96),  # warm yellow-orange
        "dreamy":    (260 / 360, 0.30, 0.98),  # purple-blue
        "sad":       (210 / 360, 0.22, 0.90),  # dark blue
        "happy":     (50  / 360, 0.45, 0.99),  # bright yellow
        "romantic":  (330 / 360, 0.35, 0.97),  # pink-purple
        "tense":     (350 / 360, 0.60, 0.92),  # red-ish
    }

    base_h, base_s, base_v = mood_to_hsv.get(mood, mood_to_hsv["calm"])
    colors = []
    num_colors = np.random.randint(3, 6)

    for _ in range(num_colors):
        # Add variation for more diverse colors
        h = (base_h + np.random.uniform(-0.12, 0.12)) % 1.0
        s = np.clip(base_s + np.random.uniform(-0.25, 0.2), 0.05, 0.95)
        v = np.clip(base_v + np.random.uniform(-0.2, 0.2), 0.4, 1.0)

        # Higher intensity → stronger contrast and slightly darker tones
        v *= (0.9 - 0.3 * intensity)

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))

    return colors


def analyze_memory_local(city: str, memory: str):
    """
    Local emotional analysis (no API needed).
    Uses keyword matching + punctuation + text length to estimate mood and intensity.
    """

    text = (city + " " + memory).lower()

    mood = "calm"
    intensity = 0.4

    # Strong emotional keyword groups
    sad_words = ["sad", "cry", "alone", "lonely", "lost", "empty", "寂寞", "失落", "难过"]
    happy_words = ["happy", "joy", "excited", "smile", "满足", "开心", "快乐"]
    romantic_words = ["romantic", "love", "kiss", "date", "牵手", "告白", "浪漫"]
    nostalgic_words = ["nostalgic", "memory", "childhood", "old", "过去", "从前", "回忆"]
    dreamy_words = ["dream", "dreamy", "fog", "mist", "night", "neon", "幻", "朦胧"]
    tense_words = ["fight", "argue", "anxious", "压力", "紧张", "争吵"]

    def contains_any(words):
        return any(w in text for w in words)

    # Determine mood
    if contains_any(sad_words):
        mood = "sad"
        intensity = 0.7
    elif contains_any(happy_words):
        mood = "happy"
        intensity = 0.6
    elif contains_any(romantic_words):
        mood = "romantic"
        intensity = 0.55
    elif contains_any(nostalgic_words):
        mood = "nostalgic"
        intensity = 0.6
    elif contains_any(dreamy_words):
        mood = "dreamy"
        intensity = 0.65
    elif contains_any(tense_words):
        mood = "tense"
        intensity = 0.7
    else:
        # Neutral mood hints
        if any(w in text for w in ["rain", "fog", "mist", "雨", "雾"]):
            mood = "nostalgic"
            intensity = 0.55
        elif any(w in text for w in ["sea", "ocean", "港口", "海边", "海"]):
            mood = "calm"
            intensity = 0.5
        elif any(w in text for w in ["night", "灯光", "城市", "霓虹"]):
            mood = "dreamy"
            intensity = 0.6

    # Adjust intensity based on text length + exclamation marks
    length_factor = min(len(memory) / 400.0, 1.0)
    exclam = memory.count("!") + memory.count("！")
    intensity += 0.1 * length_factor + 0.05 * exclam
    intensity = float(np.clip(intensity, 0.3, 0.85))

    # Generate palette using detected mood
    palette = generate_palette(mood, intensity)

    return {
        "city": city,
        "mood": mood,
        "intensity": intensity,
        "palette": palette,
        "summary": f"The memory of {city} presents a {mood} emotional tone with intensity around {intensity:.2f}.",
    }
