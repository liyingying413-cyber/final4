
import io
import random
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageDraw

RGB = Tuple[int, int, int]


def _to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _normalize_palette(palette) -> List[RGB]:
    """Normalize palette into a list of RGB tuples."""
    if palette is None:
        return [(200, 220, 230), (230, 240, 245), (180, 200, 210)]

    if isinstance(palette, np.ndarray):
        palette = palette.tolist()

    if not palette:
        return [(200, 220, 230), (230, 240, 245), (180, 200, 210)]

    # single flat list like [r,g,b]
    if isinstance(palette[0], (int, float)):
        if len(palette) >= 3:
            return [(int(palette[0]), int(palette[1]), int(palette[2]))]
        v = int(palette[0])
        return [(v, v, v)]

    norm: List[RGB] = []
    for c in palette:
        if isinstance(c, (list, tuple)) and len(c) >= 3:
            r, g, b = c[:3]
            norm.append((int(r), int(g), int(b)))

    if not norm:
        norm = [(200, 220, 230), (230, 240, 245), (180, 200, 210)]

    return norm


def _lerp_color(c1: RGB, c2: RGB, t: float) -> RGB:
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
    )


def _base_gradient(size: int, palette, mood_intensity: float) -> Image.Image:
    palette = _normalize_palette(palette)
    if len(palette) == 1:
        palette = [palette[0], palette[0], palette[0]]
    elif len(palette) == 2:
        palette = [palette[0], palette[1], palette[0]]

    c1, c2, c3 = palette[0], palette[1], palette[2]

    w = h = size
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            tx = x / (w - 1)
            ty = y / (h - 1)
            d = ((x - w / 2) ** 2 + (y - h / 2) ** 2) ** 0.5 / (0.75 * w)
            d = max(0.0, min(1.0, d))
            t_diag = (tx + ty) / 2.0
            cd = _lerp_color(c1, c2, t_diag)
            factor = (1.0 - d) * (0.3 + 0.7 * mood_intensity)
            cf = _lerp_color(cd, c3, factor)
            arr[y, x] = cf

    img = Image.fromarray(arr, mode="RGB")
    return img.filter(ImageFilter.GaussianBlur(radius=1.5))


def _apply_mist(img: Image.Image, strength: float, smoothness: float, glow: float) -> Image.Image:
    if strength <= 0 and glow <= 0:
        return img

    w, h = img.size
    base = img.convert("RGB")

    if strength > 0:
        noise = np.random.rand(h, w).astype("float32")
        mist = Image.fromarray((noise * 255).astype("uint8"), mode="L")
        mist = mist.filter(ImageFilter.GaussianBlur(radius=15 + smoothness * 25))
        mist_rgb = Image.merge("RGB", (mist, mist, mist))
        white = Image.new("RGB", (w, h), (235, 238, 247))
        mist_rgb = Image.blend(white, mist_rgb, alpha=0.4)
        alpha = min(0.6, 0.15 + strength * 0.35)
        base = Image.blend(base, mist_rgb, alpha=alpha)

    if glow > 0:
        glow_layer = base.filter(ImageFilter.GaussianBlur(radius=6 + glow * 20))
        glow_layer = Image.blend(base, glow_layer, alpha=0.55)
        arr = np.array(glow_layer).astype("float32")
        arr *= 1.05 + glow * 0.2
        arr = np.clip(arr, 0, 255).astype("uint8")
        glow_layer = Image.fromarray(arr, mode="RGB")
        base = Image.blend(base, glow_layer, alpha=0.55)

    return base


def _apply_watercolor(img: Image.Image, palette, spread: float, layers: int, saturation: float) -> Image.Image:
    if spread <= 0 or layers <= 0:
        return img

    palette = _normalize_palette(palette)
    w, h = img.size
    base = img.convert("RGB")

    for _ in range(layers):
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        n_blobs = int(15 + spread * 35)
        for _ in range(n_blobs):
            r, g, b = random.choice(palette)
            r = int(r + (255 - r) * (0.4 * (1 - saturation)))
            g = int(g + (255 - g) * (0.4 * (1 - saturation)))
            b = int(b + (255 - b) * (0.4 * (1 - saturation)))
            cx = random.randint(0, w)
            cy = random.randint(0, h)
            max_r = int(min(w, h) * (0.22 + spread * 0.35))
            rx = random.randint(int(max_r * 0.25), max_r)
            ry = random.randint(int(max_r * 0.25), max_r)
            alpha = int(70 + 110 * random.random())
            bbox = (cx - rx, cy - ry, cx + rx, cy + ry)
            draw.ellipse(bbox, fill=(r, g, b, alpha))

        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=8 + spread * 30))
        base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")

    return base


def _apply_pastel(img: Image.Image, softness: float, grain: float, blend_ratio: float) -> Image.Image:
    base = img.convert("RGB")
    w, h = base.size

    if softness > 0:
        soft = base.filter(ImageFilter.GaussianBlur(radius=1.5 + softness * 6))
    else:
        soft = base

    arr = np.array(soft).astype("float32")
    arr *= 1.04
    arr = np.clip(arr, 0, 255).astype("uint8")
    soft = Image.fromarray(arr, mode="RGB")

    if grain > 0:
        noise = np.random.normal(0, grain * 12, (h, w, 1)).astype("float32")
        arr = np.array(soft).astype("float32")
        arr = arr + noise
        arr = np.clip(arr, 0, 255).astype("uint8")
        soft = Image.fromarray(arr, mode="RGB")

    overlay = Image.new("RGB", (w, h), (245, 245, 248))
    pastel = Image.blend(soft, overlay, alpha=0.18)
    return Image.blend(base, pastel, alpha=blend_ratio * 0.8)


