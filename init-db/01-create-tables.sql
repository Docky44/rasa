-- Script d'initialisation de la base de données pour les réservations

-- Création de la table des réservations
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    reservation_number VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date TIMESTAMP NOT NULL,
    number_of_people INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index pour accélérer les recherches par numéro de réservation
CREATE INDEX idx_reservation_number ON reservations(reservation_number);

-- Index pour accélérer les recherches par nom
CREATE INDEX idx_name ON reservations(name);

-- Index pour accélérer les recherches par date
CREATE INDEX idx_date ON reservations(date);

-- Fonction pour mettre à jour le timestamp 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Trigger pour mettre à jour automatiquement 'updated_at' à chaque modification
CREATE TRIGGER update_reservations_updated_at
BEFORE UPDATE ON reservations
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table pour stocker l'historique des modifications de réservation
CREATE TABLE IF NOT EXISTS reservation_history (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER NOT NULL REFERENCES reservations(id),
    action VARCHAR(20) NOT NULL,
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index pour accélérer les recherches dans l'historique par réservation
CREATE INDEX idx_reservation_id ON reservation_history(reservation_id);
