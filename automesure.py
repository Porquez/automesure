# coding: utf-8 
import sys
from flask import Flask
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import csv

if len(sys.argv) > 1:
    id_patient = sys.argv[1]
else:
    id_patient = None

app = Flask(__name__)

#Fenetre Tkinter
class Application(tk.Frame):
    def __init__(self, parent, id_patient=None, *args, **kwargs):
        super().__init__(parent, id_patient=None, *args, **kwargs)
        self.master.title("Automesure Tensionnelle")
        self.master.geometry("800x800")

        self.pack()
        self.create_status_bar()
        label = tk.Label(self, text="tensiometre")

        #Creation des widgets pour le formulaire de creation de patient
        if id_patient:
            self.id_patient = id_patient
            patient = db.patients.find_one({"id_patient": self.id_patient})
            self.create_widgets(patient)
        else:
            self.id_patient = None
            self.create_widgets()
      
    def create_widgets(self,patient=None):
        self.label_id_patient = tk.Label(self, text="id patient")
        self.entry_id_patient = tk.Entry(self)
        self.label_nom = tk.Label(self, text="Nom")
        self.entry_nom = tk.Entry(self)
        self.label_prenom = tk.Label(self, text="Prenom")
        self.entry_prenom = tk.Entry(self)
        self.label_date_naissance = tk.Label(self, text="Date de naissance")
        self.entry_date_naissance = tk.Entry(self)
        self.label_age = tk.Label(self, text="Age")
        self.entry_age = tk.Entry(self)
        self.label_antecedents = tk.Label(self, text="Antecedents")
        self.entry_antecedents = tk.Entry(self)
        
        #Verification si le patient existe
        if patient:
            #Afficher les informations du patient existant
            self.entry_id_patient.insert(0, patient['id_patient'])
            self.entry_nom.insert(0, patient['nom'])
            self.entry_prenom.insert(0, patient['prenom'])
            self.entry_date_naissance.insert(0, patient['date_naissance'])
            self.entry_age.insert(0, patient['age'])
            self.entry_antecedents.insert(0, patient['antecedents'])
            #self.btn_enregistrer = tk.Button(self, text="Enregistrer", command=self.modifier_patient)
        #else:
            #Les zones de saisie sont vides
            #self.btn_enregistrer = tk.Button(self, text="Enregistrer", command=self.creer_patient, state='disabled')

        #Placer les widgets dans la fenetre
        #self.label_id_patient.grid(row=0, column=0)
        #self.entry_id_patient.grid(row=0, column=1)
        #self.label_nom.grid(row=1, column=0)
        #self.entry_nom.grid(row=1, column=1)
        ##self.label_prenom.grid(row=1, column=0)
        #self.entry_prenom.grid(row=1, column=1)
        #self.label_date_naissance.grid(row=2, column=0)
        ##self.entry_date_naissance.grid(row=2, column=1)
        #self.label_age.grid(row=2, column=0)
        #self.entry_age.grid(row=2, column=1)
        #self.label_antecedents.grid(row=2, column=0)
        #self.entry_antecedents.grid(row=2, column=1)
        #self.btn_enregistrer.grid(row=3, column=1)

        #Creation des widgets pour le formulaire de creation nouvelle tension
        self.label_sys = tk.Label(self, text="Tension Systolique")
        self.entry_sys = tk.Entry(self)
        self.label_dia = tk.Label(self, text="Tension Diastolique")
        self.entry_dia = tk.Entry(self)
        self.label_pou = tk.Label(self, text="Pouls")
        self.entry_pou = tk.Entry(self)

        self.bouton_creer_patient = tk.Button(self, text="Enregistrer patient", command=lambda: Patient.creer_patient(db, self.entry_id_patient.get(), self.entry_nom.get(), self.entry_prenom.get(), self.entry_date_naissance.get(),self.entry_age.get(),self.entry_antecedents.get()))
        self.bouton_creer_tension = tk.Button(self, text="Creer un nouveau releve de la tension", command=lambda: Tension.creer_tension(db, self.entry_id_patient.get(), self.entry_sys.get(),self.entry_dia.get(),self.entry_pou.get()))
        self.bouton_edition = tk.Button(self, text="Edition releve medecin", command=lambda: Patient.generer_pdf_medecin(db, self.entry_id_patient.get()))

        # Positionnement des widgets dans la fenetre
        self.label_id_patient.pack()
        self.entry_id_patient.pack()
        self.label_nom.pack()
        self.entry_nom.pack()
        self.label_prenom.pack()
        self.entry_prenom.pack()
        self.label_date_naissance.pack()
        self.entry_date_naissance.pack()
        self.label_age.pack()
        self.entry_age.pack()
        self.label_antecedents.pack()
        self.entry_antecedents.pack()
        self.bouton_creer_patient.pack()

        self.label_sys.pack()
        self.entry_sys.pack()
        self.label_dia.pack()
        self.entry_dia.pack()
        self.label_pou.pack()
        self.entry_pou.pack()
        self.bouton_creer_tension.pack()
      
        self.bouton_edition.pack()

        # Creation d'un bouton et d'une zone de texte pour le commentaire
        self.bouton_commentaire = tk.Button(self, text="Commentaire", command=self.afficher_commentaire)
        self.bouton_commentaire.pack(side=tk.LEFT)
        self.texte_commentaire = tk.Text(self, width=100 , height=18)
        self.texte_commentaire.pack(side=tk.LEFT)

    def create_status_bar(self):
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def afficher_commentaire(self):
        # Ouverture du fichier CSV et lecture des 10 premieres lignes
        with open(f"commentaires.txt", newline="") as f:
            reader = csv.reader(f)
            lignes = []
            for i, ligne in enumerate(reader):
                if i >= 20:
                    break
                lignes.append(ligne)
    
        # Affichage des 10 premieres lignes dans la zone de texte
        self.texte_commentaire.delete("1.0", tk.END)
        for ligne in lignes:
            self.texte_commentaire.insert(tk.END, ", ".join(ligne) + "\n")

