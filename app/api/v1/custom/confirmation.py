from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from app.schemas.confirmation import ConfirmationRequest, ConfirmationResponse
from app.db.session import get_db
from app.models.cotizacion import Cotizacion
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.crud.cliente import create_or_update_cliente
from app.crud.pedido import create_pedido_from_cotizacion

router = APIRouter()


FIXED_MESSAGE = "Pedido recibido. El precio final será confirmado manualmente por correo."

@router.post("/confirmation", response_model=ConfirmationResponse, status_code=status.HTTP_201_CREATED)
def create_custom_confirmation(payload: ConfirmationRequest, db: Session = Depends(get_db)):

    cotizacion = db.query(Cotizacion).filter(Cotizacion.id == payload.cotizacion_id).first()
    if not cotizacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"codigo": "NOT_FOUND", "mensaje": "Cotizacion no encontrada"}})


    cliente = create_or_update_cliente(
        db,
        nombre=payload.nombre,
        email=payload.email,
        telefono=payload.telefono,
        rut=payload.rut,
        direccion=payload.direccion,
        comentarios=payload.comentarios
    )

    # 3) Crear Pedido basado en la cotización
    pedido = create_pedido_from_cotizacion(
        db=db,
        cotizacion=cotizacion,
        cliente_id=cliente.id,
        cantidad=payload.cantidad if payload.cantidad else 1
    )

    print("DEBUG item_personalizado_id =", cotizacion.item_personalizado_id, type(cotizacion.item_personalizado_id))



    # 4) Respuesta final al frontend
    return ConfirmationResponse(
        pedido_id=pedido.id,
        cotizacion_id=cotizacion.id,
        item_personalizado_id=cotizacion.item_personalizado_id,
        cantidad=pedido.cantidad,
        estado=pedido.estado,
        fecha_pedido=pedido.fecha_pedido,
        mensaje="Pedido recibido. El precio final será confirmado manualmente por correo."
    )
    return