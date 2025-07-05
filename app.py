#import streamlit as st
#from PIL import Image
#from recipe_model import predict_dish, generate_recipe

#st.set_page_config(page_title="AI Recipe Chef", layout="centered", page_icon="🍳")
#st.title("👨‍🍳 AI Recipe Chef")
#st.write("Upload any food image and get a real AI-generated recipe with filters.")
#st.markdown(
 #   "<h1 style='text-align: center; color: #F63366;'>👨‍🍳 AI Recipe Chef</h1>",
  #  unsafe_allow_html=True
#)
#st.markdown("<p style='text-align: center;'>Upload a food image and get a personalized recipe with filters!</p>", unsafe_allow_html=True)
#uploaded_image = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])
#st.sidebar.title("🔍History")
#diet = st.selectbox("Dietary Preference", [
 #   "Any", "Vegetarian", "Non-Vegetarian", "Keto", "Gluten-Free", "Paleo"])

#cuisine = st.selectbox("Cuisine", ["Any","Indian", "Chinese", "Italian", "Mexican", "Meditarrean"])
#cook_time = st.selectbox("Cook Time", ["Any","<15 mins", "15-30 mins", ">30 mins","1 hour"])

#if uploaded_image:
 #   st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
 #   with st.spinner("Detecting dish..."):
 #       dish = predict_dish(uploaded_image)
 #   st.success(f"Detected Dish: {dish}")

#  with st.spinner("Generating recipe..."):
 #       import time
 #       time.sleep(0.8)  
 #       recipe = generate_recipe(dish, diet, cuisine, cook_time)
        
 #   st.subheader("📋 Ingredients & Instructions")
 #   st.markdown(recipe, unsafe_allow_html=True)
from __future__ import annotations
import streamlit as st
from PIL import Image
from typing import Dict, List



# ---------------- Dummy backend ----------------
def generate_recipes(img: Image.Image, filters: Dict[str, str]) -> List[Dict]:
    """Return hard-coded recipes; swap with real model later."""
    return [
        {
            "title": "Cheesy Veg Sandwich",
            "diet": filters["diet"],
            "cuisine": filters["cuisine"],
            "cook_time": filters["cook_time"],
            "ingredients": [
                "2 bread slices",
                "1 slice cheese",
                "Chopped tomato",
                "Chopped onion",
                "Butter",
            ],
            "instructions": [
                "Spread butter on bread.",
                "Add cheese and veggies.",
                "Grill or toast till golden.",
                "Serve hot with ketchup.",
            ],
        },
        {
            "title": "Quick Egg Fried Rice",
            "diet": filters["diet"],
            "cuisine": "Chinese",
            "cook_time": "<30 min",
            "ingredients": [
                "1 cup cooked rice",
                "2 eggs",
                "Soy sauce",
                "Chopped spring onion",
                "Salt & pepper",
            ],
            "instructions": [
                "Scramble eggs in a pan.",
                "Add rice and soy sauce.",
                "Mix well with veggies.",
                "Garnish with spring onion.",
            ],
        },
    ]

# ---------------- UI ----------------
def main() -> None:
    st.markdown("<h1 style='text-align: center; color: #F63366;'>👨‍🍳 AI Recipe Chef</h1>",unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Upload a food image and get a personalized recipe with filters!</p>", unsafe_allow_html=True)
    #st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳", layout="centered")
    #st.title("📸🍽️ AI-Powered Recipe Generator")

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





# ---------- tiny helper to colour the diet tag ----------
def diet_badge(diet: str) -> str:
    colors = {
        "Vegetarian":   "#34c759",   # green
        "Vegan":        "#0a84ff",   # blue
        "Keto":         "#ff9f0a",   # orange
        "Gluten-Free":  "#ff375f",   # pink
        "Any":          "#8e8e93",   # grey
    }
    col = colors.get(diet, "#8e8e93")
    return (
        f"<span style='background:{col};color:white;"
        "border-radius:4px;padding:2px 6px;font-size:0.85rem;'>"
        f"{diet}</span>"
    )
#if file:
 #   img = Image.open(file)
  #  st.image(img, caption="Your Image", use_column_width=True)
   # with st.spinner("Thinking like a chef..."):
    #    dish = predict_dish(img)
     #   st.success(f"Detected Dish: **{dish}**")
      #  recipe = generate_recipe(dish, diet, cuisine, cook_time)
      #  st.subheader("📝 Recipe:")
      #  st.write(recipe)

