# camara_insights/scripts/sync_all.py
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Type

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Início das Correções de Importação ---
from sqlalchemy.orm import Session
from app.infra.db.session import SessionLocal
from app.infra.db.models.entidades import Base
# --- Fim das Correções de Importação ---

from app.infra.camara_api import camara_api_client
from app.infra.db.crud.entidades import upsert_entidade
from app.infra.db.models import entidades as models

async def fetch_and_save_detail(db: Session, model: Type[Base], item_uri: str):
    """ Busca os detalhes de uma entidade específica e salva no banco. """
    try:
        # Extrai o path da URI completa para usar no nosso client
        endpoint_path = item_uri.replace(camara_api_client.base_url, "")
        detail_response = await camara_api_client.get(endpoint=endpoint_path)
        
        if detail_response and 'dados' in detail_response:
            # O endpoint de detalhe retorna os dados diretamente no objeto 'dados'
            upsert_entidade(db, model, detail_response['dados'])
        else:
            print(f"Não foi possível obter detalhes para a URI: {item_uri}")
    except Exception as e:
        print(f"Erro ao processar a URI {item_uri}: {e}")

async def sync_entidade(db: Session, model: Type[Base], endpoint: str, params: Dict[str, Any] = {}):
    """
    Função genérica para sincronizar uma entidade.
    1. Busca a lista de itens no endpoint de listagem.
    2. Para cada item, busca seus detalhes completos.
    3. Salva os detalhes no banco de dados.
    """
    print(f"Iniciando descoberta para {model.__tablename__}...")
    
    # 1. Descoberta
    summary_data: List[Dict[str, Any]] = []
    next_url: str = f"{camara_api_client.base_url}{endpoint}"
    current_params = params.copy()
    
    while next_url:
        print(f"Buscando lista de: {next_url.split('?')[0]} com params: {current_params}")
        clean_endpoint = next_url.replace(camara_api_client.base_url, '')
        api_response = await camara_api_client.get(endpoint=clean_endpoint)
        
        if api_response and 'dados' in api_response:
            summary_data.extend(api_response['dados'])
            
            self_link = next((link for link in api_response.get('links', []) if link['rel'] == 'self'), None)
            next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
            
            if next_link and self_link and next_link['href'] == self_link['href']:
                next_url = None
            else:
                next_url = next_link['href'] if next_link else None

            current_params = {}
        else:
            print(f"Não foram encontrados mais dados ou houve erro para {model.__tablename__} em {next_url}.")
            break

    # 2. Enriquecimento
    if summary_data:
        print(f"{len(summary_data)} itens descobertos para {model.__tablename__}. Iniciando enriquecimento...")
        
        tasks = [fetch_and_save_detail(db, model, item['uri']) for item in summary_data if 'uri' in item]
        
        # Processa em lotes concorrentes para não sobrecarregar a API
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            await asyncio.gather(*batch)
            print(f"Lote {i//batch_size + 1} de {len(tasks)//batch_size + 1} para {model.__tablename__} processado.")
        
        db.commit()
        print(f"Enriquecimento e salvamento para {model.__tablename__} concluídos.")
    else:
        print(f"Nenhum registro encontrado para {model.__tablename__}.")

async def main():
    db = SessionLocal()
    try:
        start_date = "2023-01-01" 

        await sync_entidade(db, models.Deputado, "/deputados", params={'itens': 100})
        await sync_entidade(db, models.Partido, "/partidos", params={'itens': 100})
        await sync_entidade(db, models.Orgao, "/orgaos", params={'itens': 100})
        await sync_entidade(db, models.Proposicao, "/proposicoes", 
                            params={'dataApresentacaoInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entidade(db, models.Evento, "/eventos", 
                            params={'dataInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entidade(db, models.Votacao, "/votacoes", 
                            params={'dataInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
    finally:
        db.close()

if __name__ == "__main__":
    print("--- INICIANDO SINCRONIZAÇÃO GERAL (COM ENRIQUECIMENTO) ---")
    asyncio.run(main())
    print("--- SINCRONIZAÇÃO GERAL CONCLUÍDA ---")