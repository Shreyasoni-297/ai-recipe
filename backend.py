import openai, os, json, random

openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------- TEMP: random ingredients -------------
def detect_ingredients(_img):
    sample = [
        ["milk", "eggs", "cheese"],
        ["apple", "banana"],
        ["bread", "tomato", "cheese"],
        ["yogurt", "broccoli", "carrot"],
    ]
    return random.choice(sample)
# ----------------------------------------------------

SYSTEM = ("You are a chef. Return ONE JSON dict with keys: "
          "title, ingredients(list), instructions(list).")

def recipe_from_llm(ingredients, opts):
    user = (
        f"Ingredients: {', '.join(ingredients)}. "
        f"Diet: {opts['diet']}. Cuisine: {opts['cuisine']}. "
        f"Time: {opts['time']}."
    )
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":user}],
        temperature=0.7
    )
    return json.loads(rsp.choices[0].message.content)

