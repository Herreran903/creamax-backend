from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Cotizacion(Base):
    __tablename__ = "cotizacion"

    # Campos principales de identificación y relación
    id = Column(Integer, primary_key=True, index=True)
 
    # 🔗 Relación con el ítem personalizado que la solicitó
    item_personalizado_id = Column(Integer, ForeignKey("item_personalizado.id"), nullable=False, unique=True)
    
    nombre_personalizado = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    moneda = Column(String(5), nullable=False) # e.g., 'CLP', 'USD'

    cotizacion_min = Column(Float, nullable=False) # de cotizacion_rango
    cotizacion_max = Column(Float, nullable=False) # de cotizacion_rango
    desglose = Column(JSON, nullable=False) # Almacena el objeto {"material": X, "mano_obra": Y, ...}

    tiempo_entrega_dias = Column(Integer, nullable=False)
    valida_hasta = Column(DateTime, nullable=False)
    notas = Column(String)

    item_personalizado = relationship("ItemPersonalizado", back_populates="cotizacion")