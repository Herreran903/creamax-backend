# app/crud/item.py
from http.client import HTTPException
from sqlalchemy.orm import Session
from app.models.item_personalizado import ItemPersonalizado
from datetime import datetime
from app.utils.generate_item_id import generate_item_id


def create_item_personalizado(db: Session, cliente_id: int | None, modelo_catalogo_id: int | None, nombre_personalizado: str, parametros: dict, color: str | None = None, logo_url: str | None = None, model_url: str | None = None):
    item_id = generate_item_id()
    
    item = ItemPersonalizado(
        id=item_id,
        cliente_id=cliente_id,
        modelo_catalogo_id=modelo_catalogo_id,
        nombre_personalizado=nombre_personalizado,
        color=color,
        logo_url=logo_url,
        model_url=model_url,
        parametros=parametros,
        fecha_creacion=datetime.utcnow()
    )
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
