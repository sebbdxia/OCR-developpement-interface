import urllib.request
import xml.etree.ElementTree as ET
import os
import datetime

def telecharger_factures_par_annee():
    # Répertoire de destination de base
    destination_dir_base = r"C:\Users\sbond\Desktop\OCR developpement interface\1-Data"
    if not os.path.exists(destination_dir_base):
        os.makedirs(destination_dir_base)
    
    base_url = "https://projetocrstorageacc.blob.core.windows.net"
    # Paramètres SAS pour l'énumération et le téléchargement
    listing_params = (
        "?restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&"
        "se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&"
        "sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D"
    )
    download_params = (
        "sv=2019-12-12&ss=b&srt=sco&sp=rl&"
        "se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&"
        "sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D"
    )
    
    # Définition de la période : de 2018 à l'année actuelle (incluse)
    annee_debut = 2018
    annee_fin = datetime.datetime.now().year + 1

    for annee in range(annee_debut, annee_fin):
        container = f"invoices-{annee}"
        # Création du sous-dossier pour l'année en cours
        destination_dir = os.path.join(destination_dir_base, str(annee))
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        
        liste_url = f"{base_url}/{container}{listing_params}"
        print(f"Accès au container : {container}")
        try:
            with urllib.request.urlopen(liste_url) as response:
                contenu = response.read()
        except Exception as e:
            print(f"Erreur lors de l'accès au container {container} : {e}")
            continue
        
        racine = ET.fromstring(contenu)
        blobs = racine.findall(".//Blob")
        if not blobs:
            print(f"Aucun blob trouvé dans le container {container}")
            continue
        
        for blob in blobs:
            blob_name = blob.find("Name").text
            download_url = f"{base_url}/{container}/{blob_name}?{download_params}"
            print(f"Téléchargement de {blob_name} depuis le container {container}")
            try:
                with urllib.request.urlopen(download_url) as blob_response:
                    blob_content = blob_response.read()
                # Enregistre le fichier dans le sous-dossier de l'année
                destination_file = os.path.join(destination_dir, blob_name)
                with open(destination_file, "wb") as f:
                    f.write(blob_content)
                print(f"Téléchargement de {blob_name} du container {container} terminé.")
            except Exception as e:
                print(f"Erreur lors du téléchargement de {blob_name} du container {container} : {e}")

if __name__ == "__main__":
    telecharger_factures_par_annee()
