# camara_insights/app/api/v1/deputados.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from typing import Optional

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

@router.get("/deputados", response_model=List[schemas.DeputadoSchema])
def read_deputados(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"), 
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sigla_uf: Optional[str] = Query(None, description="Filtra deputados por sigla da UF (ex: SP, RJ)"),
    sigla_partido: Optional[str] = Query(None, description="Filtra deputados por sigla do partido (ex: PT, MDB)")
):
    """
    Retorna uma lista de deputados com paginação e filtros opcionais.
    """
    deputados = crud.get_deputados(
        db=db, 
        skip=skip, 
        limit=limit, 
        sigla_uf=sigla_uf, 
        sigla_partido=sigla_partido
    )
    return deputados