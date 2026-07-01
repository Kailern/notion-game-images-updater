# Notion Game Images Updater

> **Script Python pour mettre à jour automatiquement les images des jeux dans une base de données Notion à partir de leur IGDB ID ou lien HowLongToBeat.**

---

## 📌 Fonctionnement

Ce script permet de :
- **Récupérer** les jeux d'une base de données Notion qui n'ont **pas encore d'image**.
- **Télécharger** automatiquement la couverture du jeu depuis :
  - [IGDB](https://www.igdb.com/) (via leur API officielle, nécessite une clé API Twitch).
  - [HowLongToBeat](https://howlongtobeat.com/) (via scraping, si l'IGDB ID n'est pas disponible).
- **Mettre à jour** la propriété `Image` ou `Cover` de chaque jeu dans Notion avec l'URL de l'image trouvée.
- **Éviter les doublons** : un jeu déjà doté d'une image ne sera pas traité.

---

## 🛠 Prérequis

### 1. **Clés API**
- **Notion** :
  - Crée une [intégration Notion](https://www.notion.so/my-integrations).
  - Note la **clé secrète** (ex: `secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`).
  - Partage ta base de données avec cette intégration (clique sur **Partager > Inviter une personne** et sélectionne ton intégration).

- **IGDB (Twitch)** :
  - Crée un compte développeur sur [Twitch Developer Console](https://dev.twitch.tv/console).
  - Crée une **application** (nom : `Notion Game Images Updater`, redirect URI : `http://localhost`).
  - Note le **Client ID** et génère un **Client Secret**.

### 2. **Python 3.8+**
- Installe les dépendances :
  ```bash
  pip install requests python-dotenv beautifulsoup4
  ```

---

## 📂 Structure du projet

```
notion-game-images-updater/
├── .env.example          # Exemple de fichier de configuration
├── .gitignore            # Fichiers à ignorer
├── README.md             # Ce fichier
├── requirements.txt      # Dépendances Python
├── config.py            # Configuration centralisée
└── main.py               # Script principal
```

---

## 🔧 Configuration

### 1. **Fichier `.env`**
Crée un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Notion
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=1234567890abcdef1234567890abcdef

# IGDB (Twitch)
IGDB_CLIENT_ID=xxxxxxxxxxxxxxxxxxxx
IGDB_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Propriétés Notion (à adapter selon ta base)
NOTION_IMAGE_PROPERTY=Image
NOTION_IGDB_ID_PROPERTY=IGDB ID
NOTION_HLTB_URL_PROPERTY=HowLongToBeat
```

> ⚠️ **Ne partage jamais ton fichier `.env`** (ajoute-le au `.gitignore`).

### 2. **Propriétés Notion**
Assure-toi que ta base de données Notion contient les propriétés suivantes :
- **`IGDB ID`** (type : `Nombre` ou `Texte`) : l'ID du jeu sur IGDB (ex: `12345`).
- **`HowLongToBeat`** (type : `URL`) : le lien du jeu sur HLTB (ex: `https://howlongtobeat.com/game.php?detail=12345`).
- **`Image`** (type : `URL` ou `Média`) : la propriété où stocker l'URL de l'image.

---

## 🚀 Utilisation

### 1. **Installation**
Clone le dépôt et installe les dépendances :
```bash
git clone https://github.com/Kailern/notion-game-images-updater.git
cd notion-game-images-updater
pip install -r requirements.txt
```

### 2. **Lancer le script**
```bash
python main.py
```

### 3. **Automatisation**
Pour exécuter le script régulièrement (ex: tous les jours) :
- **GitHub Actions** : Crée un workflow `.github/workflows/update_images.yml` :
  ```yaml
  name: Update Game Images
  on:
    schedule:
      - cron: '0 0 * * *'  # Tous les jours à minuit
    workflow_dispatch:     # Permet de lancer manuellement
  jobs:
    update:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v4
          with:
            python-version: '3.10'
        - run: pip install -r requirements.txt
        - run: python main.py
          env:
            NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
            NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
            IGDB_CLIENT_ID: ${{ secrets.IGDB_CLIENT_ID }}
            IGDB_CLIENT_SECRET: ${{ secrets.IGDB_CLIENT_SECRET }}
  ```
  > ⚠️ Ajoute les secrets (`NOTION_API_KEY`, etc.) dans **Settings > Secrets > Actions** de ton dépôt GitHub.

- **Local (cron)** :
  ```bash
  crontab -e
  ```
  Ajoute la ligne :
  ```cron
  0 0 * * * /chemin/vers/python /chemin/vers/notion-game-images-updater/main.py
  ```

---

## 📜 Exemples

### Base de données Notion
| Nom          | IGDB ID | HowLongToBeat                          | Image                          |
|--------------|---------|----------------------------------------|--------------------------------|
| The Witcher 3| 1900    | https://howlongtobeat.com/game.php?... | (vide)                         |
| Elden Ring   | 15475   | https://howlongtobeat.com/game.php?... | https://images.igdb.com/...   |

- **The Witcher 3** : pas d'image → le script va chercher sur IGDB ou HLTB et mettre à jour.
- **Elden Ring** : image déjà présente → ignoré.

---

## ❓ FAQ

### Pourquoi utiliser IGDB en priorité ?
IGDB propose des images en **haute résolution** et standardisées (format `cover_big`). HowLongToBeat est utilisé en fallback.

### Comment obtenir un IGDB ID pour un jeu ?
- Utilise la [recherche IGDB](https://www.igdb.com/search) ou leur API.
- Exemple : `https://api.igdb.com/v4/games?search="The Witcher 3"&fields=id`

### Le script est-il rapide ?
- Il traite **1 page toutes les 0.5 secondes** pour respecter les limites de Notion (3 requêtes/seconde).
- Pour 100 jeux, compte environ **50 secondes**.

---

## 🤝 Contribuer
Les contributions sont les bienvenues ! Ouvre une **issue** ou un **pull request** pour :
- Ajouter le support d'autres sources (Steam, RAWG, etc.).
- Améliorer la gestion des erreurs.
- Optimiser les performances.

---

## 📜 Licence
[MIT](https://choosealicense.com/licenses/mit/) – Libre d'utilisation, modification et distribution.