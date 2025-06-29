import torch


orig_torch_load = torch.load
def patched_load(file, *args, **kwargs):
    kwargs["weights_only"] = False
    return orig_torch_load(file, *args, **kwargs)
torch.load = patched_load
# --------------------------------------------------

from ultralytics import YOLO

MODEL = YOLO("yolov8n.pt")



from PIL import Image
import openai, os, json, textwrap, torch.serialization
from ultralytics.nn.tasks import DetectionModel

# Prevent PyTorch 2.7 “weights_only” unpickling error
torch.serialization.add_safe_globals({'ultralytics.nn.tasks.DetectionModel': DetectionModel})



LABEL_MAP = {
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
    res = MODEL(img, conf=0.25, imgsz=640)[0]
    names = [res.names[int(c)] for c in res.boxes.cls.tolist()]
    return sorted({LABEL_MAP.get(n) for n in names if n in LABEL_MAP}) or ["salt", "pepper"]

openai.api_key = os.getenv("OPENAI_API_KEY")
SYSTEM = ("You are a chef. Return ONE JSON dict with keys: "
          "title, ingredients(list), instructions(list).")

def recipe_from_llm(ingredients, opts):
    prompt = textwrap.dedent(f"""
        Ingredients: {', '.join(ingredients)}
        Diet: {opts['diet']} | Cuisine: {opts['cuisine']} | Time: {opts['time']}
    """)
    msg = [{"role":"system","content":SYSTEM},
           {"role":"user","content":prompt}]
    rsp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=msg)
    return json.loads(rsp.choices[0].message.content)

# backend.py
from pathlib import Path
from urllib.request import urlretrieve
from ultralytics import YOLO
import torch

# --- monkey‑patch: make torch.load ignore weights_only ---
_orig_load = torch.load
def _patched_load(f, *args, **kw):
    kw.setdefault("weights_only", False)
    return _orig_load(f, *args, **kw)
torch.load = _patched_load
# ----------------------------------------------------------

WEIGHTS = Path("models/yolov8n.pt")          # keep weights in repo OR auto‑download

def get_model(weights=WEIGHTS):
    if not weights.exists() or weights.stat().st_size < 1_000_000:  # <~1 MB = definitely corrupt
        weights.parent.mkdir(parents=True, exist_ok=True)
        url = "https://assets.ultralytics.com/models/v8/yolov8n.pt"
        urlretrieve(url, weights)           # 6 MB only, Streamlit limit safe
    return YOLO(str(weights))

MODEL = get_model()
