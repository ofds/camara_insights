# camara_insights/app/api/v1/votacoes.py
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

@router.get("/votacoes", response_model=List[schemas.VotacaoSchema])
def read_votacoes(
    skip: int = Query(0, ge=0, description="Número de registros a pular"), 
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"), 
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de votações com paginação.
    """
    votacoes = crud.get_votacoes(db, skip=skip, limit=limit)
    return votacoes