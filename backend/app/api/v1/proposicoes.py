# camara_insights/app/api/v1/proposicoes.py
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

@router.get("/proposicoes", response_model=List[schemas.ProposicaoSchema])
def read_proposicoes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"), 
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sigla_tipo: Optional[str] = Query(None, description="Filtra por sigla do tipo de proposição (ex: PL, PEC)"),
    ano: Optional[int] = Query(None, description="Filtra por ano de apresentação da proposição"),
    sort: Optional[str] = Query(None, description="Ordena os resultados. Formato: campo:direcao (ex: ano:desc)")
):
    """
    Retorna uma lista de proposições com paginação, filtros e ordenação opcionais.
    """
    proposicoes = crud.get_proposicoes(
        db=db, skip=skip, limit=limit, sigla_tipo=sigla_tipo, ano=ano, sort=sort
    )
    return proposicoes