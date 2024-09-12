from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
from app.core.database import get_session
from . import schemas, services, helpers, models


router = APIRouter()


@router.post("/store-key/")
def store_private_key(request: schemas.StorePrivateKeyRequest, db: Session = Depends(get_session)):
    """
    Store a private key encrypted with AES in the database.
    Returns the AES key required for decryption.
    """
    # Generate AES key
    aes_key = helpers.generate_aes_key()

    # Encrypt the private key using AES
    encrypted_private_key = helpers.encrypt_private_key_aes(aes_key, request.private_key)

    # Hash the unique keyword for security
    unique_keyword_hash = helpers.hash_unique_keyword(request.unique_keyword)

    # Store in the database
    encrypted_key_entry = models.EncryptedKey(
        aes_encrypted_private_key=encrypted_private_key,
        unique_keyword_hash=unique_keyword_hash,
        aes_key=base64.b64encode(aes_key).decode()  # Store AES key base64 encoded for later use
    )
    db.add(encrypted_key_entry)
    db.commit()

    return {
        "message": "Private key stored successfully",
        "aes_key": base64.b64encode(aes_key).decode()  # Return the AES key for decryption
    }

@router.post("/retrieve-key/")
def retrieve_private_key(keyword: str, aes_key_header: str = Header(...), db: Session = Depends(get_session)):
    """
    Retrieve the encrypted private key using the AES key and unique keyword.
    """
    # Hash the keyword to compare
    keyword_hash = helpers.hash_unique_keyword(keyword)

    # Find the encrypted private key in the database
    encrypted_key_entry = db.query(models.EncryptedKey).filter_by(unique_keyword_hash=keyword_hash).first()

    if not encrypted_key_entry:
        raise HTTPException(status_code=404, detail="No matching encrypted key found.")

    # Verify the AES key
    aes_key = base64.b64decode(aes_key_header)
    stored_aes_key = base64.b64decode(encrypted_key_entry.aes_key)

    if aes_key != stored_aes_key:
        raise HTTPException(status_code=403, detail="Invalid AES key provided.")

    # Decrypt the private key
    decrypted_private_key = helpers.decrypt_private_key_aes(aes_key, encrypted_key_entry.aes_encrypted_private_key)

    return {"decrypted_private_key": decrypted_private_key}