# Classe pour la gestion des donnees patient
class Patient:
    def __init__(self, id_patient, nom, prenom, date_naissance, age, antecedents):
        self.id_patient = id_patient
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.age = age
        self.antecedents = antecedents

    @staticmethod
    def creer_patient(db, id_patient, nom, prenom, date_naissance, age, antecedents):
        # Inserer le nouveau patient dans la base de donnees
        patient = Patient(id_patient, nom, prenom, date_naissance, age, antecedents)
        db.patients.insert_one({
            "id_patient": patient.id_patient,
            "nom": patient.nom,
            "prenom": patient.prenom,
            "date_naissance": patient.date_naissance,
            "age": patient.age,
            "antecedents": patient.antecedents
        })
        messagebox.showinfo("Confirmation", f"patient { id_patient } creee.")

    @staticmethod
    def modifier_patient(db, id_patient, nom, prenom, date_naissance, age, antecedents):
        db.patients.update_one({"id_patient": id_patient},
                                {"$set": {"nom": nom,
                                            "prenom": prenom,
                                            "date_naissance": date_naissance,
                                            "age": age,
                                            "antecedents": antecedents}})
        messagebox.showinfo("Confirmation", f"patient { id_patient } modifiee.")

    @staticmethod
    @app.route("/medecin/generer_pdf/<id_patient>")
    def generer_pdf_medecin(db,id_patient):

        #patient = Patient.objects.get(id_patient).first()
        patient = db.patients.find_one({"id_patient": id_patient})

        # Date limite inferieure
        limite_inf = datetime.now() - timedelta(days=3)
        # Date limite superieure
        limite_sup = datetime.now()

        # Recuperer les tensions correspondantes
        #tensions = Tension.objects.filter(patient=patient, date_heure__gte=limite_inf, date_heure__lt=limite_sup)
        collection = db["tensions"]
        tensions = collection.find({"id_patient": id_patient, "date_heure": {"$gte": limite_inf, "$lt": limite_sup}})
        
        # Creer un objet Canvas pour generer le PDF
        pdf = canvas.Canvas("releve_automesure_tensionnelle.pdf", pagesize=A4)
        
        # Afficher les informations du patient et la periode du releve en haut a droite
        nom_patient = patient['nom']
        prenom_patient = patient['prenom']
        periode = f"{limite_inf.date()} - {limite_sup.date()}"
        pdf.drawString(A4[0]-250, A4[1]-50, f"Patient : {nom_patient} {prenom_patient}")
        pdf.drawString(A4[0]-250, A4[1]-70, f"Periode : {periode}")
        
        # Afficher les commentaires pour le medecin en haut a gauche
        commentaires = "Aucun commentaire pour le moment"
        pdf.drawString(50, A4[1]-50, "Commentaires pour le medecin :")
        pdf.drawString(50, A4[1]-70, commentaires)
        
        # Afficher les releves dans un tableau
        x_offset = 50
        y_offset = A4[1]-150
        for i, tension in enumerate(tensions):
            # Afficher la date et heure du releve
            pdf.drawString(x_offset, y_offset-i*20, tension['date_heure'].strftime("%d/%m/%Y %H:%M:%S"))
            #heure = tension['date_heure'].time()
            date_heure = tension['date_heure']
            heure_str = date_heure.strftime("%H:%M:%S")
            heure = datetime.strptime(heure_str, "%H:%M:%S").time()
            #if heure  datetime.strptime("11:59:00", "%H:%M:%S"):
            # Afficher la tension du matin
            #pdf.drawString(x_offset+80, y_offset-i*20, f"{tension.matin.sys}/{tension.matin.dia}/{tension.matin.pouls}")
            #pdf.drawString(x_offset+80, y_offset-i*20, f"{tension['sys']}/{tension['dia']}/{tension['pouls']}")
            #else:
            # Afficher la tension du soir
            #pdf.drawString(x_offset+160, y_offset-i*20, f"{tension.soir.sys}/{tension.soir.dia}/{tension.soir.pouls}")
        
        # Calculer les moyennes
        #moy_sys = round(sum(tension['tension']['matin']['sys'] + tension['tension']['soir']['sys'] for tension in tensions) / (2*len(tensions)), 1)
        #moy_dia = round(sum(tension['tension']['matin']['dia'] + tension['tension']['soir']['dia'] for tension in tensions) / (2*len(tensions)), 1)

        # Afficher les moyennes en bas de la derniere page
        #pdf.drawString(x_offset, 100, f"Moyenne systolique : {moy_sys}")
        #pdf.drawString(x_offset, 80, f"Moyenne diastolique : {moy_dia}")
        
        # Ajouter le filigrane
        pdf.setFont("Helvetica", 12)
        pdf.setStrokeColorRGB(0, 0, 0, alpha=0.1)

        # Sauvegarder le PDF et renvoyer une reponse au client
        pdf.save()
        #return send_file("releve_automesure_tensionnelle.pdf", as_attachment=True)        

