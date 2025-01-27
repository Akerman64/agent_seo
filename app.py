from flask import Flask, render_template, request, jsonify, send_file
import openai
import pandas as pd
from database import get_db_connection, save_to_database, fetch_all_products, fetch_product_by_handle
import os

# Configuration Flask
app = Flask(__name__)

# Configuration OpenAI
openai.api_key = "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 "  # Remplacez par votre clé OpenAI

# Fonction pour générer le contenu du produit
def generate_product_data(product_name):
    prompt = f"""
    Analyse les descriptions de {product_name} sur les sites concurrents et génère une description unique et optimisée pour le SEO, en format HTML. Fournis une structure complète avec des sections telles que Caractéristiques, Pyramide Olfactive, Ingrédients, Fabrication, Conseils d'Utilisation, et Avantages. Utilise des balises HTML pour structurer la description, telles que <p>, <h2>, <ul>, <li>, etc. Tu peux ne pas mettre le header et le footer. Mets juste le body. Le handle, selon le nom du produit entré, doit etre comme çà par exemple : parfum-musc-blanc-edition-aigle-50ml-collection-privee
    """
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Vous pouvez aussi utiliser "gpt-3.5-turbo" selon la version que vous avez
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant spécialisé dans la génération de descriptions de produits."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7  # Vous pouvez ajuster la température pour plus ou moins de créativité
        )
        
        if response and response.choices:
            description = response.choices[0].message["content"].strip()
            description = description.replace("\u00e9", "é").replace("\u00f4", "ô")  # Décode les caractères échappés
            print(f"Description générée : {description}")  # Affiche la description générée
        else:
            print("Pas de description générée.")
            description = ""  # Gérer le cas où aucune réponse n'est générée

    except Exception as e:
        print(f"Erreur lors de la génération de la description : {str(e)}")
        description = ""  # Retourner une chaîne vide en cas d'erreur
        
    print(f"API Response: {response.choices[0].get('text')}")
    
    handle = product_name.lower().replace(" ", "-")
    
    return {
        "handle": handle,
        "title": product_name,
        "body_html": description,
        "vendor": "Collection Privée",
        "type": "",
        "published": False
    }

# Route principale (page HTML)
@app.route('/')
def index():
    try:
        products = fetch_all_products()
        return render_template('index.html', products=products)
    except Exception as e:
        print(f"Erreur : {e}")
        return 'Une erreur est survenue.'


# Route pour générer et sauvegarder les données d'un produit
@app.route('/generate', methods=['POST'])
def generate():
    product_name = request.form['product_name']
    product_data = generate_product_data(product_name)
    save_to_database(
        handle=product_data['handle'],
        title=product_data['title'],
        body_html=product_data['body_html'],
        vendor=product_data['vendor'],
        type=product_data['type'],
        published=False
    )
    return jsonify(product_data)

# Route pour télécharger tous les produits en CSV
@app.route('/download/all')
def download_all():
    products = fetch_all_products()
    if not products:
        return "Aucun produit disponible", 404

    # Créer un DataFrame et supprimer la colonne 'id' si elle existe
    df = pd.DataFrame(products)
    if 'id' in df.columns:
        df = df.drop(columns=['id'])  # Supprimer la colonne 'id'

    filename = "all_products.csv"
    df.to_csv(filename, index=False)
    return send_file(filename, as_attachment=True)

# Route pour télécharger un produit spécifique en CSV
@app.route('/download/<handle>')
def download_product(handle):
    product = fetch_product_by_handle(handle)
    if not product:
        return "Produit non trouvé", 404

    # Créer un DataFrame et supprimer la colonne 'id' si elle existe
    df = pd.DataFrame([product])
    if 'id' in df.columns:
        df = df.drop(columns=['id'])  # Supprimer la colonne 'id'

    filename = f"{handle}.csv"
    df.to_csv(filename, index=False)
    return send_file(filename, as_attachment=True)

@app.route('/delete/<handle>', methods=['POST'])
def delete_product(handle):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Requête pour supprimer un produit par son handle
            sql = "DELETE FROM products WHERE handle = %s"
            cursor.execute(sql, (handle,))
            connection.commit()  # Validation de la transaction
        return jsonify({"message": f"Produit avec handle '{handle}' supprimé avec succès."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True,  host='127.0.0.1', port=5001)
# 