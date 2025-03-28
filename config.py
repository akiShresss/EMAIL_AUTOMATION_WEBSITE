import os
import json

# Default configuration that will be overridden by environment variables in production
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    
    # Database configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'clients.db')
    
    # Email configuration
    ALLOWED_EMAILS = ["marketing@homeschool.asia", "marketing@kungfuquiz.com"]
    
    # Paths
    CREDENTIALS_PATH = os.environ.get('CREDENTIALS_PATH', 'credentials.json')
    SIGNATURE_PATHS = {
        "hsa": os.environ.get('HSA_SIGNATURE_PATH', 'signature/HSA.html'),
        "kfq": os.environ.get('KFQ_SIGNATURE_PATH', 'signature/KFQ.html')
    }
    
    @staticmethod
    def load_credentials():
        # First try to load from environment variables
        if os.environ.get('HSA_EMAIL') and os.environ.get('KFQ_EMAIL'):
            return {
                "kfq": {
                    "email": os.environ.get('KFQ_EMAIL'),
                    "password": os.environ.get('KFQ_PASSWORD'),
                    "display_name": os.environ.get('KFQ_DISPLAY_NAME', 'Kung Fu Quiz'),
                    "smtp_server": os.environ.get('KFQ_SMTP_SERVER', 'smtp.zoho.com'),
                    "smtp_port": int(os.environ.get('KFQ_SMTP_PORT', 587))
                },
                "hsa": {
                    "email": os.environ.get('HSA_EMAIL'),
                    "password": os.environ.get('HSA_PASSWORD'),
                    "display_name": os.environ.get('HSA_DISPLAY_NAME', 'HomeSchool Asia'),
                    "smtp_server": os.environ.get('HSA_SMTP_SERVER', 'smtp.zoho.com'),
                    "smtp_port": int(os.environ.get('HSA_SMTP_PORT', 587))
                }
            }
        
        # Fallback to credentials.json file
        try:
            with open(Config.CREDENTIALS_PATH, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            # Return empty credentials if file not found
            return {
                "kfq": {
                    "email": "",
                    "password": "",
                    "display_name": "Kung Fu Quiz",
                    "smtp_server": "smtp.zoho.com",
                    "smtp_port": 587
                },
                "hsa": {
                    "email": "",
                    "password": "",
                    "display_name": "HomeSchool Asia",
                    "smtp_server": "smtp.zoho.com",
                    "smtp_port": 587
                }
            }
