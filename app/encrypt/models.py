from sqlalchemy import Column, Integer, String
from app.core.database import Base  # Assuming you have a Base model class

class EncryptedKey(Base):
    __tablename__ = 'encrypted_keys'
    id = Column(Integer, primary_key=True, index=True)
    aes_encrypted_private_key = Column(String, nullable=False)
    unique_keyword_hash = Column(String, nullable=False)
    aes_key = Column(String, nullable=False)