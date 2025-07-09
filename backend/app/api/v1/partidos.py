# camara_insights/app/api/v1/partidos.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.domain import entidades as schemas
from app.infra.db.crud import entidades as crud
from app.infra.db.session import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/partidos", response_model=List[schemas.PartidoSchema])
def read_partidos(
    skip: int = Query(0, ge=0, description="Número de registros a pular"), 
    limit: int = Query(50, ge=1, le=100, description="Número de registros a retornar"), 
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de partidos políticos com paginação.
    """
    partidos = crud.get_partidos(db, skip=skip, limit=limit)
    return partidos