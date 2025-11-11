from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.nfc import NFCConfigResponse, NFCConfigUpdateRequest
from app.crud.nfc import get_nfc_by_item_id, get_nfc_by_short_code, update_nfc_url, get_click_stats

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
        url_short_code=f"https://creamax.app/{nfc.short_code}",
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
        url_short_code=f"https://creamax.app/{nfc.short_code}",
        url_destino_actual=nfc.url_destino_actual,
        data=stats
    )