# Classe pour la gestion des donnees de la tension
class Tension:
    def __init__(self, sys, dia, pouls, id_patient, date_heure):
        self.id_patient = id_patient
        self.sys = sys
        self.dia = dia
        self.pouls = pouls
        self.date_heure = date_heure

    @staticmethod
    def creer_tension(db, id_patient, sys, dia, pouls):
        patient = db.patients.find_one({"id_patient": id_patient})
        # Verifier si le patient existe deja dans la base de donnees
        if not patient:
            messagebox.showerror("Erreur", "Patient inexistant")
            return

        collection = db["tensions"]
        date_heure = datetime.now()

        # Verifier la duree depuis la derniere prise de tension
        derniere_tension = collection.find_one({"id_patient": id_patient}, sort=[("date_heure", -1)])
        if derniere_tension is not None:
            if 'date_heure' in derniere_tension:
                duree = (datetime.now() - derniere_tension['date_heure']).total_seconds() // 60
                if duree < 1:
                    messagebox.showerror("Erreur", "Tension deja prise il y a moins d'une minute")
                    return
        #heure_minute = date_heure.strftime("%H:%M")  # calcul de la colonne heure_minute
        # Inserer la nouvelle tension dans la base de donnees
        tension = Tension(sys, dia, pouls, id_patient, date_heure )
        collection.insert_one({"id_patient": id_patient, "date_heure": date_heure, "tension": tension.__dict__})
        messagebox.showinfo("Confirmation", f"Tension enregistree a {date_heure}.")
     
# Fonction pour se connecter a la base de donnees mongodb
def connect_to_db():
    with open(r"config.json") as f:
        config = json.load(f)
        client = MongoClient(
            host=config["host"],
            port=config["port"]
        )
    db = client[config["database"]]
    return db
    
# Fonction pour inserer une mesure de tension dans la base de donnees
def insert_tension(db, patient, sys, dia, pouls):
    collection = db["tensions"]
    date_heure = datetime.now()
    tension = Tension(sys, dia, pouls, patient.id_patient, date_heure)
    collection.insert_one({"id_patient": patient.id_patient, "tension": tension.__dict__})

