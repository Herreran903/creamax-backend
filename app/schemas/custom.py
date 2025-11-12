from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class AIParams(BaseModel):
    text_prompt: Optional[str] = None
    prompt: Optional[str] = None
    imagen_prompt: Optional[Dict[str, Any]] = None
    semilla: Optional[int] = None
    variacion: Optional[str] = None
    motor: Optional[str] = None
    
class ModeloCreate(BaseModel):
    modelo_id: Optional[str] = None 
    archivo: Optional[str] = None 
    url: Optional[HttpUrl] = None
    model_url: Optional[HttpUrl] = None
    svg: Optional[str] = None
    textura_imagen: Optional[str] = None 
    parametros_generacion_ai: Optional[AIParams] = None
    thumbnail_url: Optional[HttpUrl] = None
    precio_base: Optional[float] = None

class ParametrosCreate(BaseModel):
    color: Optional[List[str]] = None 
    alto: Optional[float] = None
    ancho: Optional[float] = None
    profundidad: Optional[float] = None
    uv_map: Optional[Dict[str, Any]] = None
    include_nfc: Optional[bool] = None
    nfc_url: Optional[str] = None

class Metadatos(BaseModel):
    app_version: Optional[str] = None
    locale: Optional[str] = None
    dispositivo: Optional[str] = None
    referer: Optional[str] = None

class CustomCreateRequest(BaseModel):
    version: str = Field("1.0", description="Versión del contrato de solicitud.")
    fuente_modelo: str = Field(..., description="Origen del modelo: 'ai', '3d_upload', 'svg', 'texture_image'.")
    nombre_personalizado: str = Field(..., max_length=30)
    usuario_id: Optional[str] = None 
    modelo: ModeloCreate
    parametros: ParametrosCreate
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