
from PIL import Image
from io import BytesIO
import base64, json, requests, streamlit as st

HF_MODEL = "google/flan-t5-base"            # lightweight, totally free


# ---------- YOUR free HF token ----------
HF_TOKEN = st.secrets["HF_API_KEY"]

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.1" 
st.write("DEBUG token prefix:", st.secrets.get("HF_API_KEY", "")[:6])

def call_hf(prompt: str, max_tokens=250):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": 0.7}
    }
    r = requests.post(url, headers=headers, json=data, timeout=60)
    r.raise_for_status()
    return r.json()[0]["generated_text"]

#from torch.serialization import add_safe_globals
#from ultralytics.nn.tasks import DetectionModel
#add_safe_globals([DetectionModel])


#import torch
from functools import partial

#_orig_load = torch.load
#def _patched_load(*args, **kwargs):
    #kwargs.setdefault("weights_only", False)   # force full pickle load
    #return _orig_load(*args, **kwargs)

#torch.load = _patched_load
# ---------------------------------------------------------------

#from ultralytics import YOLO
#model = YOLO("yolov8n.pt")    



#openai.api_key =st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# -------- Ingredient detection (simple text prompt) --------
def detect_ingredients(img: Image.Image):
    buf = BytesIO(); img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    prompt = (
        "You will get a fridge photo in base64. "
        "List the visible edible ingredients as simple nouns, comma‑separated:\n"
        f"BASE64:{b64[:4000]}..."  # pass first 4k chars (HF limit)
    )
    text = call_hf(prompt, max_tokens=120)
    line = text.split(":")[-1] if ":" in text else text
    return [x.strip().lower() for x in line.split(",") if x.strip()]

# -------- Recipe generation --------
def recipe_from_llm(ingredients, opts):
    prompt = (
        "You are a chef. Return ONE JSON with keys: "
        "title, ingredients(list), instructions(list).\n\n"
        f"Ingredients: {', '.join(ingredients)}\n"
        f"Diet: {opts['diet']}\nCuisine: {opts['cuisine']}\n"
        f"Time: {opts['cook_time']}\n"
    )
    raw = call_hf(prompt, max_tokens=300)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # fallback: plain text -> wrap in JSON manually
        return {
            "title": "AI Recipe",
            "ingredients": ingredients,
            "instructions": raw.split("\n")
        }