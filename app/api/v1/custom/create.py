# app/api/v1/custom/create.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.schemas.custom import CustomCreateRequest, CustomCreateResponse, CotizacionRango, Desglose
from app.db.session import get_db
from app.crud.item_personalizado import create_item_personalizado
from app.crud.cotizacion import create_cotizacion
from app.services.cotizacion_service import estimate_price_from_params
from app.models.modelo_catalogo import ModeloCatalogo

router = APIRouter()

@router.post("/create", response_model=CustomCreateResponse, status_code=status.HTTP_201_CREATED)
def create_custom_quote(payload: CustomCreateRequest, db: Session = Depends(get_db)):
    # 1) Definir validez de la cotización
    now = datetime.utcnow()
    expires = now + timedelta(days=1000)

    # 2) buscar precio base del modelo en catálogo si provisto y si modelo_id es int/str que mapea
    modelo_precio_base = None
    modelo_catalogo_id = None
    try:
        # si viene modelo.modelo_id que represente el id numérico en catálogo
        if payload.modelo and payload.modelo.modelo_id:
            # intento convertir a int y buscar
            try:
                mid = int(payload.modelo.modelo_id)
                modelo = db.query(ModeloCatalogo).filter(ModeloCatalogo.id == mid).first()
                if modelo:
                    modelo_precio_base = float(modelo.precio_base or 0)
                    modelo_catalogo_id = modelo.id
            except ValueError:
                # no es entero: salto (puede ser identificador externo)
                pass
    except Exception:
        # no fallar: continuar
        pass

    # 3) generar estimación
    cot_min, cot_max, desglose_dict = estimate_price_from_params(payload.parametros.dict(), modelo_precio_base)

    # 4) persistir ItemPersonalizado (cotización se representa como item personalizado)
    parametros_json = payload.parametros.dict()
    item = create_item_personalizado(
        db=db,
        cliente_id=None,  
        modelo_catalogo_id=modelo_catalogo_id,
        nombre_personalizado=payload.nombre_personalizado,
        parametros=payload.parametros.dict(),
        color=payload.parametros.color,
        logo_url=None
    )

    cotizacion_data = {
        "item_personalizado_id": item.id,
        "nombre_personalizado": payload.nombre_personalizado,
        "fecha_creacion": now,
        "moneda": "COP",
        "cotizacion_min": cot_min,
        "cotizacion_max": cot_max,
        "desglose": desglose_dict,
        "tiempo_entrega_dias": 5,
        "valida_hasta": expires,
        "notas": "Valores estimados sujetos a revisión técnica."
    }

    cotizacion_db = create_cotizacion(db=db, cotizacion=cotizacion_data)

    return {
        "id": cotizacion_db.id,
        "nombre_personalizado": item.nombre_personalizado,
        "fecha_creacion": cotizacion_db.fecha_creacion,
        "moneda": cotizacion_db.moneda,
        "cotizacion_rango": {"cotizacion_min": cot_min, "cotizacion_max": cot_max},
        "desglose": desglose_dict,
        "tiempo_entrega_dias": cotizacion_db.tiempo_entrega_dias,
        "valida_hasta": cotizacion_db.valida_hasta,
        "notas": cotizacion_db.notas
    }
