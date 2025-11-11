from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os

from app.db.session import get_db
from app.schemas.nfc import NFCConfigResponse, NFCConfigUpdateRequest
from app.crud.nfc import get_nfc_by_item_id, get_nfc_by_short_code, update_nfc_url, get_click_stats
from app.crud.nfc import register_visit
from fastapi.responses import RedirectResponse
from datetime import date

BASE_URL = os.environ.get("BASE_URL")

router = APIRouter()


@router.get("/config/{item_id}", response_model=NFCConfigResponse)
def get_nfc_config(item_id: str, db: Session = Depends(get_db)):

    nfc = get_nfc_by_item_id(db, item_id)
    if not nfc:
        raise HTTPException(status_code=404, detail="NFC no encontrado para este item.")
    print(nfc)

    stats = get_click_stats(db, nfc.id)

    return NFCConfigResponse(
        item_id=item_id,
        short_code=nfc.short_code,
        url_short_code=f"{BASE_URL}/{nfc.short_code}",
        url_destino_actual=nfc.url_destino_actual,
        data=stats
    )


@router.put("/config/{short_code}", response_model=NFCConfigResponse)
def update_nfc_config(short_code: str, payload: NFCConfigUpdateRequest, db: Session = Depends(get_db)):

    # now the path param is explicitly the short_code
    nfc = get_nfc_by_short_code(db, short_code)
    if not nfc:
        raise HTTPException(status_code=404, detail="NFC no encontrado para este item.")

    nfc = update_nfc_url(db, nfc, payload.url_destino_actual)

    stats = get_click_stats(db, nfc.id)

    # keep response shape identical to previous behaviour
    return NFCConfigResponse(
        item_id=short_code,
        short_code=nfc.short_code,
        url_short_code=f"{BASE_URL}/{nfc.short_code}",
        url_destino_actual=nfc.url_destino_actual,
        data=stats
    )


@router.get("/{short_code}")
def redirect_short_code(short_code: str, db: Session = Depends(get_db)):

    nfc = get_nfc_by_short_code(db, short_code)
    print(nfc)
    if not nfc:
        raise HTTPException(status_code=404, detail="NFC no encontrado")

    # registrar la visita (incrementa o crea el conteo para el día de hoy)
    register_visit(db, nfc.id)

    # redirigir al url destino
    return RedirectResponse(url=nfc.url_destino_actual, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
