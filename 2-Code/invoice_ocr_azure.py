# invoice_ocr_azure.py - Application OCR pour traiter les factures depuis Azure Blob Storage

import os
import io
import json
import uuid
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import re
import logging
from azure.storage.blob import BlobServiceClient
import requests
import xml.etree.ElementTree as ET

# ------ Configuration de l'environnement ------
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration MongoDB
app.config["MONGO_URI"] = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ocr-app")
mongo = PyMongo(app)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Azure Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = "invoices-2018"
AZURE_SAS_URL = "https://projetocrstorageacc.blob.core.windows.net/invoices-2018?restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D"

# ------ Modèle de données MongoDB ------
class InvoiceModel:
    def __init__(self, mongo):
        self.collection = mongo.db.invoices
    
    def save_invoice(self, invoice_data):
        return self.collection.insert_one(invoice_data)
    
    def get_invoice(self, invoice_id):
        from bson.objectid import ObjectId
        return self.collection.find_one({"_id": ObjectId(invoice_id)})
    
    def get_all_invoices(self):
        return list(self.collection.find())

# ------ Classe d'extraction de facture ------
class InvoiceExtractor:
    def extract_invoice_data(self, text):
        """
        Extrait les données spécifiques de notre facture type
        """
        invoice_data = {
            "invoiceNumber": None,
            "date": None,
            "recipient": None,
            "address": None,
            "items": [],
            "totalAmount": None,
            "currency": None,
            "processingDate": datetime.now()
        }
        
        # Extraire le numéro de facture (format FAC/YYYY/XXXX)
        invoice_number_regex = r"INVOICE\s+FAC/(\d{4}/\d{4})"
        invoice_number_match = re.search(invoice_number_regex, text, re.IGNORECASE)
        if invoice_number_match:
            invoice_data["invoiceNumber"] = "FAC/" + invoice_number_match.group(1)
        else:
            # Recherche alternative
            alt_invoice_regex = r"FAC/\d{4}/\d{4}"
            alt_match = re.search(alt_invoice_regex, text)
            if alt_match:
                invoice_data["invoiceNumber"] = alt_match.group(0)
        
        # Extraire la date (format YYYY-MM-DD)
        date_regex = r"Issue\s+date\s+(\d{4}-\d{2}-\d{2})"
        date_match = re.search(date_regex, text, re.IGNORECASE)
        if date_match:
            invoice_data["date"] = date_match.group(1)
        
        # Extraire le destinataire
        recipient_regex = r"Bill\s+to\s+([\w\s]+)"
        recipient_match = re.search(recipient_regex, text, re.IGNORECASE)
        if recipient_match:
            invoice_data["recipient"] = recipient_match.group(1).strip()
        
        # Extraire l'adresse
        address_regex = r"Address[:\s]+([\d\w\s,]+)"
        address_match = re.search(address_regex, text, re.IGNORECASE)
        if address_match:
            address_parts = address_match.group(1).strip()
            # Chercher aussi la ville et le code postal qui peuvent être sur une autre ligne
            location_regex = r"(East\s+Joseph,\s+TX\s+\d+)"
            location_match = re.search(location_regex, text)
            if location_match:
                address_parts += ", " + location_match.group(1)
            invoice_data["address"] = address_parts
        
        # Extraire les éléments de la facture
        # Rechercher des lignes avec format "description x price Euro"
        item_regex = r"([A-Za-z\s.]+)\s+(\d+)\s+x\s+(\d+\.\d+)\s+Euro"
        item_matches = re.finditer(item_regex, text)
        
        for match in item_matches:
            description = match.group(1).strip()
            quantity = int(match.group(2))
            unit_price = float(match.group(3))
            amount = quantity * unit_price
            
            invoice_data["items"].append({
                "description": description,
                "quantity": quantity,
                "unitPrice": unit_price,
                "amount": amount
            })
        
        # Extraire le montant total
        total_regex = r"TOTAL\s+(\d+\.\d+)\s+Euro"
        total_match = re.search(total_regex, text, re.IGNORECASE)
        if total_match:
            invoice_data["totalAmount"] = float(total_match.group(1))
            invoice_data["currency"] = "Euro"
        
        return invoice_data

# ------ Service OCR ------
class OcrService:
    def __init__(self):
        self.invoice_extractor = InvoiceExtractor()
    
    def process_image(self, image_path):
        """
        Traite une image avec OCR et extrait les données de facture
        """
        try:
            # Effectuer l'OCR avec Tesseract
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            # Extraire les données structurées
            invoice_data = self.invoice_extractor.extract_invoice_data(text)
            
            # Ajouter le texte brut pour référence
            invoice_data["rawText"] = text
            
            # Calculer les métriques de qualité
            quality_metrics = self.calculate_quality_metrics(invoice_data)
            invoice_data["qualityMetrics"] = quality_metrics
            
            return invoice_data
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise e
    
    def calculate_quality_metrics(self, invoice_data):
        """
        Calcule des métriques de qualité de l'extraction
        """
        # Vérifier les champs obligatoires
        required_fields = ["invoiceNumber", "date", "recipient", "totalAmount"]
        fields_present = sum(1 for field in required_fields if invoice_data.get(field) is not None)
        
        # Calculer le score de complétude
        completeness = fields_present / len(required_fields)
        
        # Vérifier la cohérence des montants
        consistency = 1.0
        if invoice_data.get("items") and invoice_data.get("totalAmount"):
            calculated_total = sum(item.get("amount", 0) for item in invoice_data["items"])
            difference = abs(calculated_total - invoice_data["totalAmount"])
            
            # Si la différence est supérieure à 1€, réduire le score de cohérence
            if difference > 1:
                consistency = max(0, 1 - (difference / invoice_data["totalAmount"]))
        
        # Score global
        overall_score = (completeness * 0.7) + (consistency * 0.3)
        
        return {
            "completeness": completeness,
            "consistency": consistency,
            "overallScore": overall_score
        }

