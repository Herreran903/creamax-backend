# app/schemas/custom.py
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class AIParams(BaseModel):
    prompt: str
    semilla: Optional[int]
    variacion: Optional[str]
    motor: Optional[str]

class ModeloInfo(BaseModel):
    modelo_id: Optional[str]
    archivo_id: Optional[str] = None
    url: Optional[HttpUrl] = None
    svg: Optional[str] = None
    textura_imagen_id: Optional[str] = None
    parametros_generacion_ai: Optional[AIParams] = None
    thumbnail_url: Optional[HttpUrl] = None

class ParametrosFabricacion(BaseModel):
    material: str
    color: Optional[str] = None
    acabado: Optional[str] = None
    dimension_unidad: Optional[str] = "mm"
    alto: Optional[float] = None
    ancho: Optional[float] = None
    profundidad: Optional[float] = None
    escala: Optional[float] = 1.0
    cantidad: int = Field(..., gt=0)
    complejidad_estimacion: Optional[str] = "media"
    tolerancia: Optional[str] = "estandar"
    espesor_minimo: Optional[float] = None

class Metadatos(BaseModel):
    app_version: Optional[str] = None
    locale: Optional[str] = None
    dispositivo: Optional[str] = None
    referer: Optional[str] = None

class CustomCreateRequest(BaseModel):
    version: str = Field("1.0")
    fuente_modelo: str
    nombre_personalizado: str
    usuario_id: Optional[str] = None
    modelo: ModeloInfo
    parametros: ParametrosFabricacion
    metadatos: Optional[Metadatos] = None

class Desglose(BaseModel):
    material: float
    mano_obra: float
    energia: float
    acabado: float

class CotizacionRango(BaseModel):
    cotizacion_min: float
    cotizacion_max: float

class CustomCreateResponse(BaseModel):
    id: int
    nombre_personalizado: str
    fecha_creacion: datetime
    moneda: str = "COP"
    cotizacion_rango: CotizacionRango
    desglose: Desglose
    tiempo_entrega_dias: int
    valida_hasta: datetime
    notas: Optional[str] = None
