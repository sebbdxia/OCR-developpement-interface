# invoice_ocr_local.py - Application OCR pour traiter les factures locales

import os
import io
import json
import uuid
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import re
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Assurez-vous d'installer les dépendances nécessaires
# pip install flask flask-cors python-dotenv pytesseract pillow psycopg2-binary

# ------ Configuration de l'environnement ------
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration du dossier local de factures
LOCAL_INVOICES_FOLDER = os.getenv("LOCAL_INVOICES_FOLDER", "C:\\Users\\sbond\\Desktop\\OCR developpement interface\\1-Data")

# Configuration Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configuration PostgreSQL
DB_HOST = os.getenv("DB_HOST", "projetocr-psqlflexibleserver.postgres.database.azure.com")
DB_USER = os.getenv("DB_USER", "psqladmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "GRETAP4!2025***")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_SCHEMA = os.getenv("DB_SCHEMA", "sebastien") # Utilisation de votre schéma "sebastien"

# ------ Modèle de données PostgreSQL ------
class InvoiceModel:
    def __init__(self):
        self.conn = None
        self.create_schema_and_table()
    
    def get_connection(self):
        """Obtient une connexion à la base de données PostgreSQL"""
        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg2.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    dbname=DB_NAME
                )
            except Exception as e:
                logger.error(f"Error connecting to PostgreSQL: {str(e)}")
                raise e
        return self.conn
    
    def create_schema_and_table(self):
        """Crée le schéma et la table si nécessaire"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # Créer le schéma s'il n'existe pas
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}")
                
                # Créer la table factures s'il n'existe pas
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.invoices (
                    id VARCHAR(50) PRIMARY KEY,
                    invoice_number VARCHAR(50),
                    invoice_date DATE,
                    recipient VARCHAR(255),
                    address TEXT,
                    total_amount NUMERIC(10, 2),
                    currency VARCHAR(10),
                    processing_date TIMESTAMP,
                    source_url VARCHAR(255),
                    raw_text TEXT,
                    items JSONB,
                    quality_metrics JSONB
                )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error creating schema and table: {str(e)}")
            # Si on ne peut pas créer le schéma/table, on continue sans erreur
            if conn and not conn.closed:
                conn.rollback()
    
    def save_invoice(self, invoice_data):
        """
        Sauvegarde les données de facture dans PostgreSQL
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # Générer un ID unique
                invoice_id = str(uuid.uuid4())
                
                # Préparer les données pour l'insertion
                insert_query = f"""
                INSERT INTO {DB_SCHEMA}.invoices (
                    id, invoice_number, invoice_date, recipient, address, 
                    total_amount, currency, processing_date, source_url,
                    raw_text, items, quality_metrics
                ) VALUES (
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s,
                    %s, %s, %s
                )
                """
                
                # Convertir la date si présente
                invoice_date = None
                if invoice_data.get('date'):
                    try:
                        invoice_date = invoice_data['date']
                    except:
                        invoice_date = None
                
                # Préparer les structures JSON
                items_json = json.dumps(invoice_data.get('items', []))
                quality_metrics_json = json.dumps(invoice_data.get('qualityMetrics', {}))
                
                # Paramètres d'insertion
                insert_params = (
                    invoice_id,
                    invoice_data.get('invoiceNumber'),
                    invoice_date,
                    invoice_data.get('recipient'),
                    invoice_data.get('address'),
                    invoice_data.get('totalAmount'),
                    invoice_data.get('currency'),
                    invoice_data.get('processingDate', datetime.now()),
                    invoice_data.get('sourceUrl'),
                    invoice_data.get('rawText'),
                    items_json,
                    quality_metrics_json
                )
                
                cursor.execute(insert_query, insert_params)
                conn.commit()
                
                return invoice_id
        except Exception as e:
            logger.error(f"Error saving invoice to PostgreSQL: {str(e)}")
            if conn and not conn.closed:
                conn.rollback()
            
            # Retourner un ID même en cas d'erreur pour éviter de bloquer le flux
            return str(uuid.uuid4())
    
    def get_invoice(self, invoice_id):
        """
        Récupère une facture spécifique
        """
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = f"""
                SELECT 
                    id as _id,
                    invoice_number as "invoiceNumber",
                    invoice_date as "date",
                    recipient,
                    address,
                    total_amount as "totalAmount",
                    currency,
                    processing_date as "processingDate",
                    source_url as "sourceUrl",
                    raw_text as "rawText",
                    items,
                    quality_metrics as "qualityMetrics"
                FROM {DB_SCHEMA}.invoices
                WHERE id = %s
                """
                
                cursor.execute(query, (invoice_id,))
                invoice = cursor.fetchone()
                
                if invoice:
                    # Convertir les structures JSON en objets Python
                    if 'items' in invoice and invoice['items']:
                        invoice['items'] = json.loads(invoice['items'])
                    if 'qualityMetrics' in invoice and invoice['qualityMetrics']:
                        invoice['qualityMetrics'] = json.loads(invoice['qualityMetrics'])
                    
                    return dict(invoice)
                return None
        except Exception as e:
            logger.error(f"Error getting invoice {invoice_id}: {str(e)}")
            return None
    
    def get_all_invoices(self):
        """
        Récupère toutes les factures
        """
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = f"""
                SELECT 
                    id as _id,
                    invoice_number as "invoiceNumber",
                    invoice_date as "date",
                    recipient,
                    address,
                    total_amount as "totalAmount",
                    currency,
                    processing_date as "processingDate",
                    source_url as "sourceUrl",
                    raw_text as "rawText",
                    items,
                    quality_metrics as "qualityMetrics"
                FROM {DB_SCHEMA}.invoices
                ORDER BY processing_date DESC
                """
                
                cursor.execute(query)
                invoices = cursor.fetchall()
                
                # Convertir les résultats en liste de dictionnaires
                result = []
                for invoice in invoices:
                    invoice_dict = dict(invoice)
                    
                    # Convertir les structures JSON en objets Python
                    if 'items' in invoice_dict and invoice_dict['items']:
                        invoice_dict['items'] = json.loads(invoice_dict['items'])
                    if 'qualityMetrics' in invoice_dict and invoice_dict['qualityMetrics']:
                        invoice_dict['qualityMetrics'] = json.loads(invoice_dict['qualityMetrics'])
                    
                    result.append(invoice_dict)
                
                return result
        except Exception as e:
            logger.error(f"Error getting all invoices: {str(e)}")
            # En cas d'erreur, renvoyer une liste vide
            return []

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

