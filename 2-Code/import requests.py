import urllib.request
import xml.etree.ElementTree as ET

def acceder_container():
    url = ("https://projetocrstorageacc.blob.core.windows.net/invoices-2018?"
           "restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&"
           "se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&"
           "sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D")
    
    try:
        with urllib.request.urlopen(url) as response:
            contenu = response.read()
            racine = ET.fromstring(contenu)
            for blob in racine.findall(".//Blob"):
                nom = blob.find("Name").text
                print("Nom du blob :", nom)
    except Exception as e:
        print("Une erreur s'est produite lors de l'accès au container :", e)

if __name__ == "__main__":
    acceder_container()
