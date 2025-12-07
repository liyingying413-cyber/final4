import streamlit as st
from utils import analyze_memory_local
from poster_generator import generate_poster

st.set_page_config(
    page_title="City × Memory × Emotion — Art Poster Generator",
    layout="wide"
)

st.title("🌆 City × Memory × Emotion — Art Poster Generator")

# ---------------------------------------------------------------------
# About Section
# ---------------------------------------------------------------------
with st.expander("📘 About This App (Click to expand)", expanded=True):
    st.markdown("""
This application transforms your **City × Memory × Emotion** into an abstract generative art poster.

**Features:**

- Fully local generation — **no API required**, totally free, runs on Streamlit Cloud.
- Uses three visual styles:
  - **Mist** — dreamy atmospheric diffusion  
  - **Watercolor** — organic flowing texture  
  - **Pastel** — soft grain & illustration-like feeling  
- Analyzes your **city name** and **memory text** to derive emotional color palettes and composition tendencies.

Use the sliders on the left to explore different artistic variations.
    """)

st.write("---")

# ---------------------------------------------------------------------
# Step 1 — Input Section
# ---------------------------------------------------------------------
st.subheader("Step 1 — Enter Your City and Memory Description")

city = st.text_input("City Name", placeholder="e.g., Seoul / Nanjing / Tokyo ...")
memory_text = st.text_area("Write your memory of this city:", height=180)

st.write("---")

# ---------------------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------------------
st.sidebar.header("🌫 Mist Style")
mist_strength = st.sidebar.slider("Mist Strength", 0.0, 1.2, 0.6)
mist_smoothness = st.sidebar.slider("Gradient Smoothness", 0.0, 1.0, 0.7)
mist_glow = st.sidebar.slider("Glow Radius", 0.0, 1.0, 0.4)

st.sidebar.header("🎨 Watercolor Spread")
wc_spread = st.sidebar.slider("Spread Radius", 0.0, 1.0, 0.45)
wc_layers = st.sidebar.slider("Layer Count", 1, 5, 2)
wc_saturation = st.sidebar.slider("Ink Saturation", 0.0, 1.0, 0.6)

st.sidebar.header("🩶 Pastel Softening")
pastel_softness = st.sidebar.slider("Softness", 0.0, 1.0, 0.5)
pastel_grain = st.sidebar.slider("Grain Amount", 0.0, 1.0, 0.25)
pastel_blend = st.sidebar.slider("Blend Ratio", 0.0, 1.0, 0.6)

st.sidebar.header("💗 Emotion Link")
emotion_link = st.sidebar.slider(
    "How strongly emotion influences the final art",
    0.0, 1.0, 0.7
)

st.sidebar.header("🎲 Random Seed")
manual_seed = st.sidebar.number_input(
    "Seed (optional; keeps the output reproducible)", 
    value=42, step=1
)
use_auto_seed = st.sidebar.checkbox("Auto-generate seed from city + memory", value=True)

st.sidebar.write("----")
generate_btn = st.sidebar.button("🎨 Generate Poster")

# ---------------------------------------------------------------------
# Step 2 — Local Emotional & Color Analysis
# ---------------------------------------------------------------------
st.subheader("Step 2 — Local Emotion & Color Analysis")

if generate_btn:
    if not city.strip() or not memory_text.strip():
        st.error("City and memory text cannot be empty!")
        st.stop()

    analysis = analyze_memory_local(city, memory_text)
    st.json(analysis)

    # Auto seed based on content
    if use_auto_seed:
        seed = abs(hash(city.strip() + memory_text.strip())) % 10**6
    else:
        seed = int(manual_seed)

    st.write("---")

    # -----------------------------------------------------------------
    # Step 3 — Local Poster Generation
    # -----------------------------------------------------------------
    st.subheader("Step 3 — Local Poster Generation (Offline)")

    with st.spinner("Generating poster, please wait..."):
        poster_bytes = generate_poster(
            city=city,
            memory_text=memory_text,
            mood=analysis["mood"],
            palette=analysis["palette"],
            mood_intensity=analysis["intensity"],
            seed=seed,
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

        st.image(poster_bytes, caption="🎨 Generated Poster", use_column_width=True)

        st.download_button(
            "📥 Download PNG",
            data=poster_bytes,
            file_name=f"{city}_art_poster.png",
            mime="image/png"
        )
