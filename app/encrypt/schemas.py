from pydantic import BaseModel

class StorePrivateKeyRequest(BaseModel):
    private_key: str
    unique_keyword: str