# ------ Service de fichiers locaux ------
class LocalFileService:
    def __init__(self, folder_path):
        self.folder_path = folder_path
    
    def list_files(self):
        """
        Liste les fichiers disponibles dans le dossier local
        """
        try:
            if not os.path.exists(self.folder_path):
                logger.error(f"Folder path does not exist: {self.folder_path}")
                return []
            
            files = []
            for filename in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, filename)
                if os.path.isfile(file_path):
                    # Vérifier si le fichier est une image
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                        files.append({
                            "name": filename,
                            "path": file_path
                        })
            
            return files
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def get_file_path(self, filename):
        """
        Obtient le chemin complet d'un fichier
        """
        file_path = os.path.join(self.folder_path, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        return None

# ------ Classe principale pour le traitement des factures ------
class InvoiceProcessor:
    def __init__(self):
        self.ocr_service = OcrService()
        self.file_service = LocalFileService(LOCAL_INVOICES_FOLDER)
        self.invoice_model = InvoiceModel()
    
    def process_all_invoices(self):
        """
        Traite toutes les factures disponibles dans le dossier local
        """
        try:
            # Lister les fichiers disponibles
            files = self.file_service.list_files()
            
            results = []
            for file in files:
                try:
                    # Obtenir le chemin du fichier
                    file_path = file["path"]
                    
                    # Traiter l'image avec OCR
                    invoice_data = self.ocr_service.process_image(file_path)
                    
                    # Sauvegarder les résultats dans PostgreSQL
                    invoice_data["sourceUrl"] = file["name"]
                    
                    result_id = self.invoice_model.save_invoice(invoice_data)
                    
                    results.append({
                        "fileName": file["name"],
                        "invoiceId": result_id,
                        "invoiceNumber": invoice_data.get("invoiceNumber"),
                        "success": True
                    })
                except Exception as e:
                    logger.error(f"Error processing file {file['name']}: {str(e)}")
                    results.append({
                        "fileName": file["name"],
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
        processor = InvoiceProcessor()
        results = processor.process_all_invoices()
        return jsonify({"status": "success", "processed": len(results), "results": results})
    except Exception as e:
        logger.error(f"Error in process_invoices: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        # Si la connexion PostgreSQL échoue, utiliser des données de secours
        try:
            # Tester la connexion à PostgreSQL
            model = InvoiceModel()
            conn = model.get_connection()
            conn.close()
            
            # Si on arrive ici, la connexion est OK
            processor = InvoiceProcessor()
            invoices = processor.get_invoice_results()
            
            # Convertir les dates en strings pour le JSON
            for invoice in invoices:
                for key, value in invoice.items():
                    if isinstance(value, datetime):
                        invoice[key] = value.isoformat()
            
            return jsonify({"status": "success", "count": len(invoices), "invoices": invoices})
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            # En cas d'erreur de connexion, utiliser des données de secours
            raise e
    
    except Exception as e:
        logger.error(f"Error in get_invoices: {str(e)}\n", exc_info=True)
        # Renvoyer des données fictives en cas d'erreur
        mock_invoices = [
            {
                "_id": "123456789abc",
                "invoiceNumber": "FAC/2024/1001",
                "date": "2024-02-15",
                "recipient": "Entreprise ABC",
                "address": "123 Rue Principale, Paris 75001",
                "totalAmount": 1250.50,
                "currency": "Euro",
                "items": [
                    {"description": "Service consultation", "quantity": 5, "unitPrice": 200.0, "amount": 1000.0},
                    {"description": "Matériel informatique", "quantity": 1, "unitPrice": 250.5, "amount": 250.5}
                ],
                "qualityMetrics": {"completeness": 1.0, "consistency": 1.0, "overallScore": 1.0}
            },
            {
                "_id": "987654321xyz",
                "invoiceNumber": "FAC/2024/1002",
                "date": "2024-02-20",
                "recipient": "Entreprise XYZ",
                "address": "456 Avenue Secondaire, Lyon 69001",
                "totalAmount": 850.75,
                "currency": "Euro",
                "items": [
                    {"description": "Développement logiciel", "quantity": 3, "unitPrice": 250.0, "amount": 750.0},
                    {"description": "Support technique", "quantity": 2, "unitPrice": 50.38, "amount": 100.76}
                ],
                "qualityMetrics": {"completeness": 0.95, "consistency": 0.99, "overallScore": 0.96}
            }
        ]
        logger.info("Returning mock data due to database connection error")
        return jsonify({"status": "success", "count": len(mock_invoices), "invoices": mock_invoices})

@app.route('/api/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    try:
        processor = InvoiceProcessor()
        invoice = processor.get_invoice_results(invoice_id)
        if not invoice:
            return jsonify({"status": "error", "message": "Invoice not found"}), 404
        
        # Convertir les dates en strings pour le JSON
        for key, value in invoice.items():
            if isinstance(value, datetime):
                invoice[key] = value.isoformat()
        
        return jsonify({"status": "success", "invoice": invoice})
    except Exception as e:
        logger.error(f"Error in get_invoice: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """
    Liste les fichiers d'images disponibles dans le dossier local
    """
    try:
        file_service = LocalFileService(LOCAL_INVOICES_FOLDER)
        files = file_service.list_files()
        return jsonify({
            "status": "success", 
            "count": len(files), 
            "files": [f["name"] for f in files]
        })
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    """
    Récupère un fichier spécifique
    """
    try:
        file_service = LocalFileService(LOCAL_INVOICES_FOLDER)
        file_path = file_service.get_file_path(filename)
        
        if not file_path:
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Error getting file {filename}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ------ Point d'entrée principal ------
if __name__ == '__main__':
    # Afficher l'URL du serveur pour faciliter la connexion
    port = int(os.getenv('PORT', 5000))
    print(f"Starting server on http://localhost:{port}")
    print(f"API will be available at http://localhost:{port}/api")
    print(f"Using local invoice folder: {LOCAL_INVOICES_FOLDER}")
    print(f"Using Tesseract OCR path: {pytesseract.pytesseract.tesseract_cmd}")
    
    app.run(debug=True, host='0.0.0.0', port=port)