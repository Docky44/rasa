import re
import random
import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ActionReserveTable(Action):
    def name(self) -> Text:
        return "action_reserve_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug("=== Début de l'action action_reserve_table ===")
        
        # Récupération du message reçu
        message = tracker.latest_message.get("text", "")
        logger.debug("Message reçu: %s", message)
        
        # Affichage des entités extraites par le NLU
        entities = tracker.latest_message.get("entities", [])
        logger.debug("Entités extraites par le NLU: %s", entities)
        
        # Récupération des slots initialement extraits par le NLU
        date = tracker.get_slot("date")
        number_of_people = tracker.get_slot("number_of_people")
        name = tracker.get_slot("name")
        phone = tracker.get_slot("phone")
        logger.debug("Slots initiaux: date=%s, number_of_people=%s, name=%s, phone=%s",
                     date, number_of_people, name, phone)

        # Extraction de la date si nécessaire
        if not date:
            date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", message)
            if date_match:
                date = date_match.group(1)
                logger.debug("Date extraite (numérique): %s", date)
            else:
                date_match = re.search(
                    r"(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})",
                    message, re.IGNORECASE)
                if date_match:
                    date = date_match.group(1)
                    logger.debug("Date extraite (texte): %s", date)
                else:
                    logger.debug("Aucune date extraite par regex")
        
        # Extraction du nombre de personnes
        if not number_of_people:
            num_match = re.search(r"(\d+)\s*(?:personnes|pers\.?)", message, re.IGNORECASE)
            if num_match:
                number_of_people = num_match.group(1)
                logger.debug("Nombre de personnes extrait: %s", number_of_people)
            else:
                logger.debug("Aucun nombre de personnes extrait par regex")
        
        # Extraction du nom
        if not name:
            name_match = re.search(r"(?:au\s+nom(?:\s*de)?|nom(?:\s*de)?)\s*([A-ZÉÈÀÙ]{2,})", message, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).upper()
                logger.debug("Nom extrait (méthode 1): %s", name)
            else:
                name_match = re.search(r"(?:c(?:'|’)?est)\s*([A-ZÉÈÀÙ]{2,})", message, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).upper()
                    logger.debug("Nom extrait (méthode 2): %s", name)
                else:
                    logger.debug("Aucun nom extrait par regex")
        
        # Extraction du numéro de téléphone
        if not phone:
            phone_match = re.search(r"(0\d{9})", message)
            if phone_match:
                phone = phone_match.group(1)
                logger.debug("Numéro de téléphone extrait: %s", phone)
            else:
                logger.debug("Aucun numéro de téléphone extrait par regex")
        
        logger.debug("Slots après extraction: date=%s, number_of_people=%s, name=%s, phone=%s",
                     date, number_of_people, name, phone)
        
        # Si toutes les informations sont présentes, envoyer la confirmation directement
        if date and number_of_people and name and phone:
            reservation_number = random.randint(1000, 9999)
            logger.info("Réservation réussie, numéro: %s", reservation_number)
            dispatcher.utter_message(
                text=f"Réservation confirmée. Votre numéro de réservation est {reservation_number}."
            )
            return [{"slot": "reservation_number", "value": str(reservation_number)}]
        else:
            missing = []
            if not date:
                missing.append("date")
            if not number_of_people:
                missing.append("nombre de personnes")
            if not name:
                missing.append("nom")
            if not phone:
                missing.append("numéro de téléphone")
            logger.warning("Échec de la réservation, informations manquantes: %s", ", ".join(missing))
            dispatcher.utter_message(
                text="Il manque des informations pour finaliser la réservation: " + ", ".join(missing)
            )
            return []

class ActionCancelReservation(Action):
    def name(self) -> Text:
        return "action_cancel_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("Annulation de réservation demandée")
        dispatcher.utter_message(text="Votre réservation a été annulée.")
        return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("Fallback déclenché")
        dispatcher.utter_message(text="Je n'ai pas compris. Pouvez-vous reformuler ou préciser votre demande ?")
        return []
