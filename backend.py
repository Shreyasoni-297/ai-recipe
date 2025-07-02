
from PIL import Image
from io import BytesIO
import base64, json, requests, streamlit as st

#HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"
HF_TOKEN = st.secrets["HF_API_KEY"]
HF_MODEL = st.secrets["HF_MODEL"]
    
#HF_TOKEN = st.secrets.get("HF_API_KEY", "")
#HF_API_KEY = "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"



if not HF_TOKEN:
    st.error("❌ HF_API_KEY missing in Secrets. Add it in Settings → Secrets.")
#else:S
 #   st.write("DEBUG token prefix:", HF_TOKEN[:10])


#st.write("DEBUG token prefix:", st.secrets.get("HF_API_KEY", "")[:6])

#TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def call_hf(prompt: str, max_tokens=250):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": 0.7},
        "options":{"wait_for_model": True}
    }
    r = requests.post(url, headers=headers, json=data, timeout=60)
    r.raise_for_status()
    return r.json()[0]["generated_text"]



#openai.api_key =st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# -------- Ingredient detection (simple text prompt) --------
#def detect_ingredients(img: Image.Image):
 #   buf = BytesIO(); img.save(buf, format="JPEG", quality=85)
  #  b64 = base64.b64encode(buf.getvalue()).decode()
   # prompt = (
    #    "You will get a fridge photo in base64. "
     #   "List the visible edible ingredients as simple nouns, comma‑separated:\n"
      #  f"BASE64:{b64[:4000]}..."  
    #)
    #text = call_hf(prompt, max_tokens=120)
    #line = text.split(":")[-1] if ":" in text else text
    #return [x.strip().lower() for x in line.split(",") if x.strip()]
def detect_ingredients(img: Image.Image):
    
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    img_bytes = buf.getvalue()

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {
        "parameters": json.dumps({
            "prompt": "List visible edible ingredients, comma separated.",
            "max_new_tokens": 60
        })
    }
    res = requests.post(
        url,
        headers=headers,
        files={"image": img_bytes},
        data=data,
        timeout=180,
    )
    res.raise_for_status()
    text = res.json()[0]["generated_text"]
    first_line = text.splitlines()[0]
    return [t.strip().lower() for t in first_line.split(",") if t.strip()]




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
    start, end = raw.find("{"), raw.rfind("}")
    try:
        first_brace = raw.find("{")
        last_brace  = raw.rfind("}")
        json_blob   = raw[first_brace:last_brace+1]
        return json.loads(json_blob)
    except Exception:
        
        return {
            "title": "AI Recipe",
            "diet": opts["diet"],
            "cuisine": opts["cuisine"],
            "cook_time": opts["cook_time"],
            "ingredients": ingredients,
            "instructions": [raw.strip()]
        }