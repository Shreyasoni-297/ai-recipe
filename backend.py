import torch, ultralytics.nn.tasks as tasks
torch.serialization.add_safe_globals([tasks.DetectionModel])
from ultralytics import YOLO

import base64, io, json, os
import openai
from PIL import Image

openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- Ingredient detection with GPT-4o Vision ----------
def detect_ingredients(img: Image.Image):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    vision_prompt = [
        {
            "type": "text",
            "text": (
                "You are a food AI. List the visible edible ingredients "
                "you can clearly recognise in this photo (simple nouns, comma-separated)."
            ),
        },
        {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{b64}",
        },
    ]

    rsp = openai.ChatCompletion.create(
        model="gpt-4o-vision-preview",
        messages=[{"role": "user", "content": vision_prompt}],
        max_tokens=100,
    )

    raw = rsp.choices[0].message.content.strip()
    # e.g. "Ingredients: milk, eggs, broccoli"
    line = raw.split(":")[-1] if ":" in raw else raw
    return [x.strip().lower() for x in line.split(",") if x.strip()]

# ---------- Recipe generation with GPT ----------
SYSTEM = (
    "You are a chef. Return ONE JSON object with keys: "
    "title, ingredients (list), instructions (list)."
)

def recipe_from_llm(ingredients, opts):
    user = (
        f"Ingredients: {', '.join(ingredients)}. "
        f"Diet: {opts['diet']}. Cuisine: {opts['cuisine']}. "
        f"Time: {opts['time']}."
    )

    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    return json.loads(rsp.choices[0].message.content)
