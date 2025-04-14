# Déploiement du Bot de Réservation avec Docker

Ce guide vous aide à déployer facilement votre bot de réservation RASA avec Docker et Docker Compose.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Structure des fichiers

Assurez-vous que votre structure de fichiers ressemble à ceci :

```
votre_projet/
├── actions/
│   ├── __init__.py
│   └── actions.py
├── bot/
│   └── main.py
├── data/
│   ├── nlu.yml
│   ├── rules.yml
│   └── stories.yml
├── models/
├── tests/
├── .env
├── config.yml
├── credentials.yml
├── domain.yml
├── endpoints.yml
├── Dockerfile.rasa
├── Dockerfile.actions
├── Dockerfile.discord
├── docker-compose.yml
└── requirements.txt
```

## Configuration

1. Renommez les fichiers Dockerfile :
   ```bash
   mv Dockerfile-rasa Dockerfile.rasa
   mv Dockerfile-actions Dockerfile.actions
   mv Dockerfile-discord Dockerfile.discord
   ```

2. Modifiez le fichier `.env` pour définir votre token Discord :
   ```
   DISCORD_TOKEN=votre_token_discord_ici
   ```

3. Assurez-vous que le fichier `endpoints.yml` pointe vers le bon service d'actions :
   ```yaml
   action_endpoint:
     url: "http://rasa-actions:5055/webhook"
   ```

## Déploiement

1. Construire les images Docker :
   ```bash
   docker-compose build
   ```

2. Démarrer les services :
   ```bash
   docker-compose up -d
   ```

3. Vérifier que tout fonctionne correctement :
   ```bash
   docker-compose logs -f
   ```

## Remarques importantes

- Le modèle RASA sera entraîné à chaque démarrage du conteneur Rasa.
- Les logs sont accessibles via la commande `docker-compose logs`.
- Pour arrêter tous les services : `docker-compose down`.
- Pour mettre à jour le bot après des modifications : `docker-compose build && docker-compose up -d`.

## Dépannage

Si le bot Discord ne peut pas se connecter à Rasa :
1. Vérifiez les logs des conteneurs : `docker-compose logs rasa discord-bot`
2. Assurez-vous que Rasa est complètement démarré avant de tenter de s'y connecter
3. Vérifiez que l'URL dans les variables d'environnement est correcte

Si le serveur d'actions ne fonctionne pas :
1. Vérifiez les logs : `docker-compose logs rasa-actions`
2. Vérifiez que les fichiers actions sont correctement copiés dans le conteneur
