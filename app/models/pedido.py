from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id", ondelete="SET NULL"))
    item_personalizado_id = Column(Integer, ForeignKey("item_personalizado.id", ondelete="CASCADE"))

    cantidad = Column(Integer, nullable=False)
    cotizacion_min = Column(Numeric(10, 2), nullable=True)
    cotizacion_max = Column(Numeric(10, 2), nullable=True)
    precio_final = Column(Numeric(10, 2), nullable=True)
    precio_total = Column(Numeric(12, 2), nullable=True)
    moneda = Column(String(10), nullable=True)

    estado = Column(String, nullable=False, default="Precotización")
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    mensaje = Column(Text, nullable=True)

    cliente = relationship("Cliente", backref="pedidos")
    item_personalizado = relationship("ItemPersonalizado", backref="pedidos")
