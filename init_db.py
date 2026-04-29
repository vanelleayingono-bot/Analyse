import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    age INTEGER,
    sexe TEXT,
    filiere TEXT,
    niveau TEXT,
    moyenne REAL
)
""")

conn.commit()
conn.close()

print("Base de données créée")
