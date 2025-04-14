import os
import logging
import psycopg2
from psycopg2 import pool
from datetime import datetime

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Récupération des variables d'environnement pour la connexion à la base de données
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "reservation")
DB_USER = os.getenv("DB_USER", "rasa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rasa")

# Création d'un pool de connexions
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # minconn
        10,  # maxconn
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    logger.info("Pool de connexions PostgreSQL créé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de la création du pool de connexions PostgreSQL: {e}")
    connection_pool = None

def get_connection():
    """
    Récupère une connexion du pool.
    Retourne None en cas d'erreur.
    """
    if connection_pool:
        try:
            return connection_pool.getconn()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération d'une connexion du pool: {e}")
    return None

def release_connection(conn):
    """
    Libère une connexion et la remet dans le pool.
    """
    if connection_pool and conn:
        try:
            connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Erreur lors de la libération d'une connexion: {e}")

def create_reservation(reservation_number, name, phone, date, number_of_people):
    """
    Crée une nouvelle réservation dans la base de données.

    Args:
        reservation_number (str): Numéro de réservation unique
        name (str): Nom du client
        phone (str): Numéro de téléphone
        date (str): Date de la réservation (format à convertir)
        number_of_people (str): Nombre de personnes

    Returns:
        bool: True si la réservation a été créée avec succès, False sinon
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Conversion du nombre de personnes en entier
        try:
            number_of_people_int = int(number_of_people)
        except (ValueError, TypeError):
            logger.error(f"Nombre de personnes invalide: {number_of_people}")
            return False

        # Conversion de la date en datetime
        try:
            # Tentative avec format JJ/MM/AAAA
            if "/" in date:
                date_parts = date.split("/")
                if len(date_parts) == 3:
                    day, month, year = map(int, date_parts)
                    date_obj = datetime(year, month, day)
                else:
                    logger.error(f"Format de date invalide: {date}")
                    return False
            # Tentative avec format texte (ex: 25 mars 2025)
            else:
                # Simplification : conversion manuelle des noms de mois en français
                months_fr = {
                    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
                    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
                    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
                }

                parts = date.split()
                if len(parts) == 3:
                    day = int(parts[0])
                    month_name = parts[1].lower()
                    year = int(parts[2])

                    if month_name in months_fr:
                        month = months_fr[month_name]
                        date_obj = datetime(year, month, day)
                    else:
                        logger.error(f"Nom de mois non reconnu: {month_name}")
                        return False
                else:
                    logger.error(f"Format de date en texte invalide: {date}")
                    return False
        except Exception as e:
            logger.error(f"Erreur lors de la conversion de la date {date}: {e}")
            return False

        # Insertion de la réservation
        query = """
        INSERT INTO reservations
        (reservation_number, name, phone, date, number_of_people, status)
        VALUES (%s, %s, %s, %s, %s, 'confirmed')
        RETURNING id
        """

        cursor.execute(query, (reservation_number, name, phone, date_obj, number_of_people_int))
        reservation_id = cursor.fetchone()[0]

        # Ajout d'un enregistrement dans l'historique
        history_query = """
        INSERT INTO reservation_history
        (reservation_id, action, details)
        VALUES (%s, 'create', %s)
        """

        details = f"Réservation créée pour {name} le {date_obj.strftime('%d/%m/%Y')} pour {number_of_people_int} personnes"
        cursor.execute(history_query, (reservation_id, details))

        conn.commit()
        logger.info(f"Réservation {reservation_number} créée avec succès")
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de la création de la réservation: {e}")
        return False
    finally:
        release_connection(conn)

def cancel_reservation(reservation_number=None, name=None, phone=None):
    """
    Annule une réservation en mettant à jour son statut.
    La réservation peut être identifiée par son numéro, le nom du client ou le téléphone.

    Args:
        reservation_number (str, optional): Numéro de réservation
        name (str, optional): Nom du client
        phone (str, optional): Numéro de téléphone

    Returns:
        bool: True si la réservation a été annulée avec succès, False sinon
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Vérification qu'au moins un paramètre est fourni
        if not any([reservation_number, name, phone]):
            logger.error("Aucun paramètre fourni pour annuler une réservation")
            return False

        # Construction de la requête en fonction des paramètres fournis
        query = "UPDATE reservations SET status = 'cancelled' WHERE "
        params = []

        if reservation_number:
            query += "reservation_number = %s"
            params.append(reservation_number)
        elif name:
            query += "UPPER(name) = UPPER(%s)"
            params.append(name)
        elif phone:
            query += "phone = %s"
            params.append(phone)

        query += " AND status = 'confirmed' RETURNING id, name, date"

        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            reservation_id, client_name, reservation_date = result

            # Ajout d'un enregistrement dans l'historique
            history_query = """
            INSERT INTO reservation_history
            (reservation_id, action, details)
            VALUES (%s, 'cancel', %s)
            """

            details = f"Réservation annulée pour {client_name} le {reservation_date.strftime('%d/%m/%Y')}"
            cursor.execute(history_query, (reservation_id, details))

            conn.commit()
            logger.info(f"Réservation {reservation_id} annulée avec succès")
            return True
        else:
            logger.warning("Aucune réservation active trouvée avec les paramètres fournis")
            return False

    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de l'annulation de la réservation: {e}")
        return False
    finally:
        release_connection(conn)

def get_reservation_details(reservation_number=None, name=None, phone=None):
    """
    Récupère les détails d'une réservation.

    Args:
        reservation_number (str, optional): Numéro de réservation
        name (str, optional): Nom du client
        phone (str, optional): Numéro de téléphone

    Returns:
        dict: Détails de la réservation ou None si non trouvée
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        # Vérification qu'au moins un paramètre est fourni
        if not any([reservation_number, name, phone]):
            logger.error("Aucun paramètre fourni pour récupérer les détails d'une réservation")
            return None

        # Construction de la requête en fonction des paramètres fournis
        query = """
        SELECT id, reservation_number, name, phone, date, number_of_people, status
        FROM reservations
        WHERE
        """
        params = []

        if reservation_number:
            query += "reservation_number = %s"
            params.append(reservation_number)
        elif name:
            query += "UPPER(name) = UPPER(%s)"
            params.append(name)
        elif phone:
            query += "phone = %s"
            params.append(phone)

        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            return {
                "id": result[0],
                "reservation_number": result[1],
                "name": result[2],
                "phone": result[3],
                "date": result[4],
                "number_of_people": result[5],
                "status": result[6]
            }
        else:
            return None

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails de la réservation: {e}")
        return None
    finally:
        release_connection(conn)

# Si besoin de tester la connexion
def test_connection():
    """
    Teste la connexion à la base de données.

    Returns:
        bool: True si la connexion est établie, False sinon
    """
    conn = get_connection()
    if conn:
        release_connection(conn)
        return True
    return False
