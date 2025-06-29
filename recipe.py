
from __future__ import annotations
import streamlit as st
from PIL import Image
from typing import Dict, List

# ---------------- Dummy backend ----------------
from backend import detect_ingredients, recipe_from_llm

def generate_recipes(img, filters):
    ingredients = detect_ingredients(img)
    recipe = recipe_from_llm(ingredients, filters)
    return [recipe]

# ---------------- UI ----------------
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
        with st.expander(f"🍽️  {r['title']}"):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"**Diet:** {r['diet']}")
                st.markdown(f"**Cuisine:** {r['cuisine']}")
                st.markdown(f"**Time:** {r['cook_time']}")
            with c2:
                rating = st.slider("Rate", 1, 5, 3, key=f"rating_{i}_{favourite}")
                st.session_state.setdefault("ratings", {})[r["title"]] = rating
            with c3:
                fav_key = f"fav_{i}_{favourite}"
                if st.checkbox("❤️ Save", key=fav_key):
                    st.session_state.setdefault("favourites", []).append(r)

            st.markdown("**Ingredients**")
            st.markdown("\n".join(f"- {ing}" for ing in r["ingredients"]))
            st.markdown("**Instructions**")
            st.markdown("\n".join(f"{j+1}. {step}" for j, step in enumerate(r["instructions"])))

if __name__ == "__main__":
    main()