from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id", ondelete="SET NULL"))
    cotizacion_id = Column(Integer, ForeignKey("cotizacion.id", ondelete="CASCADE"), nullable=False)

    cantidad = Column(Integer, nullable=False)
    cotizacion_min = Column(Numeric(10, 2), nullable=True)
    cotizacion_max = Column(Numeric(10, 2), nullable=True)
    precio_final = Column(Numeric(10, 2), nullable=True)
    precio_total = Column(Numeric(12, 2), nullable=True)

    estado = Column(String, nullable=False, default="Precotización")
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    mensaje = Column(Text, nullable=True)

    cliente = relationship("Cliente", backref="pedidos")
    cotizacion = relationship("Cotizacion", back_populates="pedidos")
