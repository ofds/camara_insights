import logging

# backend/app/api/v1/deputados.py

from fastapi import APIRouter, Depends, Query, Request, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date, timedelta

from app.domain import entidades as schemas
from app.infra.db.crud import entidades as crud
from app.infra.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/deputados/impacto-avg", response_model=schemas.DeputadoImpactoAvgSchema)
def read_deputados_impacto_avg(
    period: str = Query("weekly", enum=["weekly", "monthly"]),
    db: Session = Depends(get_db)
):
    """
    Calcula o impacto médio dos deputados na última semana ou mês.
    """
    end_date = date.today()
    if period == "weekly":
        start_date = end_date - timedelta(days=7)
    else: # monthly
        start_date = end_date - timedelta(days=30)
    
    average_impact = crud.get_deputados_avg_impact(db, start_date=start_date, end_date=end_date)

    return {
        "period": period,
        "average_impact": average_impact,
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/deputados/ranking", response_model=List[schemas.DeputadoRankingSchema])
def get_deputados_ranking(db: Session = Depends(get_db)):
    """
    Retorna um ranking de deputados com base no impacto de suas proposições no último mês.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    ranked_deputados = crud.get_deputados_ranking_by_impact(db, start_date=start_date, end_date=end_date)
    return ranked_deputados

@router.get("/deputados/{deputado_id}", response_model=schemas.DeputadoSchemaDetalhado)
def read_deputado_by_id(deputado_id: int, db: Session = Depends(get_db)):
    """
    Retorna informações detalhadas de um deputado específico pelo seu ID.
    """
    db_deputado = crud.get_deputado_by_id(db, deputado_id=deputado_id)
    if db_deputado is None:
        raise HTTPException(status_code=404, detail="Deputado não encontrado")
    return db_deputado

@router.get("/deputados", response_model=List[schemas.DeputadoSchema])
def read_deputados(
    req: Request,
    res: Response,  # Add the response object as a dependency
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=200, description="Número de registros a retornar"),
    sort: Optional[str] = Query(None, description="Ordena os resultados usando campo:direção, ex: nome:asc,id:desc")
):
    """
    Retorna uma lista de deputados com paginação, ordenação e filtragem dinâmicas.
    """
    filters: Dict[str, Any] = {
        key: value
        for key, value in req.query_params.items()
        if key not in ["skip", "limit", "sort"]
    }
    
    # Obter deputados e contagem total da função CRUD atualizada
    deputados, total_count = crud.get_deputados(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort
    )
    
    # Definir o cabeçalho X-Total-Count
    res.headers["X-Total-Count"] = str(total_count)

    # Expor o cabeçalho para que o navegador do cliente possa acessá-lo (importante para CORS)
    res.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    
    return deputados

@router.get("/deputados/{deputado_id}/activity/proposals", response_model=schemas.PropostaActivitySchema)
def read_deputado_proposal_activity(deputado_id: int, db: Session = Depends(get_db)):
    """
    Retorna as datas de apresentação das propostas de um deputado.
    """
    activity_dates = crud.get_proposal_activity(db, deputado_id=deputado_id)
    if not activity_dates:
        raise HTTPException(status_code=404, detail="Nenhuma atividade de proposta encontrada para este deputado")
    return {"activity": activity_dates}