# app/services/automation_service.py
import asyncio
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Type
from datetime import datetime, timedelta

# Importações de sincronização
from app.infra.camara_api import camara_api_client
from app.infra.db.models import entidades as models_entidades
from app.infra.db.crud.entidades import upsert_entidade
from app.infra.db.models.entidades import Base

# Importações de scoring
from app.infra.db.session import SessionLocal
from app.infra.db.crud.ai_data import get_unscored_propositions
from app.services.scoring_service import analyze_and_score_propositions


# --- Lógica de Sincronização (Adaptada do sync_all.py) ---

async def fetch_and_save_detail(db: Session, model: Type[Base], item_uri: str):
    """ Busca os detalhes de uma entidade específica e salva no banco. """
    try:
        endpoint_path = item_uri.replace(camara_api_client.base_url, "")
        detail_response = await camara_api_client.get(endpoint=endpoint_path)
        if detail_response and 'dados' in detail_response:
            upsert_entidade(db, model, detail_response['dados'])
    except Exception as e:
        print(f"Erro ao processar a URI {item_uri}: {e}")

async def sync_entity(db: Session, model: Type[Base], endpoint: str, params: Dict[str, Any] = {}):
    """ Função genérica para sincronizar uma entidade (descoberta + enriquecimento). """
    print(f"--- [SYNC] Iniciando descoberta para {model.__tablename__}... ---")
    summary_data: List[Dict[str, Any]] = []
    next_url: str = f"{camara_api_client.base_url}{endpoint}"
    current_params = params.copy()
    
    while next_url:
        clean_endpoint = next_url.replace(camara_api_client.base_url, '')
        api_response = await camara_api_client.get(endpoint=clean_endpoint)
        if not (api_response and 'dados' in api_response):
            break
            
        summary_data.extend(api_response['dados'])
        self_link = next((link for link in api_response.get('links', []) if link['rel'] == 'self'), None)
        next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
        next_url = None if (next_link and self_link and next_link['href'] == self_link['href']) else (next_link['href'] if next_link else None)

    if summary_data:
        print(f"--- [SYNC] {len(summary_data)} itens descobertos. Iniciando enriquecimento... ---")
        tasks = [fetch_and_save_detail(db, model, item['uri']) for item in summary_data if 'uri' in item]
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            await asyncio.gather(*tasks[i:i + batch_size])
        db.commit()

async def run_full_sync():
    """ Executa a sincronização de todas as entidades principais. """
    db = SessionLocal()
    try:
        # Para a sincronização diária, só precisamos buscar dados recentes.
        # Buscamos os últimos 2 dias para garantir que não perdemos nada.
        two_days_ago = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        
        # Sincroniza apenas o que muda com frequência
        await sync_entity(db, models_entidades.Proposicao, "/proposicoes", 
                            params={'dataApresentacaoInicio': two_days_ago, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entity(db, models_entidades.Votacao, "/votacoes", 
                            params={'dataInicio': two_days_ago, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        # Outras entidades como deputados e partidos mudam com menos frequência e podem ter outra rotina
    finally:
        db.close()


# --- Lógica de Scoring (Adaptada do score_propositions.py) ---

async def run_scoring_task():
    """ Executa uma rodada do serviço de análise e pontuação de IA. """
    db = SessionLocal()
    try:
        print("--- [SCORING] Buscando proposições não analisadas... ---")
        propositions_to_score = get_unscored_propositions(db, limit=15)

        if propositions_to_score:
            print(f"--- [SCORING] Encontradas {len(propositions_to_score)} proposições para analisar.")
            await analyze_and_score_propositions(db, propositions_to_score)
        else:
            print("--- [SCORING] Nenhuma proposição nova para analisar no momento.")
    finally:
        db.close()


# --- Tarefa Principal do Agendador ---

async def run_daily_update_task():
    """
    A tarefa mestre que o agendador irá chamar.
    Primeiro sincroniza, depois analisa.
    """
    print(f"\n--- [AGENDADOR] INICIANDO TAREFA DE ATUALIZAÇÃO DIÁRIA - {datetime.now()} ---")
    await run_full_sync()
    await run_scoring_task()
    print(f"--- [AGENDADOR] TAREFA DE ATUALIZAÇÃO DIÁRIA FINALIZADA - {datetime.now()} ---\n")