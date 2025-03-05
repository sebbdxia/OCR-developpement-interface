import urllib.request
import xml.etree.ElementTree as ET
import os

def telecharger_blobs():
    # URL pour lister le container avec les paramètres du SAS token
    liste_url = ("https://projetocrstorageacc.blob.core.windows.net/invoices-2018?"
                 "restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&"
                 "se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&"
                 "sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D")
    
    try:
        with urllib.request.urlopen(liste_url) as response:
            contenu = response.read()
    except Exception as e:
        print("Erreur lors de la récupération de la liste du container :", e)
        return
    
    # Interprétation de la réponse XML pour extraire la liste des blobs
    racine = ET.fromstring(contenu)
    
    # Dossier de destination local
    destination_dir = r"C:\Users\sbond\Desktop\OCR developpement interface\1-Data"
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    # Token pour le téléchargement des blobs (sans les paramètres propres au listing)
    token = ("sv=2019-12-12&ss=b&srt=sco&sp=rl&"
             "se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&"
             "spr=https&sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D")
    
    base_url = "https://projetocrstorageacc.blob.core.windows.net/invoices-2018"
    
    # Pour chaque blob listé, construction de l'URL de téléchargement et sauvegarde du fichier
    for blob in racine.findall(".//Blob"):
        blob_name = blob.find("Name").text
        download_url = f"{base_url}/{blob_name}?{token}"
        print("Téléchargement de :", blob_name)
        try:
            with urllib.request.urlopen(download_url) as blob_response:
                blob_content = blob_response.read()
            destination_file = os.path.join(destination_dir, blob_name)
            with open(destination_file, "wb") as f:
                f.write(blob_content)
            print(f"Téléchargement de {blob_name} terminé.")
        except Exception as e:
            print(f"Erreur lors du téléchargement de {blob_name} :", e)

if __name__ == "__main__":
    telecharger_blobs()
