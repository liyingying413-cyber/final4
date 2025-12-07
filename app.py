
import streamlit as st

from utils import local_analyze, auto_seed
from poster_generator import generate_poster


st.set_page_config(
    page_title="City × Memory × Emotion — Poster Generator",
    layout="wide",
)

st.title("City × Memory × Emotion — Poster Generator")

with st.expander("What is this app?"):
    st.markdown(
        """
        This web app turns your **memories of a city** into an **abstract art poster**.

        Workflow:

        1. Describe a city and your memory of it.
        2. A small local "AI" analysis extracts mood + color palette (no external API).
        3. You fine‑tune visual parameters (mist, watercolor, pastel, emotion link).
        4. The app generates a 1:1 PNG poster that you can download.
        """
    )

# ----------------------------- Sidebar Controls -----------------------------
st.sidebar.header("Shape & Texture Controls")

st.sidebar.subheader("☁ Mist")
mist_strength = st.sidebar.slider("Mist Strength", 0.0, 1.0, 0.6, 0.01)
mist_smoothness = st.sidebar.slider("Gradient Smoothness", 0.0, 1.0, 0.2, 0.01)
mist_glow = st.sidebar.slider("Glow Radius", 0.0, 1.0, 0.3, 0.01)

st.sidebar.subheader("🎨 Watercolor Spread")
wc_spread = st.sidebar.slider("Spread Radius", 0.0, 1.0, 0.45, 0.01)
wc_layers = st.sidebar.slider("Layer Count", 1, 6, 4, 1)
wc_saturation = st.sidebar.slider("Ink Saturation", 0.0, 1.0, 0.86, 0.01)

st.sidebar.subheader("💗 Pastel Softness")
pastel_softness = st.sidebar.slider("Softness", 0.0, 1.0, 0.5, 0.01)
pastel_grain = st.sidebar.slider("Grain Amount", 0.0, 1.0, 0.25, 0.01)
pastel_blend = st.sidebar.slider("Blend Ratio", 0.0, 1.0, 0.6, 0.01)

st.sidebar.subheader("🔗 Emotion Link")
emotion_link = st.sidebar.slider(
    "How strongly should emotion affect the visual result?",
    0.0,
    1.0,
    0.7,
    0.01,
)

st.sidebar.subheader("🎲 Random Seed")
seed_manual = st.sidebar.number_input("Seed (keeping the same seed reproduces the poster)", 0, 99999, 42, 1)
auto_seed_flag = st.sidebar.checkbox("Auto‑generate seed from city + text", value=True)

if st.sidebar.button("Generate Poster"):
    generate_click = True
else:
    generate_click = False

# ----------------------------- Main Inputs -----------------------------
st.subheader("Step 1 — Describe Your City Memory")

city = st.text_input("City", placeholder="e.g. Seoul / Tokyo / Paris / Busan …")
memory_text = st.text_area(
    "Write about your memory of this city",
    height=200,
    placeholder="For example: the first winter snow, the subway lights at night, the smell of street food…",
)

if generate_click:
    if not city.strip() or not memory_text.strip():
        st.error("Please enter both a city and a memory description.")
    else:
        with st.spinner("Step 2 — Analyzing your text (local, no API)…"):
            analysis = local_analyze(city, memory_text)

        st.subheader("Step 2 — Local AI Analysis (for your report)")
        st.json(analysis)

        if auto_seed_flag:
            seed_value = auto_seed(city, memory_text)
        else:
            seed_value = int(seed_manual)

        mood_intensity = float(analysis.get("intensity", 0.5))
        palette_rgb = analysis.get("palette_rgb", [(200, 220, 230), (230, 240, 245), (180, 200, 210)])
        mood_label = analysis.get("mood", "calm / nostalgic")

        st.subheader("Step 3 — Fully Local Poster Generation (no API, offline‑friendly)")

        with st.spinner("Rendering abstract poster…"):
            poster_bytes = generate_poster(
                city=city,
                memory_text=memory_text,
                mood=mood_label,
                palette=palette_rgb,
                mood_intensity=mood_intensity,
                seed=seed_value,
                emotion_link=emotion_link,
                mist_strength=mist_strength,
                mist_smoothness=mist_smoothness,
                mist_glow=mist_glow,
                wc_spread=wc_spread,
                wc_layers=wc_layers,
                wc_saturation=wc_saturation,
                pastel_softness=pastel_softness,
                pastel_grain=pastel_grain,
                pastel_blend=pastel_blend,
            )

        st.image(poster_bytes, caption="Generated Poster (1 : 1)", use_column_width=True)

        st.download_button(
            "Download PNG",
            data=poster_bytes,
            file_name=f"city_memory_poster_{city or 'city'}.png",
            mime="image/png",
        )
