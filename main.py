from fastapi import FastAPI
from app import database, models
from app.routers import auth_router, roles_router, documents_router, rag_router

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FastAPI Financial Document Management with Semantic Analysis")

app.include_router(auth_router.router)
app.include_router(roles_router.router)
app.include_router(documents_router.router)
app.include_router(rag_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Financial Document Management API"}
