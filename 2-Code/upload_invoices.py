# upload_invoices.py - Script pour téléverser les factures vers Azure Blob Storage

import os
import sys
from azure.storage.blob import BlobServiceClient, ContentSettings

# Configuration Azure Blob Storage
CONTAINER_NAME = "invoices-2018"  # Le même que dans votre application

def upload_files_to_azure(folder_path, connection_string):
    """
    Téléverse tous les fichiers d'un dossier vers Azure Blob Storage
    
    Args:
        folder_path: Chemin du dossier contenant les fichiers à téléverser
        connection_string: Chaîne de connexion Azure Storage
    """
    try:
        # Vérifier que le dossier existe
        if not os.path.exists(folder_path):
            print(f"Erreur: Le dossier {folder_path} n'existe pas")
            return False
        
        # Vérifier la chaîne de connexion
        if not connection_string:
            print("Erreur: La chaîne de connexion Azure Storage est vide")
            return False
        
        # Créer un client Azure Blob Storage
        print("Connexion à Azure Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Créer le conteneur s'il n'existe pas
        try:
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            # Vérifier si le conteneur existe
            container_client.get_container_properties()
            print(f"Conteneur '{CONTAINER_NAME}' trouvé")
        except Exception as e:
            print(f"Erreur lors de la vérification du conteneur: {str(e)}")
            print("Création du conteneur...")
            # Créer le conteneur s'il n'existe pas
            container_client = blob_service_client.create_container(CONTAINER_NAME)
            print(f"Conteneur '{CONTAINER_NAME}' créé")
        
        # Parcourir tous les fichiers du dossier
        files_uploaded = 0
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Ne téléverser que les fichiers, pas les sous-dossiers
            if os.path.isfile(file_path):
                # Déterminer le type MIME à partir de l'extension
                content_type = "application/octet-stream"  # Par défaut
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    content_type = "image/jpeg"
                elif filename.lower().endswith('.png'):
                    content_type = "image/png"
                elif filename.lower().endswith('.pdf'):
                    content_type = "application/pdf"
                
                # Créer le blob avec le type de contenu approprié
                blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
                
                # Téléverser le fichier
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(
                        data, 
                        overwrite=True,
                        content_settings=ContentSettings(content_type=content_type)
                    )
                    print(f"Fichier '{filename}' téléversé avec succès")
                    files_uploaded += 1
        
        print(f"\nOpération terminée: {files_uploaded} fichiers téléversés vers Azure Blob Storage")
        print(f"Container: {CONTAINER_NAME}")
        return True
    
    except Exception as e:
        print(f"Erreur lors du téléversement: {str(e)}")
        return False

if __name__ == "__main__":
    # Vérifier si un chemin de dossier a été fourni en argument
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        # Demander le chemin du dossier
        folder_path = input("Entrez le chemin du dossier contenant les factures: ")
    
    # Demander la chaîne de connexion Azure Storage
    connection_string = input("Entrez la chaîne de connexion Azure Storage: ")
    
    upload_files_to_azure(folder_path, connection_string)