from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.v1.custom.create import router as custom_create_router

app = FastAPI(title="Creamax API MVP")
app.include_router(custom_create_router, tags=["custom-create"])

# Crear tablas (solo durante desarrollo)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Creamax API backend online"}
