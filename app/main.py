from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base

# Routers
from app.api.v1.custom.create import router as custom_create_router
from app.api.v1.custom.confirmation import router as custom_confirmation_router
from app.api.v1.cotizaciones import router as cotizaciones_router
from app.api.v1.nfc.config import router as nfc_config_router

app = FastAPI(title="Creamax API MVP")

# Registrar routers con prefix y tags correctos
app.include_router(custom_create_router, prefix="/api/v1/custom", tags=["custom"])
app.include_router(custom_confirmation_router, prefix="/api/v1/custom", tags=["custom"])
app.include_router(cotizaciones_router, prefix="/api/v1/cotizaciones", tags=["cotizaciones"])
app.include_router(nfc_config_router, prefix="/api/v1/nfc",tags=["NFC"])

# Health check
@app.get("/")
def root():
    return {"message": "Creamax API backend online"}
