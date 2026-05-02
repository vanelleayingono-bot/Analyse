from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# Chemin absolu vers la base de données (important pour PythonAnywhere)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def safe_float(val):
    """Convertit une valeur en float de façon sûre."""
    try:
        return float(val) if val is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def row_to_dict(row):
    """Convertit une Row SQLite en dict avec moyenne garantie float."""
    d = dict(row)
    d['moyenne'] = safe_float(d.get('moyenne'))
    return d

# Accueil
@app.route("/")
def index():
    return render_template("index.html")

# Ajouter étudiant
@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    if request.method == "POST":
        try:
            moyenne_raw = request.form.get("moyenne", "0")
            moyenne = safe_float(moyenne_raw)

            data = (
                request.form.get("nom"),
                request.form.get("prenom"),
                request.form.get("age"),
                request.form.get("sexe"),
                request.form.get("filiere"),
                request.form.get("niveau"),
                moyenne  # stocké comme vrai float
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
    rows = conn.execute("SELECT * FROM etudiants").fetchall()
    # Garantir que moyenne est toujours un float
    etudiants = [row_to_dict(r) for r in rows]
    return render_template("liste.html", etudiants=etudiants)

# Statistiques
@app.route("/stats")
def stats():
    conn = get_db()

    # Total étudiants
    total = conn.execute("SELECT COUNT(*) as total FROM etudiants").fetchone()

    # Moyenne générale — CAST pour garantir le type numérique
    moy_row = conn.execute("SELECT AVG(CAST(moyenne AS REAL)) as moy FROM etudiants").fetchone()
    moyenne = {"moy": safe_float(moy_row["moy"]) if moy_row else 0.0}

    # Moyenne par filière
    filieres_raw = conn.execute("""
        SELECT filiere, AVG(CAST(moyenne AS REAL)) as moy
        FROM etudiants
        GROUP BY filiere
    """).fetchall()
    filieres = [{"filiere": r["filiere"], "moy": safe_float(r["moy"])} for r in filieres_raw]

    # Meilleure filière
    mf_row = conn.execute("""
        SELECT filiere, AVG(CAST(moyenne AS REAL)) as moy
        FROM etudiants
        GROUP BY filiere
        ORDER BY moy DESC
        LIMIT 1
    """).fetchone()
    meilleure_filiere = {"filiere": mf_row["filiere"], "moy": safe_float(mf_row["moy"])} if mf_row else None

    # Filière la plus faible
    pf_row = conn.execute("""
        SELECT filiere, AVG(CAST(moyenne AS REAL)) as moy
        FROM etudiants
        GROUP BY filiere
        ORDER BY moy ASC
        LIMIT 1
    """).fetchone()
    pire_filiere = {"filiere": pf_row["filiere"], "moy": safe_float(pf_row["moy"])} if pf_row else None

    # Classement — CAST pour garantir le tri et le type numériques
    classement_raw = conn.execute("""
        SELECT nom, prenom, CAST(moyenne AS REAL) as moyenne
        FROM etudiants
        ORDER BY CAST(moyenne AS REAL) DESC
    """).fetchall()
    classement = [
        {"nom": r["nom"], "prenom": r["prenom"], "moyenne": safe_float(r["moyenne"])}
        for r in classement_raw
    ]

    return render_template("stats.html",
                           total=total,
                           moyenne=moyenne,
                           filieres=filieres,
                           meilleure_filiere=meilleure_filiere,
                           pire_filiere=pire_filiere,
                           classement=classement)

if __name__ == "__main__":
    app.run(debug=True)