# ------ Service Azure Blob Storage ------
class AzureBlobService:
    def __init__(self, sas_url):
        self.sas_url = sas_url
    
    def list_blobs(self):
        """
        Liste les blobs disponibles dans le conteneur
        """
        try:
            # Faire une requête HTTP vers l'URL SAS
            response = requests.get(self.sas_url)
            if response.status_code != 200:
                raise Exception(f"Failed to list blobs: {response.status_code}")
            
            # Analyser la réponse XML
            root = ET.fromstring(response.content)
            namespace = {'blob': 'http://schemas.microsoft.com/windowsazure/2009/06/storage/blob'}
            
            blobs = []
            for blob in root.findall('.//blob:Blob', namespace):
                name = blob.find('blob:Name', namespace).text
                url = f"https://projetocrstorageacc.blob.core.windows.net/invoices-2018/{name}?sv=2019-12-12&ss=b&srt=sco&sp=rl&se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D"
                blobs.append({"name": name, "url": url})
            
            return blobs
        except Exception as e:
            logger.error(f"Error listing blobs: {str(e)}")
            raise e
    
    def download_blob(self, blob_url, local_path):
        """
        Télécharge un blob vers un chemin local
        """
        try:
            response = requests.get(blob_url)
            if response.status_code != 200:
                raise Exception(f"Failed to download blob: {response.status_code}")
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return local_path
        except Exception as e:
            logger.error(f"Error downloading blob: {str(e)}")
            raise e

# ------ Classe principale pour le traitement des factures ------
class InvoiceProcessor:
    def __init__(self, mongo):
        self.ocr_service = OcrService()
        self.azure_service = AzureBlobService(AZURE_SAS_URL)
        self.invoice_model = InvoiceModel(mongo)
    
    def process_all_invoices(self):
        """
        Traite toutes les factures disponibles dans le conteneur Azure
        """
        try:
            # Lister les blobs disponibles
            blobs = self.azure_service.list_blobs()
            
            results = []
            for blob in blobs:
                try:
                    # Créer un dossier temporaire pour les téléchargements
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Construire le chemin local pour le fichier
                        local_path = os.path.join(temp_dir, blob["name"])
                        
                        # Télécharger le blob
                        self.azure_service.download_blob(blob["url"], local_path)
                        
                        # Traiter l'image avec OCR
                        invoice_data = self.ocr_service.process_image(local_path)
                        
                        # Sauvegarder les résultats dans MongoDB
                        invoice_data["sourceBlob"] = blob["name"]
                        invoice_data["sourceUrl"] = blob["url"]
                        
                        result = self.invoice_model.save_invoice(invoice_data)
                        
                        results.append({
                            "blobName": blob["name"],
                            "invoiceId": str(result.inserted_id),
                            "invoiceNumber": invoice_data.get("invoiceNumber"),
                            "success": True
                        })
                except Exception as e:
                    logger.error(f"Error processing blob {blob['name']}: {str(e)}")
                    results.append({
                        "blobName": blob["name"],
                        "success": False,
                        "error": str(e)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error in process_all_invoices: {str(e)}")
            raise e
    
    def get_invoice_results(self, invoice_id=None):
        """
        Récupère les résultats de traitement des factures
        """
        if invoice_id:
            return self.invoice_model.get_invoice(invoice_id)
        else:
            return self.invoice_model.get_all_invoices()

# ------ Routes Flask ------
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de santé du service
    """
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/process', methods=['POST'])
def process_invoices():
    try:
        processor = InvoiceProcessor(mongo)
        results = processor.process_all_invoices()
        return jsonify({"status": "success", "processed": len(results), "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        processor = InvoiceProcessor(mongo)
        invoices = processor.get_invoice_results()
        
        # Convertir les ObjectId en strings pour le JSON
        serializable_invoices = []
        for invoice in invoices:
            invoice['_id'] = str(invoice['_id'])
            serializable_invoices.append(invoice)
        
        return jsonify({"status": "success", "count": len(serializable_invoices), "invoices": serializable_invoices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    try:
        processor = InvoiceProcessor(mongo)
        invoice = processor.get_invoice_results(invoice_id)
        if not invoice:
            return jsonify({"status": "error", "message": "Invoice not found"}), 404
        
        # Convertir l'ObjectId en string pour le JSON
        invoice['_id'] = str(invoice['_id'])
        
        return jsonify({"status": "success", "invoice": invoice})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------ Point d'entrée principal ------
if __name__ == '__main__':
    # Afficher l'URL du serveur pour faciliter la connexion
    port = int(os.getenv('PORT', 5000))
    print(f"Starting server on http://localhost:{port}")
    print(f"API will be available at http://localhost:{port}/api")
    
    app.run(debug=True, host='0.0.0.0', port=port)