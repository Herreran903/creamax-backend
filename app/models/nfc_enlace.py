from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class NfcEnlace(Base):
    __tablename__ = "nfc_enlace"

    id = Column(Integer, primary_key=True, index=True)
    item_personalizado_id = Column(Integer, ForeignKey("item_personalizado.id", ondelete="CASCADE"))
    short_code = Column(String, unique=True, nullable=False)
    url_destino_actual = Column(String, nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    item_personalizado = relationship("ItemPersonalizado", backref="nfc_enlaces")
