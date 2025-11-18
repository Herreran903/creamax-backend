from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.crud.cotizacion import get_all_cotizaciones
from app.schemas.cotizaciones import CotizacionListado

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[CotizacionListado])
def listar_cotizaciones(db: Session = Depends(get_db)):
    pedidos = get_all_cotizaciones(db)

    if not pedidos:
        raise HTTPException(status_code=404, detail="No hay cotizaciones registradas")

    response = []
    for p in pedidos:
        cot = p.cotizacion
        item = cot.item_personalizado

        cotizacion_rango = f"{cot.cotizacion_min} - {cot.cotizacion_max}"

        precio_final_unidad = None
        if p.precio_final is not None and p.cantidad > 0:
            precio_final_unidad = float(p.precio_final)

        response.append({
            "id": p.id,
            "item_personalizado_id": item.id,
            "nombre_personalizado": item.nombre_personalizado,
            "cantidad": p.cantidad,
            "cotizacion_rango": cotizacion_rango,
            "precio_final_unidad": precio_final_unidad,
            "precio_total": float(p.precio_total) if p.precio_total else None,
            "estado": p.estado,
            "fecha_pedido": p.fecha_pedido.isoformat(),
            "moneda": cot.moneda,
        })

    return response
