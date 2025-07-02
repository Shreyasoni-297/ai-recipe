
from PIL import Image
from io import BytesIO
import base64, json, requests, streamlit as st
import re
from ultralytics import YOLO
yolo_model = YOLO("yolov8n.pt")

TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def call_together(prompt, model="mistralai/Mistral-7B-Instruct-v0.1", max_tokens=250):
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["output"]




HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"  
HF_TOKEN = st.secrets.get("HF_API_KEY", "")
if not HF_TOKEN:
    st.error("❌ HF_API_KEY missing in Secrets. Add it in Settings → Secrets.")
#else:
    #st.write("DEBUG token prefix:", HF_TOKEN[:10])


#st.write("DEBUG token prefix:", st.secrets.get("HF_API_KEY", "")[:6])

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



#openai.api_key =st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# -------- Ingredient detection (simple text prompt) --------
def detect_ingredients(uploaded_file):
    uploaded_file.seek(0)
    results = yolo_model(uploaded_file.read())  # returns list
    names = yolo_model.model.names             # class‑id → label map
    # collect unique labels with confidence > 0.4
    labels = {
        names[int(cls)]
        for r in results
        for cls, conf in zip(r.boxes.cls.cpu(), r.boxes.conf.cpu())
        if conf > 0.4
    }
    if not labels:
        labels = {"vegetable", "ingredient"}   # fallback
    return list(labels)
#def detect_ingredients(img: Image.Image):
    
 #   buf = BytesIO(); img.save(buf, format="JPEG", quality=85)
  #  b64 = base64.b64encode(buf.getvalue()).decode()
   # prompt = (
    #    "You will get a fridge photo in base64. "
     #   "List the visible edible ingredients as simple nouns, comma‑separated:\n"
      #  f"BASE64:{b64[:4000]}..."  # pass first 4k chars (HF limit)
    #)
    #text = call_hf(prompt, max_tokens=120)
    #line = text.split(":")[-1] if ":" in text else text
    #return [x.strip().lower() for x in line.split(",") if x.strip()]

def call_hf(prompt: str, max_tokens: int = 250):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
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

# -------- Recipe generation --------
TOGETHER_KEY = st.secrets["TOGETHER_API_KEY"]
def recipe_from_llm(ingredients, opts):
    prompt = (
        f"Create one {opts['diet']} {opts['cuisine']} recipe "
        f"using only: {', '.join(ingredients)}. "
        f"Total cook time {opts['cook_time']}."
        "Return JSON with keys: title, ingredients (list), instructions (list)."
    )
    r = requests.post(
        "https://api.together.xyz/inference",
        headers={"Authorization": f"Bearer {TOGETHER_KEY}",
                 "Content-Type": "application/json"},
        json={
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 300,
            "temperature": 0.7
        },
        timeout=60
    )
    r.raise_for_status()
    return json.loads(r.json()["output"])

#def recipe_from_llm(ingredients, opts):
    #prompt = (
        #"You are a chef. Return ONE JSON with keys: "
        #"title, ingredients(list), instructions(list).\n\n"
        #f"Ingredients: {', '.join(ingredients)}\n"
        #f"Diet: {opts['diet']}\nCuisine: {opts['cuisine']}\n"
        #f"Time: {opts['cook_time']}\n"
    #)
    #raw = call_hf(prompt, max_tokens=300)
    #try:
     #   first_brace = raw.find("{")
      #  last_brace  = raw.rfind("}")
       # json_blob   = raw[first_brace:last_brace+1]
        #return json.loads(json_blob)
    #except Exception:
        
     #   return {
      #      "title": "AI Recipe",
       #     "diet": opts["diet"],
        #    "cuisine": opts["cuisine"],
         #   "cook_time": opts["cook_time"],
          #  "ingredients": ingredients,
           # "instructions":re.split(r"\n\d+\.\s*", raw.strip())[1:],
        #}