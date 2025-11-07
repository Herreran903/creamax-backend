from sqlalchemy.orm import Session
from app.models.cotizacion import Cotizacion
from http.client import HTTPException

def create_cotizacion(db: Session, cotizacion: dict):
    """Crea y persiste una nueva cotización en la DB."""
    db_cotizacion = Cotizacion(**cotizacion)
    try:
        db.add(db_cotizacion)
        db.commit()
        db.refresh(db_cotizacion)
        return db_cotizacion
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))