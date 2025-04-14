import discord
import requests
import logging

# === Configuration des logs ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# === Configuration du bot et de Rasa ===
DISCORD_TOKEN = "MTM1NDAwNzcxNDI5NjEwNzA3OA.GmagkO.WNNH_9zGb0opWBctjU9xchxTOEQnUkU2l8rjyE"  # Remplacez par votre token Discord
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# Activez les intents, y compris le message_content
intents = discord.Intents.default()
intents.message_content = True  # Indispensable pour lire message.content

# Créez un client Discord avec ces intents
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f"Connecté sur Discord en tant que {client.user}")

@client.event
async def on_message(message):
    # Ignorer les messages du bot lui-même
    if message.author == client.user:
        return

    # Log du message reçu
    logger.debug(f"Message reçu de {message.author} (ID={message.author.id}): {message.content!r}")

    # Construire le payload pour Rasa
    payload = {
        "sender": str(message.author.id),
        "message": message.content
    }

    try:
        # Envoyer le message à Rasa
        response = requests.post(RASA_URL, json=payload)
        logger.debug(f"Envoi du message à Rasa : {payload}")
        logger.debug(f"Statut de la réponse : {response.status_code}")

        if response.status_code == 200:
            responses = response.json()
            logger.debug(f"Réponse reçue de Rasa : {responses}")

            # Pour chaque texte renvoyé par Rasa, l'envoyer sur Discord
            for r in responses:
                if "text" in r:
                    logger.debug(f"Envoi à Discord : {r['text']}")
                    await message.channel.send(r["text"])
        else:
            logger.warning(f"Échec de la requête Rasa : {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'envoi de la requête à Rasa : {e}")

# Lancement du bot
client.run(DISCORD_TOKEN)
