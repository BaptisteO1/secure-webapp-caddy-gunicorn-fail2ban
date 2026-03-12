import logging

# configuration du logging
# ici on écrit les événements dans le fichier de log utilisé par Caddy
logging.basicConfig(
    filename="/var/log/caddy/access.log",
    level=logging.INFO
)

from flask import Flask, request, session, redirect, url_for, abort

app = Flask(__name__)
app.secret_key = "supersecretkey"

# identifiants simples directement dans le code
USER = "admin"
PASSWORD = "password123"


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # vérification des identifiants
        if username == USER and password == PASSWORD:
            session["logged"] = True
            return redirect("/private")

        else:
            # en cas d'échec on enregistre un log
            # fail2ban pourra détecter ces tentatives
            logging.info("LOGIN_FAILED")
            return "Login incorrect", 401

    # formulaire simple de connexion
    return '''
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit">
        </form>
    '''


@app.route("/private")
def private():

    # si l'utilisateur n'est pas connecté on le renvoie vers /login
    if not session.get("logged"):
        return redirect("/login")

    return "Accès au contenu privé autorisé"


if __name__ == "__main__":
    app.run()