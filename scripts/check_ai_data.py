# scripts/check_ai_data.py
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infra.db.session import SessionLocal
from app.infra.db.models.ai_data import ProposicaoAIData
from app.infra.db.models.entidades import Proposicao

def check_results():
    db = SessionLocal()
    try:
        print("--- Verificando os 10 últimos resultados da análise de IA ---")
        
        # Busca os últimos 10 resultados da tabela de IA,
        # e também busca a proposição original para termos contexto.
        results = (
            db.query(ProposicaoAIData, Proposicao)
            .join(Proposicao, ProposicaoAIData.proposicao_id == Proposicao.id)
            .order_by(ProposicaoAIData.created_at.desc())
            .limit(10)
            .all()
        )

        if not results:
            print("Nenhum dado de análise de IA encontrado no banco de dados.")
            return

        for ai_data, proposicao in results:
            print("\n" + "="*80)
            print(f"Análise para Proposição ID: {ai_data.proposicao_id} ({proposicao.siglaTipo} {proposicao.numero}/{proposicao.ano})")
            print(f"Ementa Original: {proposicao.ementa}")
            print("-"*80)
            print(f"Modelo Utilizado: {ai_data.model_version}")
            print(f"Score de Impacto (Calculado): {ai_data.impact_score}")
            print(f"Score (Estimativa LLM): {ai_data.llm_impact_estimate}")
            print(f"Resumo (Summary): {ai_data.summary}")
            print(f"Abrangência (Scope): {ai_data.scope}")
            print(f"Magnitude: {ai_data.magnitude}")
            # json.dumps para formatar o JSON de forma legível
            print(f"Tags: {json.dumps(ai_data.tags, indent=2, ensure_ascii=False)}")
            print("="*80)

    finally:
        db.close()

if __name__ == "__main__":
    check_results()