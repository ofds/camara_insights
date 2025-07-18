import logging

# app/infra/db/crud/ai_data.py
from sqlalchemy.orm import Session
from typing import List

from app.infra.db.models import entidades as models_entidades
from app.infra.db.models import ai_data as models_ai

def get_unscored_propositions(db: Session, limit: int = 50) -> List[models_entidades.Proposicao]:
    """
    Busca proposições que ainda não possuem uma análise de IA correspondente.
    Usa um LEFT JOIN para encontrar proposições sem um registro na tabela proposicao_ai_data.
    """
    return (
        db.query(models_entidades.Proposicao)
        .outerjoin(
            models_ai.ProposicaoAIData,
            models_entidades.Proposicao.id == models_ai.ProposicaoAIData.proposicao_id
        )
        .filter(models_ai.ProposicaoAIData.id == None)
        .order_by(models_entidades.Proposicao.dataApresentacao.asc())
        .limit(limit)
        .all()
    )