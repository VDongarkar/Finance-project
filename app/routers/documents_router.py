from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
from .. import database, models, schemas, auth
from ..rag import embeddings

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_document(
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_role(["Admin", "Financial Analyst"]))
):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_document = models.Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        uploaded_by=current_user.id,
        file_path=file_path
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/")
def get_documents(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Document).all()

@router.get("/search")
def search_documents(
    company_name: str = None,
    document_type: str = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Document)
    if company_name:
        query = query.filter(models.Document.company_name == company_name)
    if document_type:
        query = query.filter(models.Document.document_type == document_type)
        
    return query.all()

@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["Admin"]))):
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
        
    embeddings.remove_document(document_id)
    
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
