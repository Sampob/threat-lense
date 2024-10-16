from app import db
from cryptography.fernet import Fernet
from app.config import Config

# Encrypt/Decrypt helper
def encrypt_data(data):
    cipher_suite = Fernet(Config.SECRET_KEY.encode("utf-8"))
    return cipher_suite.encrypt(data.encode("utf-8")).decode("utf-8")

def decrypt_data(data):
    cipher_suite = Fernet(Config.SECRET_KEY.encode("utf-8"))
    return cipher_suite.decrypt(data.encode("utf-8")).decode("utf-8")

class Source(db.Model):
    """ Represents different external sources. """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    requires_api_key = db.Column(db.Boolean, default=False)

class APIKey(db.Model):
    """ Stores encrypted API keys for sources that need them. """
    id = db.Column(db.Integer, primary_key=True)
    encrypted_key = db.Column(db.String(500), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey("source.id"), nullable=False)
    source = db.relationship("Source", backref="api_key", lazy=True)

    def set_key(self, raw_key):
        self.encrypted_key = encrypt_data(raw_key)

    def get_key(self):
        return decrypt_data(self.encrypted_key)
