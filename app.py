from functools import wraps
import hashlib
from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_bcrypt import Bcrypt
import plotly.express as px
import pyodbc
import plotly.graph_objects as go

app = Flask(__name__)
bcrypt = Bcrypt(app)
DSN = "Driver={SQL Server};Server=DESKTOP-DU03FQL\\SQLEXPRESS;Database=PhenixMarket;"

# configuration de la clé flash
app.config['SECRET_KEY'] = 'clés_flash'

# @app.route("/accueil")
# def accueil():
#     return render_template("base.html")

# configuration de l'authentification requise pour toutes les pages
def login_required(f):
    # Utilisation de wraps pour garantir que les attributs de la fonction décorée sont conservés
    @wraps(f)
    # Définition de la fonction décorée, prenant les mêmes arguments que la fonction originale
    def decorated_function(*args, **kwargs):
        # Vérifie si 'user_id' est présent dans la session de l'utilisateur
        if 'user_id' not in session:
            # Si 'user_id' n'est pas présent, affiche un message d'erreur flash
            flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
            # Redirige l'utilisateur vers la page de connexion
            return redirect(url_for('connexion'))
        # Si l'utilisateur est connecté, exécute la fonction originale avec les arguments
        return f(*args, **kwargs)

    # Retourne la fonction décorée
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    if request.method == 'POST':
        # Récupérer les données du formulaire
        email = request.form['email']
        password = request.form['password']

        select_query = "SELECT id_users, email, motdepasse FROM users WHERE email = ?"
        cursor.execute(select_query, (email))
        user = cursor.fetchone()
        print(user)

        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            print("Bravo vous êtes connecté !")
            return redirect(url_for('dashboard'))
        
        else:
            print("Email ou mot de passe incorrect")
       

    cursor.close()
    conn.close()
   
    return render_template('./connexion/connexion.html')

# route inscription
@app.route("/enregistrement", methods=["POST", "GET"])
def enregistrement():
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    if request.method == "POST":
        username = request.form.get("username")
        nom = request.form.get("nom")
        prenom = request.form.get("prenoms")
        telephone = request.form.get("telephone")
        roles = request.form.get("roles")
        genre = request.form.get("genre")
        email = request.form.get("email")
        password = request.form.get("password")

    # Vérifiez les champs du formulaire pour les erreurs
        
        select_query = "SELECT id_users FROM users WHERE email = ?"
        cursor.execute(select_query, (email))
        user_exist = cursor.fetchone()

        if user_exist:
            print("Cet email existe déjà")

        else:
            hash_password = bcrypt.generate_password_hash(password)

            insert_query = "INSERT INTO users (email, motdepasse, roles, nom, prenom, genre, tel) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_query, (email, hash_password, roles, nom, prenom, genre, telephone))

            print(email, hash_password, roles, nom, prenom, genre, telephone)

            conn.commit()
            
            return redirect("/")
        
        cursor.close()
        conn.close()
    
    return render_template("connexion/enregistrement.html")

@app.route("/enregistrementemployer", methods=["POST", "GET"])
@login_required
def enregistrementemployer():
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    if request.method == "POST":
        username = request.form.get("username")
        nom = request.form.get("nom")
        prenom = request.form.get("prenoms")
        telephone = request.form.get("telephone")
        roles = request.form.get("roles")
        genre = request.form.get("genre")
        email = request.form.get("email")
        password = request.form.get("password")

        select_query = "SELECT id_users FROM users WHERE email = ?"
        cursor.execute(select_query, (email,))
        user_exist = cursor.fetchone()

        if user_exist:
            print("Cet email existe déjà")

        else:
            hash_password = bcrypt.generate_password_hash(password)

            # Insérer dans la table users
            insert_user_query = "INSERT INTO users (roles, email, motdepasse, nom, prenom, tel, genre) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_user_query, (roles, email, hash_password, nom, prenom, telephone, genre))
            conn.commit()

            # Récupérer l'ID du nouvel utilisateur inséré
            cursor.execute(select_query, (email,))
            user_id = cursor.fetchone()[0]

            # Insérer dans la table spécifique en fonction du rôle
            if roles.lower() == "vendeur":
                insert_vendeur_query = "INSERT INTO vendeur (nom, prenoms, genre, telephone, id_users) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(insert_vendeur_query, (nom, prenom, genre, telephone, user_id))
            elif roles.lower() == "gestionnaire de stock":
                insert_gestionnaire_query = "INSERT INTO gestionnaire_stock (nom, prenoms, genre, telephone, id_users) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(insert_gestionnaire_query, (nom, prenom, genre, telephone, user_id))

            conn.commit()
            
            return redirect(url_for('dashboard'))
        
        cursor.close()
        conn.close()

    return render_template("./connexion/enregistrementemployer.html")



