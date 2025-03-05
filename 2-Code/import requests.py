import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def recuperer_blobs():
    # Définition de l'URL avec le SAS token inclus
    sas_token = os.getenv("SAS_TOKEN")
    url = (f"https://projetocrstorageacc.blob.core.windows.net/invoices-2018?"
           f"restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&"
           f"se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&"
           f"sig={sas_token}")
    try:
        # Exécution de la requête GET
        response = requests.get(url)
        response.raise_for_status()  # Vérifie qu'il n'y a pas eu d'erreur HTTP

        # Parsing de la réponse XML
        racine = ET.fromstring(response.content)
        for blob in racine.findall(".//Blob"):
            nom = blob.find("Name").text
            print(nom)
    except Exception as e:
        print("Une erreur s'est produite lors de l'accès à l'API :", e)

if __name__ == "__main__":
    recuperer_blobs()
