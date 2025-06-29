
from __future__ import annotations
import streamlit as st
from PIL import Image



from backend import detect_ingredients, recipe_from_llm

def generate_recipes(img, filters):
    ingr  = detect_ingredients(img)
    st.write("DEBUG ingredients ⇒", ingr)
    rec   = recipe_from_llm(ingr, filters)
    return [rec]                     
