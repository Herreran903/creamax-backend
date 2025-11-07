from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class ItemPersonalizado(Base):
    __tablename__ = "item_personalizado"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id", ondelete="SET NULL"))
    modelo_catalogo_id = Column(Integer, ForeignKey("modelo_catalogo.id", ondelete="SET NULL"))
    nombre_personalizado = Column(String, nullable=False)
    color = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    parametros = Column(JSON, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente", backref="items_personalizados")
    modelo_catalogo = relationship("ModeloCatalogo", backref="items_personalizados")
    cotizacion = relationship("Cotizacion", uselist=False, back_populates="item_personalizado")
