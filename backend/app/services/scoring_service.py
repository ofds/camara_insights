import logging

# app/services/scoring_service.py
import asyncio
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.infra.llm_client import llm_client
from app.infra.db.models.ai_data import ProposicaoAIData

def _calculate_impact_score(proposicao: Dict[str, Any], analysis: Dict[str, Any]) -> int:
    """
    Calcula o score de impacto final com base na análise do LLM e nos dados da proposição.
    """
    score = 0
    
    # Pesos por Abrangência
    scope_weights = {"Nacional": 35, "Estadual": 15, "Municipal": 5}
    score += scope_weights.get(analysis.get("scope", ""), 0)

    # Pesos por Magnitude
    magnitude_weights = {"População Geral": 25, "Setorial Específico": 15, "Alto": 10, "Médio": 5, "Baixo": 5}
    score += magnitude_weights.get(analysis.get("magnitude", ""), 0)

    # Estimativa direta do LLM
    score += int(analysis.get("llm_impact_estimate", 0))

    # Bônus por Relevância Jurídica (PEC)
    if proposicao.siglaTipo == 'PEC':
        score += 10
        
    return min(score, 100) # Garante que o score não passe de 100

async def analyze_and_score_propositions(db: Session, propositions: list):
    """
    Coordena a análise de um lote de proposições, calcula o score e salva no banco.
    """
    if not propositions:
        logging.info("Nenhuma proposição nova para analisar.")
        return

    # Cria tarefas assíncronas para análise no LLM
    tasks = [
        llm_client.analyze_proposition(prop.id, prop.ementa) for prop in propositions
    ]
    
    # Executa as tarefas concorrentemente
    analysis_results = await asyncio.gather(*tasks)

    for prop, analysis in zip(propositions, analysis_results):
        if not analysis:
            logging.warning(f"Análise falhou ou foi pulada para a proposição ID: {prop.id}")
            continue

        # Verifica se o ID retornado pela LLM bate com o ID enviado
        if int(analysis.get("proposicao_id", 0)) != prop.id:
            logging.warning(f"ID da proposição na resposta do LLM ({analysis.get('proposicao_id')}) não corresponde ao esperado ({prop.id}). Pulando.")
            continue

        # Calcula o score final
        final_score = _calculate_impact_score(prop, analysis)

        # Cria o objeto para salvar no banco de dados
        ai_data_obj = ProposicaoAIData(
            proposicao_id=prop.id,
            summary=analysis.get("summary"),
            scope=analysis.get("scope"),
            magnitude=analysis.get("magnitude"),
            tags=analysis.get("tags"),
            llm_impact_estimate=analysis.get("llm_impact_estimate"),
            impact_score=final_score,
            model_version=llm_client.model
        )
        db.add(ai_data_obj)
    
    db.commit()
    logging.info(f"{len(propositions)} proposições processadas e salvas.")