from sqlalchemy import Column, Integer, ForeignKey, Date, UniqueConstraint
from app.db.base import Base

class NfcVisita(Base):
    __tablename__ = "nfc_visita"

    id = Column(Integer, primary_key=True, index=True)
    nfc_enlace_id = Column(Integer, ForeignKey("nfc_enlace.id", ondelete="CASCADE"))
    fecha_conteo = Column(Date, nullable=False)
    conteo = Column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("nfc_enlace_id", "fecha_conteo", name="uq_nfc_enlace_fecha"),)
