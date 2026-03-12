# Secure Web Application with Caddy, Gunicorn and Fail2ban

## Problème choisi

Configuration d’une application web avec reverse proxy, gestionnaire de processus et détection d’activité malveillante.

Ce projet consiste à déployer une application web dynamique protégée par un système d’authentification.  
L’infrastructure comprend un serveur applicatif, un reverse proxy et un mécanisme de bannissement d’IP en cas de tentatives de connexion suspectes.

L’application expose deux routes :

- `/login` : permet de se connecter
- `/private` : accessible uniquement après authentification

Une fois authentifié, l’utilisateur peut accéder au message :
Accès au contenu privé autorisé


---

## Membres du groupe

- Baptiste Marie

---

## Structure du dépôt

├── README.md
└── probleme2
├── guide.md
└── app.py


- `guide.md` : guide expliquant toutes les étapes pour déployer la solution
- `app.py` : application web Flask utilisée dans le projet

---

## Remarques / Motivations

> Python et Flask ont été choisis car ils permettent de créer rapidement une application web dynamique simple à comprendre.

> Gunicorn est utilisé comme gestionnaire de processus car il est très utilisé pour déployer des applications Python.

> Caddy est utilisé comme serveur web et reverse proxy car il est explicitement demandé dans le sujet.

> Fail2ban est utilisé pour détecter et bloquer automatiquement les tentatives de connexion suspectes.

---

## Références

- https://flask.palletsprojects.com/
- https://gunicorn.org/
- https://caddyserver.com/docs/
- https://www.fail2ban.org/wiki/index.php/Main_Page
- https://www.it-connect.fr/premiers-pas-avec-fail2ban/#A_Les_prisons_jails