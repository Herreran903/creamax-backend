# app/api/v1/custom/create.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import logging

from app.schemas.custom import CustomCreateRequest, CustomCreateResponse, CotizacionRango, Desglose
from app.db.session import get_db
from app.crud.item_personalizado import create_item_personalizado
from app.crud.cotizacion import create_cotizacion
from app.crud.nfc import create_nfc_enlace
from app.services.cotizacion_service import estimate_price_from_params
from app.models.modelo_catalogo import ModeloCatalogo
from app.utils.slicing import download_3mf, run_prusaslicer_and_parse_metrics

logger = logging.getLogger(__name__)

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
                #modelo = db.query(ModeloCatalogo).filter(ModeloCatalogo.id == mid).first()
                #if modelo:
                modelo_precio_base = payload.modelo.precio_base
                modelo_catalogo_id = payload.modelo.modelo_id
            except ValueError:
                # no es entero: salto (puede ser identificador externo)
                pass
    except Exception:
        # no fallar: continuar
        pass

    # 3) si modelo.url existe, intenta descargar, slice y extraer métricas
    slicer_metrics = {}
    tmp_files = []
    
    try:
        '''
        file_url = None
        # new parameter: model_url inside payload.modelo
        if payload.modelo and getattr(payload.modelo, "model_url", None):
            file_url = str(payload.modelo.model_url)

        if file_url:
            try:
                model_3mf_path = download_3mf(file_url)
                tmp_files.append(model_3mf_path)

                # run prusaslicer and parse metrics (may raise HTTPException on errors)
                slicer_metrics = run_prusaslicer_and_parse_metrics(model_3mf_path)
                # attach profile name if present
                slicer_metrics.setdefault("slicer_profile", slicer_metrics.get("slicer_profile") or None)
            except HTTPException:
                # re-raise HTTPExceptions (they are already formatted for response)
                raise
            except Exception as e:
                logger.exception("Error during slicing flow: %s", e)
                raise HTTPException(status_code=500, detail=f"Slicer/processing error: {e}")
        '''
        # 4) merge parametros and slicer metrics for pricing function
        merged_params = payload.parametros.dict()
        # include safe subset under 'slicer_metrics' to avoid polluting service contract
        if slicer_metrics:
            merged_params["slicer_metrics"] = slicer_metrics
        
        # 5) generar estimación
        cot_min, cot_max, desglose_dict = estimate_price_from_params(merged_params)
    finally:
        # ensure temp cleanup
        for p in tmp_files:
            try:
                import os
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                logger.warning("Failed to remove temp file %s", p)
        # remove gcode produced by slicer if present
        try:
            gpath = slicer_metrics.get("raw_gcode_path") if isinstance(slicer_metrics, dict) else None
            if gpath:
                import os
                if os.path.exists(gpath):
                    os.remove(gpath)
        except Exception:
            logger.warning("Failed to remove gcode file %s", gpath)

    # 6) persistir ItemPersonalizado (cotización se representa como item personalizado)
    parametros_json = payload.parametros.dict()
    item = create_item_personalizado(
        db=db,
        cliente_id=None,  
        modelo_catalogo_id=None,
        nombre_personalizado=payload.nombre_personalizado,
        parametros=payload.parametros.dict(),
        color=payload.parametros.color,
        logo_url=None,
        model_url=(str(payload.modelo.model_url) if payload.modelo and getattr(payload.modelo, "model_url", None) else None)
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

    # 7) Crear registro NFC si include_nfc es True
    if payload.parametros.include_nfc and payload.parametros.nfc_url:
        create_nfc_enlace(
            db=db,
            item_personalizado_id=item.id,
            url_destino=payload.parametros.nfc_url
        )

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
