from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, schemas


router = APIRouter(prefix="/catalogue", tags=["catalogue"])


@router.get("/", response_model=list[schemas.ItemOut])
def list_catalogue(db: Session = Depends(get_db)):
    return crud.list_items(db)

