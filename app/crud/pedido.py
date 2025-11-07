# app/crud/pedido.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime

from app.models.pedido import Pedido
from app.models.cotizacion import Cotizacion


def create_pedido_from_cotizacion(db: Session, *, cotizacion: Cotizacion, cliente_id: int, cantidad: int):
    """
    Crea un Pedido basado en una cotización.
    Copia los valores de cotización (min/max/moneda) y deja los campos de precio_final y precio_total como NULL.
    """

    try:
        pedido = Pedido(
            cliente_id=cliente_id,
            cotizacion_id=cotizacion.id,
            cantidad=cantidad,
            cotizacion_min=Decimal(str(cotizacion.cotizacion_min)),
            cotizacion_max=Decimal(str(cotizacion.cotizacion_max)),
            precio_final=None,
            precio_total=None,
            estado="Precotización",
            fecha_pedido=datetime.utcnow(),
            mensaje="Pedido recibido. El precio final será confirmado manualmente por correo.",
        )

        # Si Pedido tiene campo moneda → copiar
        if hasattr(Pedido, "moneda"):
            setattr(pedido, "moneda", getattr(cotizacion, "moneda", None))

        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        return pedido

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear pedido: {str(e)}")
