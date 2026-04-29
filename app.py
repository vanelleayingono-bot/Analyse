from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Accueil
@app.route("/")
def index():
    return render_template("index.html")

# Ajouter étudiant
@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    if request.method == "POST":
        try:
            data = (
                request.form.get("nom"),
                request.form.get("prenom"),
                request.form.get("age"),
                request.form.get("sexe"),
                request.form.get("filiere"),
                request.form.get("niveau"),
                request.form.get("moyenne")
            )

            conn = get_db()
            conn.execute("""
            INSERT INTO etudiants (nom, prenom, age, sexe, filiere, niveau, moyenne)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", data)
            conn.commit()

            return redirect("/liste")

        except Exception as e:
            return f"Erreur : {e}"

    return render_template("ajouter.html")

# Liste
@app.route("/liste")
def liste():
    conn = get_db()
    etudiants = conn.execute("SELECT * FROM etudiants").fetchall()
    return render_template("liste.html", etudiants=etudiants)

# Statistiques
@app.route("/stats")
def stats():
    conn = get_db()

    # Total étudiants
    total = conn.execute("SELECT COUNT(*) as total FROM etudiants").fetchone()

    # Moyenne générale
    moyenne = conn.execute("SELECT AVG(moyenne) as moy FROM etudiants").fetchone()

    # Moyenne par filière
    filieres = conn.execute("""
        SELECT filiere, AVG(moyenne) as moy
        FROM etudiants
        GROUP BY filiere
    """).fetchall()

    # Meilleure filière
    meilleure_filiere = conn.execute("""
        SELECT filiere, AVG(moyenne) as moy
        FROM etudiants
        GROUP BY filiere
        ORDER BY moy DESC
        LIMIT 1
    """).fetchone()

    # Filière la plus faible
    pire_filiere = conn.execute("""
        SELECT filiere, AVG(moyenne) as moy
        FROM etudiants
        GROUP BY filiere
        ORDER BY moy ASC
        LIMIT 1
    """).fetchone()

    # Classement des étudiants
    classement = conn.execute("""
        SELECT nom, prenom, moyenne
        FROM etudiants
        ORDER BY moyenne DESC
    """).fetchall()

    return render_template("stats.html",
                           total=total,
                           moyenne=moyenne,
                           filieres=filieres,
                           meilleure_filiere=meilleure_filiere,
                           pire_filiere=pire_filiere,
                           classement=classement)

