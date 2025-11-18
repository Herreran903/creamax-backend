from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import date


class NFCStatsItem(BaseModel):
    dia: date
    clicks: int


class NFCConfigResponse(BaseModel):
    item_id: str
    short_code: str
    url_short_code: str
    url_destino_actual: Optional[HttpUrl]
    data: List[NFCStatsItem]


class NFCConfigUpdateRequest(BaseModel):
    url_destino_actual: HttpUrl
