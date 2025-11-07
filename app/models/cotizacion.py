from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Cotizacion(Base):
    __tablename__ = "cotizacion"

    # Campos principales de identificación y relación
    id = Column(Integer, primary_key=True, index=True)

    item_personalizado_id = Column(Integer, ForeignKey("item_personalizado.id"), nullable=False, unique=True)

    nombre_personalizado = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    moneda = Column(String(5), nullable=False)

    cotizacion_min = Column(Float, nullable=False)
    cotizacion_max = Column(Float, nullable=False)
    desglose = Column(JSON, nullable=False)

    tiempo_entrega_dias = Column(Integer, nullable=False)
    valida_hasta = Column(DateTime, nullable=False)
    notas = Column(String)

    # Relaciones
    item_personalizado = relationship("ItemPersonalizado", back_populates="cotizacion")
    pedidos = relationship("Pedido", back_populates="cotizacion", cascade="all, delete-orphan")