from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import database, models, auth
from ..rag import embeddings

router = APIRouter(prefix="/rag", tags=["rag"])

class IndexDocumentRequest(BaseModel):
    document_id: int

class SearchQuery(BaseModel):
    query: str

@router.post("/index-document")
def index_document(request: IndexDocumentRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["Admin", "Financial Analyst"]))):
    doc = db.query(models.Document).filter(models.Document.document_id == request.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        embeddings.index_document(doc.file_path, doc.document_id)
        return {"message": "Document indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/remove-document/{id}")
def remove_document(id: int, current_user: models.User = Depends(auth.require_role(["Admin", "Financial Analyst"]))):
    embeddings.remove_document(id)
    return {"message": "Document embeddings removed successfully"}

@router.post("/search")
def perfom_semantic_search(search: SearchQuery, current_user: models.User = Depends(auth.get_current_user)):
    results = embeddings.search_documents(search.query)
    if not results:
        return {"results": []}
    
    reranked = embeddings.rerank_results(search.query, results)
    
    return {
        "results": [
            {"content": r.page_content, "document_id": r.metadata.get("document_id")} 
            for r in reranked
        ]
    }

@router.get("/context/{document_id}")
def get_document_context(document_id: int, current_user: models.User = Depends(auth.get_current_user)):
    # This endpoint gets chunks of a specific document, for semantic searching we might need to filter by document_id
    results = embeddings.vector_db.get(where={"document_id": document_id})
    if not results or not results['documents']:
         raise HTTPException(status_code=404, detail="Context not found for document")
         
    return {"context": results['documents']}
