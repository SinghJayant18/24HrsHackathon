from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, schemas


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[schemas.ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.list_items(db)


@router.post("/", response_model=schemas.ItemOut)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = crud.create_item(db, payload)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = crud.update_item(db, item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.commit()
    db.refresh(item)
    return item