@app.route("/dashboard")
@login_required
def dashboard():
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    cursor.execute(''' 
                   SELECT CONVERT(varchar(7), dateachat, 120) AS year_m, COUNT(*) AS count 
                    FROM vente 
                    GROUP BY CONVERT(varchar(7), dateachat, 120);
                   ''')

    vente_month = cursor.fetchall()
   
    label = []
    data = []
    for item in vente_month:
        label.append(item[0])
        data.append(item[1])
    fig = px.line(
        vente_month,
        x=label,
        y=data, 
        labels={"y":'Nombre de vente', 'x':'Mois'},
        template='plotly_dark'
    )
    fig.update_layout(title='Nombre de produits vendus par année',
        xaxis = dict(
            tickvals = label,
            ticktext = label,
            tickfont= dict(
            size=10,
        )
        
        ),
        height = 300,
        width = 550
    )

    cursor.execute('''SELECT YEAR(dateachat) as year_ca,SUM(montant) as Montant FROM vente group by YEAR(dateachat)
        order by year_ca''')
    amount_year = cursor.fetchall()

    years = []
    montants = []
    for row in amount_year:
        years.append(row[0])
        montants.append(row[1])
    barplot = go.Figure(data=[go.Bar(x=years, y=montants)])
    barplot.update_layout(title='Montant des ventes par année',
            xaxis_title='Année',
            yaxis_title='Montant',
            
    height = 400,
    width = 600
    )
    # Afficher le graphique
    barplot = barplot.to_html()
    # print(amount_year)
    

    chart = fig.to_html()
    return render_template("./dashboard/dashboard.html", chart=chart, barplot=barplot)



# Define a constant for the number of items per page
PER_PAGE = 10

# Flask routes

@app.route("/produit")
def produit():
    # Retrieve the page number from the query parameters or default to 1
    page = int(request.args.get('page', 1))

    # Calculate the offset
    offset = (page - 1) * PER_PAGE

    # Execute a SQL query to retrieve a page of products
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produit ORDER BY id_produit OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", offset, PER_PAGE)
    data = cursor.fetchall()

    # Count the total number of products
    cursor.execute("SELECT COUNT(*) FROM produit")
    total_products = cursor.fetchone()[0]

    # Calculate the total number of pages
    total_pages = (total_products + PER_PAGE - 1) // PER_PAGE

    # Close the cursor
    cursor.close()

    return render_template("./produit/produit.html", data=data, page=page, total_pages=total_pages)


@app.route("/ajout_produit", methods=['GET', 'POST'])
def ajout_produit():
    if request.method == 'POST':
        nom = request.form['nom']
        descriptions = request.form['descriptions']
        prixunitaire = request.form['prixunitaire']
        id_categorie = request.form['id_categorie']

        # Insert data into the database
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produit (nom, descriptions, prixunitaire, id_categorie) VALUES (?, ?, ?, ?)",
                       (nom, descriptions, prixunitaire, id_categorie))
        conn.commit()

        flash("Product added successfully!", "success")
        return redirect("/produit")  # Redirect to the product management page after adding the product
    else:
        # Render a form for adding a new product
        data = ''
        return render_template("./produit/ajout_produit.html", data=data)
    

@app.route('/modifproduit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def modif_produit(item_id):
    item_id = int(item_id)

    # Connexion à la base de données
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    # Récupération des données du produit depuis la base de données
    cursor.execute('SELECT * FROM produit WHERE id_produit = ?', (item_id,))
    data = cursor.fetchone()

    # Si la méthode de la requête est POST, mise à jour des données du produit dans la base de données
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form['nom']
        descriptions = request.form['descriptions']
        prixunitaire = request.form['prixunitaire']

        # Mise à jour des données du produit dans la base de données
        cursor.execute('''
            UPDATE produit
            SET nom = ?, descriptions = ?, prixunitaire = ?
            WHERE id_produit = ?
        ''', (nom, descriptions, prixunitaire, item_id))

        # Validation des modifications dans la base de données
        conn.commit()

        # Fermeture de la connexion à la base de données
        conn.close()

        # Affichage d'un message de succès à l'utilisateur
        flash(f'Le produit numéro {item_id} a été modifié avec succès !', 'info')

        # Redirection de l'utilisateur vers la page du produit
        return redirect(url_for('produit'))

    # Retour du modèle de formulaire du produit
    return render_template('./produit/modif_produit.html', data=data)

# Route de page de confirmation de suppression produit
@app.route("/confirme_produit/<int:item_id>", methods=['GET', 'POST'])
@login_required
def confirme_produit(item_id):
    item_id = int(item_id)

    
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM produit WHERE id_produit = ?', (item_id,))
    data = cursor.fetchone()
    conn.commit()
    conn.close()

    # flash (f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
    return render_template("./produit/supprimer_produit.html", data=data)

# Route pour la suppression du produit
@app.route('/supprime_produit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def supprime_produit(item_id):
    item_id = int(item_id)

    try:
        # Connexion à la base de données
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()

        # Suppression du produit de la base de données
        cursor.execute('DELETE FROM produit WHERE id_produit = ?', (item_id,))
        
        # Validation des modifications dans la base de données
        conn.commit()

        # Fermeture de la connexion à la base de données
        conn.close()

        flash(f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
    except Exception as e:
        # Gestion des erreurs
        flash(f'Une erreur est survenue lors de la suppression du produit : {str(e)}', 'error')

    return redirect(url_for('produit'))



@app.route("/stock")
def stock():
    return render_template("./stock/stock.html")



@app.route("/vente")
def vente():
    return render_template("./vente/vente.html")


@app.route("/ajout_vente")
def ajoutvente():
    return render_template("./vente/vente.html")



@app.route("/utilisateur")
def utilisateur():
    return render_template("./user/user.html")



if __name__ == '__main__':
    app.run(debug=True)