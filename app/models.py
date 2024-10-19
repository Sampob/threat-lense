from app.config import Config

from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

db = SQLAlchemy()

# Encrypt/Decrypt helper
def encrypt_data(data):
    """ Encrypt given data. Secret key is used to encrypt. """
    cipher_suite = Fernet(Config.SECRET_KEY.encode("utf-8"))
    return cipher_suite.encrypt(data.encode("utf-8")).decode("utf-8")

def decrypt_data(data):
    """ Decrypt given data. Encrypted data must have been encrypted using the configured secret key. """
    cipher_suite = Fernet(Config.SECRET_KEY.encode("utf-8"))
    return cipher_suite.decrypt(data.encode("utf-8")).decode("utf-8")

def fetch_api_key(name):
    api_key_entry = APIKey.query.filter_by(source_name=name).first()
    
    if api_key_entry:
        return api_key_entry.get_key()
    else:
        raise ValueError(f"No API key found for source '{name}'")

class Source(db.Model):
    """ Represents different external sources. """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    requires_api_key = db.Column(db.Boolean, default=False)
        
    @property
    def is_api_key_configured(self):
        return APIKey.query.filter_by(source_name=self.name).first() is not None

class APIKey(db.Model):
    """ Stores encrypted API keys for sources that need them. """
    id = db.Column(db.Integer, primary_key=True)
    encrypted_key = db.Column(db.String(500), nullable=False)
    source_name = db.Column(db.Integer, db.ForeignKey("source.name"), nullable=False)

    def set_key(self, raw_key):
        self.encrypted_key = encrypt_data(raw_key)

    def get_key(self):
        return decrypt_data(self.encrypted_key)
