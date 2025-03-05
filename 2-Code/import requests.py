import requests
import xml.etree.ElementTree as ET

def acceder_container():
    url = ("https://projetocrstorageacc.blob.core.windows.net/invoices-2018?"
           "restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&"
           "se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&"
           "sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parsing de la réponse XML
        racine = ET.fromstring(response.content)
        # Affichage des noms de blobs présents dans le container
        for blob in racine.findall(".//Blob"):
            nom = blob.find("Name").text
            print("Nom du blob :", nom)
    else:
        print("Erreur lors de l'accès à l'API, code HTTP :", response.status_code)

if __name__ == "__main__":
    acceder_container()
