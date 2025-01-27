import openai

openai.api_key = "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"

prompt = "Analyse les descriptions de Parfum Musc Blanc Edition Aigle 50ml et génère une description optimisée pour le SEO."
response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Vous pouvez aussi utiliser "gpt-3.5-turbo" selon la version que vous avez
        messages=[
            {"role": "system", "content": "Vous êtes un assistant spécialisé dans la génération de descriptions de produits."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7  # Vous pouvez ajuster la température pour plus ou moins de créativité
)

print(response)

