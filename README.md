# Epic Events - CRM CLI Application

Epic Events est une application en ligne de commande (CLI) développée en Python. Elle permet de gérer les collaborateurs, les clients, les contrats et les événements liés, avec une interface sécurisée par JWT, des permissions par rôle, et un suivi des erreurs via Sentry.

---

##Fonctionnalités

- 🔐 Authentification JWT
- 🧑‍💼 Gestion des collaborateurs (création, modification..)
- 🧾 Gestion des clients, contrats, et événements
- ⚙️ Interface en ligne de commande avec Click
- 🔒 Permissions par rôle (`gestion`, `commercial`, `support`)
- 📊 Journalisation des erreurs et actions importantes via Sentry
- ✅ Tests unitaires, CLI et d'intégration avec Pytest + Pytest-Cov
- 🧪 Couverture de tests supérieure à 60 %

---

##Installation

1. Cloner le projet

```bash
git clone https://github.com/ton-utilisateur/epic_events.git
cd epic_events
``` 

2. Créer un environnement virtuel
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
``` 

3. Installer les dépendances
``` bash
pip install -r requirements.txt
``` 

4. Créer la base de données PostgreSQL
Configurer .env ou vos variables d’environnement :

DB_NAME=epic_event
DB_USER=postgres
DB_PASSWORD=ton_mot_de_passe
DB_HOST=localhost
DB_PORT=5432


5. Initialiser la base de données
``` bash
python -m app.db.init_db
``` 

🔐 Authentification
L’application utilise des tokens JWT générés via :
``` bash
python -m app.cli.main login
``` 

Le token est ensuite utilisé pour exécuter les commandes CLI protégées :
``` bash
python -m app.cli.main create-client --token <your_token>
``` 

📦 Commandes CLI disponibles
``` bash
python -m app.cli.main --help
``` 
Les principales commandes sont :

login
create-client
update-client
create-contract
update-contract
create-event
update-event
create-collaborator
delete-collaborator
sign-contracts

🐛 Journalisation avec Sentry
Le projet utilise Sentry pour remonter les erreurs et messages d’information :
Toutes les exceptions critiques sont capturées via capture_exception()
Les actions importantes (signature, création…) via logger.info()
Le DSN est stocké dans une variable d’environnement : SENTRY_DSN=https://xxx@o12345.ingest.sentry.io/12345