def insert_patient(db, patient):
    #collection = db["patient"]
    #patient = Patient(patient)
    db.patients.insert_one({"id_patient": patient.id_patient,
            "nom": patient.nom,
            "prenom": patient.prenom,
            "date_naissance": patient.date_naissance,
            "age": patient.age,
            "antecedents": patient.antecedents})

# Fonction pour afficher le dernier releve de tension enregistre en base de donnees
def show_last_tension(db,patient):
    collection = db["tensions"]
    cursor = collection.find().sort("tension.date_heure", DESCENDING).limit(1)
    last_tension = cursor.limit(1)[0]
    print("Derniere mesure de tension pour le patient le {}:".format(last_tension["tension"]["date_heure"]))
    print("Systolique  : {}".format(last_tension["tension"]["sys"]))
    print("Diastolique : {}".format(last_tension["tension"]["dia"]))
    print("Pouls       : {}".format(last_tension["tension"]["pouls"]))
    print("Patient     : {} {} {}, ne le {} age {}".format(patient.id_patient,patient.nom, patient.prenom, patient.date_naissance, patient.age))

def generer_fiche_releve(db,patient,date):
    collection = db['tensions']
    cursor = collection.find({
        'date_heure': {'$gte': date, '$lt': date + timedelta(days=1)}
    })
    fiche = f"Fiche de releve automesure tensionnelle du {date.strftime('%d/%m/%Y')} :\n"
    for tension in cursor:
        fiche += f"Systolique : {tension['sys']} - Diastolique : {tension['dia']} - Pouls : {tension['pouls']} - Nom : {tension['nom']} - Prenom : {tension['prenom']}\n"
    with open(f"releve_{date.strftime('%Y%m%d')}.txt", "w") as file:
        file.write(fiche)

#Fonction pour generer la fiche de releve des mesures de la tension pour le medecin
def generer_pdf_medecin(id_patient):

    patient = Patient.objects(id=id_patient).first()

    # Date limite inferieure
    limite_inf = datetime.now() - timedelta(days=3)
    # Date limite superieure
    limite_sup = datetime.now()

    # Requete pour recuperer les tensions entre les deux dates
    query = {"date_heure": {"$gte": limite_inf, "$lt": limite_sup}}

    # Recuperer les tensions correspondantes
    tensions = db.tensions.find(query)

    # Creer un objet Canvas pour generer le PDF
    pdf = canvas.Canvas("releve_automesure_tensionnelle.pdf", pagesize=A4)
    
    # Afficher les informations du patient et la periode du releve en haut a droite
    pdf.drawString(A4[0]-250, A4[1]-50, f"Patient : {nom_patient} {prenom_patient}")
    pdf.drawString(A4[0]-250, A4[1]-70, f"Periode : {periode}")
    
    # Afficher les commentaires pour le medecin en haut a gauche
    pdf.drawString(50, A4[1]-50, "Commentaires pour le medecin :")
    pdf.drawString(50, A4[1]-70, commentaires)
    
    # Afficher les releves dans un tableau
    x_offset = 50
    y_offset = A4[1]-150
    for i, tension in enumerate(tensions):
        # Afficher la date du releve
        pdf.drawString(x_offset, y_offset-i*20, str(tension['date_heure'].date()))
        
        heure = tension['date_heure'].time()
        if heure >= datetime.time(6, 0) and heure < datetime.time(12, 0):
            # Afficher la tension du matin
            pdf.drawString(x_offset+80, y_offset-i*20, f"{tension['tension']['matin']['sys']}/{tension['tension']['matin']['dia']}/{tension['tension']['matin']['pouls']}")
        else:
            # Afficher la tension du soir
            pdf.drawString(x_offset+160, y_offset-i*20, f"{tension['tension']['soir']['sys']}/{tension['tension']['soir']['dia']}/{tension['tension']['soir']['pouls']}")

# Fonction principale pour enregistrement des mesures de tension
if __name__ == '__main__':

    #Connexion e la base de donnees
    db = connect_to_db()

    # Creation de objet patient
    patient = Patient("1","Doe", "John", "01/01/1980", 41, "Aucun")
    
    # Creation releve tension
    tension1 = Tension(120, 80, 70, patient.id_patient, datetime.now())
   
    insert_patient(db,patient)
    insert_tension(db,patient, tension1.sys, tension1.dia, tension1.pouls)

    root = tk.Tk()
    app = Application(root,id_patient)
    app.pack()
    
    show_last_tension(db,patient)
    generer_fiche_releve(db,patient,datetime.now())

    root.mainloop()    