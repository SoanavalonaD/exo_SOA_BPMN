from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Hôtel & Restaurant API")



class ArticleStock(BaseModel):
    nom: str
    quantite: int

class Chambre(BaseModel):
    numero: int
    categorie: str  
    tarif: float
    est_propre: bool = True 

class Reservation(BaseModel):
    client_nom: str
    piece_identite: str # [cite: 8]
    categorie_chambre: str
    nuitees: int

class Facture(BaseModel):
    id_facture: int
    montant_total: float
    est_payee: bool
    inclut_restaurant: bool = False



stock = {
    "gel douche": 100,
    "papier hygiénique": 100,
    "pantoufle": 100,
    "broche à dent": 100
}

chambres = [
    Chambre(numero=101, categorie="Standard", tarif=50.0, est_propre=True),
    Chambre(numero=201, categorie="Suite Senior", tarif=120.0, est_propre=True),
    Chambre(numero=301, categorie="Suite Prestige", tarif=250.0, est_propre=True)
]


@app.post("/reservations/", response_model=Facture)
def creer_reservation(res: Reservation):
    chambre_dispo = next((c for c in chambres if c.categorie == res.categorie_chambre and c.est_propre), None)
    
    if not chambre_dispo:
        raise HTTPException(status_code=400, detail="Aucune chambre propre disponible dans cette catégorie")

    articles_requis = ["gel douche", "papier hygiénique", "pantoufle", "broche à dent"]
    for art in articles_requis:
        if stock[art] < res.nuitees:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour l'article: {art}")
        stock[art] -= res.nuitees

    chambre_dispo.est_propre = False

    montant = chambre_dispo.tarif * res.nuitees
    return Facture(id_facture=123, montant_total=montant, est_payee=True)

@app.post("/menage/{numero_chambre}")
def effectuer_menage(numero_chambre: int):
    chambre = next((c for c in chambres if c.numero == numero_chambre), None)
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")
    
    chambre.est_propre = True
    return {"message": f"Chambre {numero_chambre} nettoyée et remise en vente"}

@app.get("/comptable/dashboard")
def generer_tableau_de_bord():
    return {
        "stock_actuel": stock,
        "chambres_occupees_ou_sales": [c.numero for c in chambres if not c.est_propre],
        "message": "Tableau de bord généré pour vérification des stocks"
    }

@app.post("/restaurant/commande")
def commander_restaurant(montant: float, additionner_a_la_chambre: bool):
    if additionner_a_la_chambre:
        return {"message": "Somme transférée à la facture de la chambre", "montant": montant} 
    return {"message": "Paiement direct au restaurant effectué"}