
# City × Memory × Emotion — Poster Generator (Fully Local)

This project is a Streamlit web app for your final project.  
It turns a **city + personal memory** into an **abstract 1:1 art poster**.

## Features

- Step 1: User writes a memory about a city (in any language).
- Step 2: Local "AI analysis" (no OpenAI / Stability / API keys needed).
  - Detects a rough **mood label** (warm / melancholic / tense).
  - Generates a **color palette** (RGB) and **intensity** parameter.
- Step 3: Fully local generative art:
  - Mist layer (atmospheric fog + glow)
  - Watercolor layer (soft color blobs / diffusion)
  - Pastel layer (softening + grain)
  - City style overlays (waves, neon lines, pixel grid, arches, chaos strokes, fog)
- Users can adjust parameters in the sidebar via sliders and regenerate the poster.
- Final poster can be downloaded as PNG.

## Files

- `app.py` — Streamlit UI and app logic.
- `utils.py` — Local text analysis and auto-seed helper.
- `poster_generator.py` — Core generative‑art functions (pure Python + Pillow + NumPy).
- `requirements.txt` — Dependencies for Streamlit Cloud.

## Deploy on Streamlit Cloud

1. Create a GitHub repository and upload all files in this folder.
2. On Streamlit Cloud, create a new app:
   - Repository: your GitHub repo
   - Branch: `main`
   - Main file path: `app.py`
3. No secrets or API keys are required (everything is local code).
4. Deploy and share the app link.

This app is designed as a **creative data‑driven final project** for a course on
generative art and web‑based interaction.
