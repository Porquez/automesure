# coding: utf-8 
import json
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

# Classe pour la gestion des donnees patient
class Patient:
    def __init__(self, id_patient, nom, prenom, date_naissance, age, antecedents):
        self.id_patient = id_patient
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.age = age
        self.antecedents = antecedents

# Classe pour la gestion des donnees de la tension
class Tension:
    def __init__(self, sys, dia, pouls, id_patient, date_heure):
        self.id_patient = id_patient
        self.sys = sys
        self.dia = dia
        self.pouls = pouls
        self.date_heure = date_heure

# Fonction pour se connecter a la base de donnees mongodb
def connect_to_db():
    with open(r"config.json") as f:
        config = json.load(f)
        client = MongoClient(
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            authSource='admin',
            authMechanism='MONGODB-X509'
        )
    db = client[config["database"]]
    return db
    
# Fonction pour inserer une mesure de tension dans la base de donnees
def insert_tension(db, patient, sys, dia, pouls):
    collection = db["tensions"]
    date_heure = datetime.now()
    tension = Tension(sys, dia, pouls, patient.id_patient, date_heure)
    collection.insert_one({"id_patient": patient.id_patient, "tension": tension.__dict__})

# Fonction pour afficher le dernier releve de tension enregistre en base de donnees
def show_last_tension(db,patient):
    collection = db["tensions"]
    cursor = collection.find().sort("tension.date_heure", DESCENDING).limit(1)
    last_tension = cursor.limit(1)[0]
    print("Derniere mesure de tension pour le patient numero {}:".format(patient.id_patient))
    print("Systolique  : {}".format(last_tension["tension"]["sys"]))
    print("Diastolique : {}".format(last_tension["tension"]["dia"]))
    print("Pouls       : {}".format(last_tension["tension"]["pouls"]))
    print("Patient     : {} {}, ne le {} age {}".format(patient.nom, patient.prenom, patient.date_naissance, patient.age))


# Fonction principale pour enregistrement des mesures de tension
def main():
    # Creation de objet patient
    patient = Patient("1","Doe", "John", "01/01/1980", 41, "Aucun")

    # Connexion e la base de donnees
    db = connect_to_db()

    # Interface graphique tkinter
    root = tk.Tk()
    root.geometry("300x300")
    root.title("Automesure Tensionnelle")
    
    tension1 = Tension(120, 80, 70, patient.id_patient, datetime.now())
    insert_tension(db,patient,tension1.sys,tension1.dia,tension1.pouls)
    show_last_tension(db,patient)

if __name__ == '__main__':
    main()    