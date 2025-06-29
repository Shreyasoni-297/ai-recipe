import streamlit as st
from PIL import Image
from src.backend import  detect_ingredients, recipe_from_llm

def main():
    st.title("📸🍽️ AI‑Powered Recipe Generator")
    up = st.file_uploader("Upload fridge / pantry photo", type=["jpg","jpeg","png"])
    if up:
        img = Image.open(up)
        st.image(img, caption="Your image", use_column_width=True)

        diet    = st.selectbox("Diet", ["Any","Vegetarian","Vegan","Keto"])
        cuisine = st.selectbox("Cuisine", ["Any","Indian","Italian","Mexican"])
        time    = st.selectbox("Cook time", ["Any","<15 min","<30 min","<45 min"])

        if st.button("Generate Recipe"):
            with st.spinner("Detecting ingredients & talking to GPT..."):
                ingr = detect_ingredients(img)
                rec  = recipe_from_llm(ingr, {"diet":diet,"cuisine":cuisine,"time":time})
            st.success(rec["title"])
            st.markdown("**Ingredients**")
            st.markdown("\n".join(f"- {x}" for x in rec["ingredients"]))
            st.markdown("**Instructions**")
            st.markdown("\n".join(f"{i+1}. {s}" for i,s in enumerate(rec["instructions"])))

if __name__ == "__main__":
    main()


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
