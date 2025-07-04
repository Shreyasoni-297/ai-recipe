import streamlit as st
from PIL import Image

st.set_page_config(page_title="Recipe Generator (Minimal)", page_icon="🍳", layout="centered")
st.title("📸 Simple Recipe Prototype")

# -------- 1. Image upload --------
uploaded_file = st.file_uploader("Fridge / pantry photo", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded image", use_column_width=True)

# -------- 2. Filters --------
diet = st.selectbox("Select diet", ["Any", "Vegetarian", "Vegan", "Keto", "Pescatarian", "Gluten-Free"])
cook_time = st.slider("Max cooking time (minutes)", 5, 120, 30)

# -------- 3. Generate dummy recipe --------
if st.button("Get Recipe", type="primary"):
    ingredients = ["milk", "egg"]
    recipe_steps = [
        "1. Beat the eggs in a bowl.",
        "2. Add milk and whisk until combined.",
        "3. Cook mixture on medium heat while stirring.",
        "4. Season and serve warm.",
    ]

    st.success("Here is a dummy recipe (backend coming soon!)")
    st.subheader("📝 Ingredients")
    st.markdown("\n".join(f"- {item}" for item in ingredients))

    st.subheader("👩‍🍳 Method")
    st.markdown("\n".join(recipe_steps))
else:
    st.info("Set your preferences and hit *Get Recipe* to see dummy output.")