# Configuration des variables d'environnement

Le projet utilise maintenant des variables d'environnement pour configurer les ports et d'autres paramètres sensibles. Cela rend le déploiement plus flexible.

## Variables disponibles

Voici les variables d'environnement configurables dans le fichier `.env` :

| Variable | Description | Valeur par défaut |
|----------|-------------|------------------|
| `DISCORD_TOKEN` | Token d'authentification pour le bot Discord | (Aucune - **Obligatoire**) |
| `DB_PORT` | Port externe pour la base de données PostgreSQL | 5432 |
| `RASA_PORT` | Port externe pour le serveur Rasa | 5005 |
| `ACTIONS_PORT` | Port externe pour le serveur d'actions Rasa | 5055 |

## Comment utiliser les variables d'environnement

Vous pouvez configurer ces variables de deux façons :

### 1. Via le fichier .env

Créez ou modifiez le fichier `.env` à la racine du projet :

```ini
# Exemple de fichier .env
DISCORD_TOKEN=votre_token_discord_ici
DB_PORT=5433  # Changé de 5432 à 5433
RASA_PORT=5006  # Changé de 5005 à 5006
ACTIONS_PORT=5055  # Valeur par défaut
```

### 2. Via la ligne de commande

Vous pouvez aussi définir ces variables directement lorsque vous lancez docker-compose :

```bash
DB_PORT=5433 RASA_PORT=5006 docker-compose up -d
```

## Vérification des ports

Pour vérifier quels ports sont utilisés, exécutez :

```bash
docker-compose ps
```

Cela affichera les mappings de ports actuellement utilisés par vos conteneurs.
