# backend.py
from ultralytics import YOLO
from PIL import Image
import openai, os, json, textwrap

# 1. Ingredient Detection
MODEL = YOLO("yolov8n.pt")
MAP = {
    "banana": "banana", 
    "apple": "apple",
    "bottle": "milk", 
    "bowl": "yogurt",
    "broccoli": "broccoli", 
    "carrot": "carrot",
    "cake": "bread", 
    "sandwich": "bread",
}

def detect_ingredients(img: Image.Image):
    results = MODEL(img, imgsz=640, conf=0.25)[0]
    names = [results.names[int(c)] for c in results.boxes.cls.tolist()]
    detected = sorted({MAP[n] for n in names if n in MAP})
    return detected or ["salt", "pepper"]


openai.api_key = os.getenv("OPENAI_API_KEY")
SYS_MSG = (
"You are a master chef. Generate one recipe in JSON."
"Use only the given ingredients. Respect diet/cuisine/time."
"Output JSON with: title, ingredients (list), instructions (list)."
)


def recipe_from_llm(ingredients, filters):
    user = f"Ingredients: {', '.join(ingredients)} | " \
           f"Diet: {filters['diet']} | Cuisine: {filters['cuisine']} | " \
           f"Time: {filters['cook_time']}"
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":SYS_MSG},
                  {"role":"user","content":user}],
        temperature=0.7,
    )
    return json.loads(rsp.choices[0].message.content)
