from sqlalchemy import Column, Integer, String, Float, Text, JSON
from app.db.base import Base

class ModeloCatalogo(Base):
    __tablename__ = "modelo_catalogo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio_base = Column(Float, nullable=False)
    archivo_id = Column(String, nullable=True)
    url = Column(String, nullable=True)
    svg = Column(Text, nullable=True)
    textura_imagen_id = Column(String, nullable=True)
    parametros_generacion_ai = Column(JSON, nullable=True)
    thumbnail_url = Column(String, nullable=True)