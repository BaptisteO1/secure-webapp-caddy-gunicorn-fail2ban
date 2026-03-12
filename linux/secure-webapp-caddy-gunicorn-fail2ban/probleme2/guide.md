# Déploiement d’une application web sécurisée avec Caddy, Gunicorn et fail2ban

## Objectif

Le but de ce guide est de déployer une petite application web dynamique qui possède un système d’authentification simple.

L’application expose deux routes :

- `/login` : page de connexion
- `/private` : accessible uniquement après authentification

Si l’utilisateur est connecté, il peut accéder au message :

Accès au contenu privé autorisé

Pour mettre cela en place, nous allons utiliser :

- une application web Flask
- Gunicorn comme gestionnaire de processus
- Caddy comme serveur web et reverse proxy
- fail2ban pour bloquer les tentatives de connexion suspectes

---

## Choix techniques

> Flask est utilisé car il permet de créer rapidement une application web dynamique simple.

> Gunicorn est utilisé comme gestionnaire de processus pour exécuter l’application.

> Caddy est utilisé comme reverse proxy car il est imposé dans le sujet.

---

# 1. Préparation du système

On suppose que l’on dispose d’une machine Debian neuve avec :

- un utilisateur `user`
- les droits sudo
- nftables activé

Dans un premier temps mettre à jour le système :

sudo apt update  
sudo apt upgrade -y

Installer les outils nécessaires :

sudo apt install -y python3 python3-pip python3-venv git fail2ban curl

---

# 2. Installation de Caddy

Installer les dépendances :

sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https

Ajouter la clé :

curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

Ajouter le dépôt :

curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

Installer Caddy :

sudo apt update  
sudo apt install caddy

---

# 3. Création de l'application

Ensuite on va venir créer le dossier du projet :

mkdir ~/webapp  
cd ~/webapp

Créer un environnement Python :

python3 -m venv venv  
source venv/bin/activate

Installer les dépendances :

pip install flask gunicorn

---

# 4. Implémentation de l'application

Dans mon cas j’ai créé le fichier `app.py` sur ma machine puis je l’ai copié sur la machine Debian.

Pour récupérer l’IP de ma machine debian :

hostname -I

Puis copier le fichier :

scp app.py user@IP:~/webapp/
dans mon cas : (scp app.py baptiste@192.168.1.48:~/webapp/)

Le fichier `app.py` contient la logique suivante :

- une route `/login` qui vérifie les identifiants
- une session utilisateur après connexion
- une route `/private` protégée

> Les identifiants sont directement écrits dans le code pour simplifier le projet.

> Lorsqu’une tentative de connexion échoue, l’application écrit un message dans les logs. (voir après comment mettre en place)
> Ces logs peuvent ensuite être analysés par fail2ban afin de détecter plusieurs tentatives de connexion suspectes et bannir l’adresse IP.

---

# 4.5 Créer un dossier pour les logs et donner les droits si besoin

sudo touch /var/log/caddy/access.log
sudo chown baptiste:www-data /var/log/caddy/access.log
sudo chmod 664 /var/log/caddy/access.log


# 5. Lancer l'application avec Gunicorn

Pour tester l’application lancer :
(ne pas oublier d'absolument activer l'environnement virtuel (venv), sinon le système ne trouvera pas Gunicorn ni les packages installés dans ce venv.)

gunicorn -w 4 -b 127.0.0.1:8000 app:app

L’application écoute sur :

127.0.0.1:8000

---

# 6. Configuration du reverse proxy Caddy

On doit maintenant éditer le fichier caddyfile pour écrire dans un fichier de log :

sudo nano /etc/caddy/Caddyfile

Configuration :

:80 {

    reverse_proxy localhost:8000

    log {
        output file /var/log/caddy/access.log
        format single_field common_log
    }

}

Pour vérifier la config:
sudo caddy validate --config /etc/caddy/Caddyfile

On doit avoir "valid configuration"

Redémarrer Caddy :

sudo systemctl restart caddy

Puis on test :

sudo systemctl status caddy

On doit avoir : active (running)

---

# 7. Mise en place du gestionnaire de processus - Service systemd

Créer un service systemd :

sudo nano /etc/systemd/system/webapp.service

avec pour contenu (remplacer user par son nom d'utilisateur) :

[Unit]
Description=Gunicorn Web Application
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/webapp
Environment="PATH=/home/user/webapp/venv/bin"
ExecStart=/home/user/webapp/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target

Dans mon cas j'ai remplacé user par baptiste

Maintenant recharger systemd et redémarrer le service :

sudo systemctl daemon-reload  
sudo systemctl enable webapp  
sudo systemctl start webapp

puis on vérifie :
sudo systemctl status webapp

on doit avoit :

Active: active (running)

enfin on vérifie que Gunicorn écoute
ss -lntp | grep 8000

---

# 8. Mise en place du fail2ban

Maintenant pour bannir une IP après plusieurs tentatives de connexion échouées.

# 9. Filtre fail2ban

Créer le fichier de conf :

sudo nano /etc/fail2ban/filter.d/caddy-login.conf

Contenu :

[Definition]
failregex = <HOST> -.*POST /login.* 401
ignoreregex =

---

# 10. Jail fail2ban

On créer le fichier:

sudo nano /etc/fail2ban/jail.local

Configuration :

[caddy-login]

enabled = true  
filter = caddy-login  
port = http,https  
logpath = /var/log/caddy/access.log  
maxretry = 5  
findtime = 600  
bantime = 600  

Ici une adresse IP sera bannie après 5 tentatives d'authentification échouées dans une période de 10 minutes.

---

# 11. Test du bannissement

On teste maintenant plusieurs tentatives de connexion incorrectes.

for i in {1..5}; do
  curl -s -X POST http://127.0.0.1/login -d "username=test&password=wrong"
done

Puis on vérifie la liste de bannissement :

sudo fail2ban-client status caddy-login

La section Banned IP list doit contenir 127.0.0.1

On peut ensuite débannir pour retester au besoin :

sudo fail2ban-client set caddy-login unbanip 127.0.0.1