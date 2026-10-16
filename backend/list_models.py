from google import genai

client = genai.Client()

for model in client.models.list():
    if "generateContent" in (model.supported_actions or []):
        print(model.name)