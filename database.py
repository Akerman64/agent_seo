import pymysql.cursors

# Connexion à la base de données
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',  # Remplacez par l'adresse de votre serveur si nécessaire
        user='root',       # Remplacez par votre nom d'utilisateur MySQL
        password='',  # Remplacez par votre mot de passe
        database='seo_agent',  # Nom de la base de données
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # Pour récupérer les résultats sous forme de dictionnaire
    )
    return connection

# Fonction pour ajouter un produit
def save_to_database(handle, title, body_html, vendor, type, published=False):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Insérer un produit dans la base de données
            sql = """
            INSERT INTO products (handle, title, body_html, vendor, type, published)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (handle, title, body_html, vendor, type, published==False))
            connection.commit()  # Valider la transaction
    finally:
        connection.close()

# Fonction pour obtenir tous les produits
def fetch_all_products():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM products"
            cursor.execute(sql)
            return cursor.fetchall()  # Retourne tous les produits sous forme de liste de dictionnaires
    finally:
        connection.close()

# Fonction pour obtenir un produit par son handle
def fetch_product_by_handle(handle):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM products WHERE handle = %s"
            cursor.execute(sql, (handle,))
            return cursor.fetchone()  # Retourne le produit sous forme de dictionnaire
    finally:
        connection.close()
