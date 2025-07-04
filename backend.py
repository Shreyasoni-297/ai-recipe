from PIL import Image
from io import BytesIO
import base64, json, requests,re, streamlit as st


HF_TOKEN = st.secrets["HF_API_KEY"]
HF_MODEL = st.secrets["HF_MODEL"]

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}",
           "Content-Type": "application/json"}
API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


if not HF_TOKEN:
    st.error("❌ HF_API_KEY missing in Secrets. Add it in Settings → Secrets.")
else:
    st.write("DEBUG token prefix:", HF_TOKEN[:10])



def call_hf(prompt: str, max_tokens=250):
    url = f"https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta/"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": 0.7},
        "options": {"wait_for_model": True}
    }
    r = requests.post(url, headers=headers, json=data, timeout=180)
    r.raise_for_status()
    return r.json()[0]["generated_text"]


# -------- Ingredient detection (simple text prompt) --------
def detect_ingredients(img: Image.Image):
    buf = BytesIO(); img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    prompt = (
        "You are a vision-food AI. I will give you part of a fridge "
        "photo encoded in base-64. **Return ONLY a comma-separated list "
        "of the visible edible ingredients - no extra words, no caption.**\n\n"
        f"PHOTO_BASE64_PART: {b64[:2000]}..."  # pass first 4k chars (HF limit)
    )
    
    text = call_hf(prompt, max_tokens=120)
    if "error" in text.lower():
        raise Exception(f"Bad HF response: {text}")

    line = text.split(":")[-1] if ":" in text else text
    return [x.strip().lower() for x in line.split(",") if x.strip()]

# -------- Recipe generation --------
def recipe_from_llm(ingredients, opts):
    prompt = (
        f"You are a chef. Return ONE JSON with keys: "
        "title, ingredients(list), instructions(list).\n\n"
        f"Ingredients: {', '.join(ingredients)}\n"
        f"Diet: {opts['diet']}\nCuisine: {opts['cuisine']}\n"
        f"Time: {opts['cook_time']}\n"
    )
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": prompt,
        "parameters": {"temperature": 0.7, "max_new_tokens": 250}
    }
  
   
    raw = call_hf(prompt, max_tokens=300)
    try:
        first_brace = raw.find("{")
        last_brace  = raw.rfind("}")
        json_blob   = raw[first_brace:last_brace+1]
        return json.loads(json_blob)
    except Exception:
        # Fallback: wrap plaintext into minimal dict
        return {
            "title": "AI Recipe",
            "diet": opts["diet"],
            "cuisine": opts["cuisine"],
            "cook_time": opts["cook_time"],
            "ingredients": ingredients,
            "instructions": re.split(r"\n\d+\.\s*", raw.strip())[1:],
        }