def _city_tags(text: str):
    text = text.lower()
    tags = []
    if any(k in text for k in ["seoul", "hongdae", "gangnam", "neon", "k-pop", "kpop"]):
        tags.append("vertical_neon")
    if any(k in text for k in ["tokyo", "shibuya", "akihabara", "anime"]):
        tags.extend(["vertical_neon", "pixel_grid"])
    if any(k in text for k in ["paris", "seine", "eiffel", "louvre", "cafe"]):
        tags.append("arches")
    if any(k in text for k in ["london", "fog", "rain", "thames"]):
        tags.append("fog")
    if any(k in text for k in ["new york", "nyc", "manhattan", "times square"]):
        tags.extend(["vertical_neon", "chaos"])
    if any(k in text for k in ["beach", "ocean", "sea", "harbor", "island"]):
        tags.append("waves")
    if not tags:
        tags.append("waves")
    return tags


def _city_overlay(img: Image.Image, palette, city: str, memory: str, strength: float) -> Image.Image:
    w, h = img.size
    base = img.convert("RGB")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    tags = _city_tags(city + " " + memory)
    palette = _normalize_palette(palette)

    def pick(vivid=False):
        r, g, b = random.choice(palette)
        if vivid:
            r = min(255, int(r * 1.2))
            g = min(255, int(g * 1.2))
            b = min(255, int(b * 1.2))
        return r, g, b

    if "waves" in tags:
        for i in range(4):
            r, g, b = pick()
            alpha = int(40 + 90 * strength)
            width = int(6 + 20 * strength)
            y0 = int(h * (0.35 + 0.4 * i / 4))
            for x in range(0, w, 8):
                y = y0 + int(np.sin(x / 45.0 + i) * 18)
                draw.line([(x, y), (x + 12, y)], fill=(r, g, b, alpha), width=width)

    if "vertical_neon" in tags:
        n = int(6 + 10 * strength)
        for _ in range(n):
            r, g, b = pick(vivid=True)
            alpha = int(120 + 120 * strength)
            x = random.randint(0, w)
            top = random.randint(0, int(h * 0.1))
            bottom = random.randint(int(h * 0.6), h)
            width = random.randint(6, 14)
            draw.rectangle((x, top, x + width, bottom), fill=(r, g, b, alpha))

    if "pixel_grid" in tags:
        cell = 16
        for y in range(0, h, cell):
            for x in range(0, w, cell):
                if random.random() < 0.2 + 0.3 * strength:
                    r, g, b = pick(vivid=True)
                    alpha = int(80 + 120 * strength)
                    draw.rectangle((x, y, x + cell, y + cell), fill=(r, g, b, alpha))

    if "chaos" in tags:
        for _ in range(int(30 + 40 * strength)):
            r, g, b = pick(vivid=True)
            alpha = int(60 + 150 * strength)
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            x2 = x1 + random.randint(-110, 110)
            y2 = y1 + random.randint(-90, 90)
            draw.line((x1, y1, x2, y2), fill=(r, g, b, alpha), width=random.randint(1, 4))

    if "arches" in tags:
        base_y = int(h * 0.8)
        for i in range(3):
            r, g, b = pick()
            alpha = int(70 + 100 * strength)
            width = int(w * 0.18)
            gap = int(w * 0.05)
            cx = int(w * 0.2 + i * (width + gap))
            left = cx - width // 2
            right = cx + width // 2
            top = int(h * (0.4 + 0.1 * random.random()))
            draw.rectangle((left, (top + base_y) // 2, right, base_y), fill=(r, g, b, alpha))
            draw.ellipse((left, top, right, top + (base_y - top) // 2), fill=(r, g, b, alpha))

    if "fog" in tags:
        fog_noise = np.random.rand(h, w).astype("float32")
        fog = Image.fromarray((fog_noise * 255).astype("uint8"), mode="L")
        fog = fog.filter(ImageFilter.GaussianBlur(radius=35))
        fog_rgba = Image.merge("RGBA", (fog, fog, fog, fog))
        overlay = Image.alpha_composite(overlay, fog_rgba)

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=3))
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def generate_poster(
    city: str,
    memory_text: str,
    mood: str,
    palette,
    mood_intensity: float,
    seed: int,
    emotion_link: float,
    mist_strength: float,
    mist_smoothness: float,
    mist_glow: float,
    wc_spread: float,
    wc_layers: int,
    wc_saturation: float,
    pastel_softness: float,
    pastel_grain: float,
    pastel_blend: float,
) -> bytes:
    """End-to-end local poster generator (no API required)."""

    try:
        seed_int = int(seed)
    except Exception:
        seed_int = 42

    np.random.seed(seed_int)
    random.seed(seed_int)

    factor = 0.35 + 0.65 * emotion_link
    mist_strength *= factor * (0.7 + 0.6 * mood_intensity)
    wc_spread *= factor * (0.6 + 0.7 * mood_intensity)
    wc_layers = max(1, int(wc_layers * (0.6 + 0.8 * mood_intensity)))
    pastel_softness *= factor * (0.5 + 0.8 * mood_intensity)
    pastel_grain *= factor
    pastel_blend *= 0.6 + 0.3 * emotion_link

    size = 1024
    img = _base_gradient(size=size, palette=palette, mood_intensity=mood_intensity)
    img = _apply_mist(img, strength=mist_strength, smoothness=mist_smoothness, glow=mist_glow)
    img = _apply_watercolor(img, palette=palette, spread=wc_spread, layers=wc_layers, saturation=wc_saturation)
    img = _apply_pastel(img, softness=pastel_softness, grain=pastel_grain, blend_ratio=pastel_blend)

    city_strength = 0.45 + 0.55 * emotion_link
    img = _city_overlay(img, palette=palette, city=city, memory=memory_text, strength=city_strength)

    return _to_bytes(img)
