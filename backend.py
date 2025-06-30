import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]
from torch.serialization import add_safe_globals
from ultralytics.nn.tasks import DetectionModel
add_safe_globals([DetectionModel])

import torch
from functools import partial

_orig_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)   # force full pickle load
    return _orig_load(*args, **kwargs)

torch.load = _patched_load
# ---------------------------------------------------------------

from ultralytics import YOLO
model = YOLO("yolov8n.pt")



from ultralytics import YOLO
model = YOLO("yolov8n.pt")         


import base64, json, os
import openai
from PIL import Image
from io import BytesIO

openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# ---------- Ingredient detection with GPT-4o Vision ----------
def detect_ingredients(img: Image.Image):
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    img_bytes = buf.getvalue()

    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    vision_prompt = [
        {
            "type": "text",
            "text": 
                "You are a food AI. List the visible edible ingredients "
                "you can clearly recognise in this photo (simple nouns, comma-separated)."
        },
        {
            "type": "image_url",
            "image_url": {"url":f"data:image/jpeg;base64,{b64}"}
        },
    ]

    rsp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": vision_prompt}],
        max_tokens=60,
    )

    raw = rsp.choices[0].message.content.strip()

    line = raw.split(":")[-1] if ":" in raw else raw
    return [x.strip().lower() for x in line.split(",") if x.strip()]


SYSTEM = (
    "You are a chef. Return ONE JSON object with keys: "
    "title, ingredients (list), instructions (list)."
)

def recipe_from_llm(ingredients, opts):
    SYSTEM = ("You are a chef. Return ONE JSON with keys: "
              "title, ingredients(list), instructions(list).")

    user = (
        f"Ingredients: {', '.join(ingredients)}. "
        f"Diet: {opts['diet']}. Cuisine: {opts['cuisine']}. "
        f"Time: {opts['time']}."
    )

    rsp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    return json.loads(rsp.choices[0].message.content)
