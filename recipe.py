from __future__ import annotations  


import streamlit as st
from PIL import Image
from typing import List, Dict
import json, re

# ---------------- Dummy backend ----------------
from backend import detect_ingredients, recipe_from_llm
#openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_recipes(img, filters):
     if img is None:
        st.error("❌ Image not found. Please upload a valid image.")
        return []
     try:
        ingr = detect_ingredients(img)
        st.info(f"✅ Detected Ingredients: {ingr}")
     except Exception as e:
        st.error(f"⚠️ Ingredient detection failed: {e}")
        return []

     try:
        rec = recipe_from_llm(ingr, filters)
        return [rec]
     except Exception as e:
        st.error(f"⚠️ Recipe generation failed: {e}")
        return []
     ingr = detect_ingredients(img)
     rec = recipe_from_llm(ingr, filters)
     return [rec]

def main() -> None:
    st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳", layout="centered")
    st.title("📸🍽️ AI-Powered Recipe Generator")

    uploaded = st.file_uploader("Upload your fridge / pantry photo", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded image", use_column_width=True)

        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            diet = st.selectbox("Diet", ["Any", "Vegetarian", "Vegan", "Keto", "Pescatarian", "Gluten-Free"])
        with col2:
            cuisine = st.selectbox("Cuisine", ["Any", "Indian", "Italian", "Mexican", "Chinese", "Mediterranean"])
        with col3:
            cook_time = st.selectbox("Cook time", ["Any", "<15 min", "<30 min", "<45 min", "1 hour+"])

        if st.button("Generate Recipes", type="primary"):
            with st.spinner("Chef-bot is thinking…"):
                recs = generate_recipes(img, {"diet": diet, "cuisine": cuisine, "cook_time": cook_time})

            if not recs:
                st.warning("No recipes found — try relaxing a filter.")
            else:
                st.success(f"{len(recs)} recipe{'s' if len(recs)>1 else ''} found!")
                show_recipes(recs)

        if st.session_state.get("favourites"):
            st.divider()
            st.subheader("⭐ Saved favourites")
            show_recipes(st.session_state["favourites"], favourite=True)
    else:
        st.info("👆 Upload an image to start.")

def show_recipes(recs: List[Dict], favourite: bool = False) -> None:
    for i, r in enumerate(recs):
        # --- Safe defaults in case keys are missing ---
        if not isinstance(r, dict):
            st.warning(f"Unexpected recipe format: {r}")
            continue

        title   = r.get("title",  "Untitled Recipe")
        diet    = r.get("diet",   "Any")
        cuisine = r.get("cuisine", "Any")
        ctime   = r.get("cook_time", "Unknown")
        ings    = r.get("ingredients", [])
        steps   = r.get("instructions", [])

        with st.expander(f"🍽️  {title}"):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"*Diet:* {diet}")
                st.markdown(f"*Cuisine:* {cuisine}")
                st.markdown(f"*Time:* {ctime}")
            with c2:
                rating = st.slider("Rate", 1, 5, 3,
                                   key=f"rating_{i}_{favourite}")
                st.session_state.setdefault("ratings", {})[title] = rating
            with c3:
                fav_key = f"fav_{i}_{favourite}"
                if st.checkbox("❤️ Save", key=fav_key):
                    st.session_state.setdefault("favourites", []).append(r)

            st.markdown("**Ingredients**")
            for ing in ings:
                st.markdown(f"- {ing}")

            st.markdown("**Instructions**")
            for j, step in enumerate(steps):
                st.markdown(f"{j+1}. {step}")
safe_ings = [ing for ing in ings if len(ing) < 50]  # drop absurdly long tokens
for ing in safe_ings:
    st.markdown(f"- {ing}")



# --------------- Run the app ---------------------
if __name__ == "__main__":
    main()