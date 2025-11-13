import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="3D Printing Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
from schemas import Printer, ContactMessage, SocialLink

# Helpers

def oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

# Public endpoints

@app.get("/")
def root():
    return {"service": "3D Printing", "status": "ok"}

@app.get("/api/products", response_model=List[Printer])
def list_products():
    items = get_documents("printer", {"available": True})
    for it in items:
        it["id"] = str(it.get("_id"))
        it.pop("_id", None)
    return items

class ContactIn(ContactMessage):
    pass

@app.post("/api/contact")
def submit_contact(payload: ContactIn):
    doc_id = create_document("contactmessage", payload)
    return {"ok": True, "id": doc_id}

@app.get("/api/socials", response_model=List[SocialLink])
def get_socials():
    items = get_documents("sociallink", {"visible": True})
    for it in items:
        it["id"] = str(it.get("_id"))
        it.pop("_id", None)
    return items

# Admin models
class LoginRequest(BaseModel):
    username: str
    password: str

# Extremely simple admin session using env vars (for demo)
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
SESSION_TOKEN = os.getenv("ADMIN_TOKEN", "changeme-token")

def check_auth(token: Optional[str]):
    if token != SESSION_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/api/admin/login")
def admin_login(body: LoginRequest):
    if body.username == ADMIN_USER and body.password == ADMIN_PASS:
        return {"token": SESSION_TOKEN}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Admin CRUD

@app.get("/api/admin/products", response_model=List[Printer])
def admin_list_products(token: str):
    check_auth(token)
    items = get_documents("printer")
    for it in items:
        it["id"] = str(it.get("_id"))
        it.pop("_id", None)
    return items

@app.post("/api/admin/products")
def admin_create_product(payload: Printer, token: str):
    check_auth(token)
    new_id = create_document("printer", payload)
    return {"id": new_id}

@app.get("/api/admin/contacts")
def admin_list_contacts(token: str):
    check_auth(token)
    items = get_documents("contactmessage")
    for it in items:
        it["id"] = str(it.get("_id"))
        it.pop("_id", None)
    return items

@app.post("/api/admin/socials")
def admin_add_social(link: SocialLink, token: str):
    check_auth(token)
    new_id = create_document("sociallink", link)
    return {"id": new_id}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
            response["database"] = "✅ Connected & Working"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
