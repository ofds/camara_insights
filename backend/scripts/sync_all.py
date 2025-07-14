# camara_insights/scripts/sync_all.py
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Type, Tuple
from dateutil.parser import parse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Date, DateTime
from app.infra.db.session import SessionLocal
from app.infra.db.models.entidades import Base
from app.infra.camara_api import camara_api_client
from app.infra.db.models import entidades as models

# --- Constantes de Otimização ---
# Limita o número de requisições simultâneas à API para evitar erros 429.
# Um valor entre 10 e 20 é geralmente seguro.
CONCURRENCY_LIMIT = 10
# Define o tamanho dos lotes para processamento em memória e inserção no banco.
BATCH_SIZE = 50

# --- Funções de Sincronização Principais ---

async def fetch_and_process_paginated_data(endpoint: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Busca todos os dados de um endpoint paginado da API da Câmara.
    (Otimizado com paginação manual para maior robustez)
    """
    all_data: List[Dict[str, Any]] = []
    page = 1
    
    while True:
        current_params = params.copy()
        current_params['pagina'] = page
        
        print(f"Buscando: {endpoint} | Página: {page}")
        api_response = await camara_api_client.get(endpoint=endpoint, params=current_params)
        
        if api_response and 'dados' in api_response and api_response['dados']:
            all_data.extend(api_response['dados'])
            
            next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
            self_link = next((link for link in api_response.get('links', []) if link['rel'] == 'self'), None)

            if not next_link or (self_link and next_link['href'] == self_link['href']):
                print(f"Fim da paginação para {endpoint}.")
                break
            
            page += 1
        else:
            print(f"Não foram encontrados mais dados ou houve erro para o endpoint {endpoint} na página {page}.")
            break
            
    return all_data

def upsert_entidade(db: Session, model: Type[Base], data: Dict[str, Any]):
    """
    Realiza o 'upsert' (insert ou update) de uma única entidade no banco de dados.
    """
    pk_name = model.__mapper__.primary_key[0].name
    pk_value = data.get(pk_name)
    
    if not pk_value:
        return

    model_columns = {c.name: c.type for c in model.__table__.columns}
    filtered_data = {k: v for k, v in data.items() if k in model_columns}

    for key, value in filtered_data.items():
        if value is None:
            continue
        
        column_type = model_columns.get(key)
        
        if isinstance(column_type, (Date, DateTime)) and isinstance(value, str):
            try:
                parsed_datetime = parse(value)
                filtered_data[key] = parsed_datetime.date() if isinstance(column_type, Date) else parsed_datetime
            except (ValueError, TypeError):
                filtered_data[key] = None
    
    if model == models.Votacao and data.get('proposicao') and data['proposicao'].get('id'):
        filtered_data['proposicao_id'] = data['proposicao']['id']

    stmt = insert(model.__table__).values(**filtered_data)
    update_dict = {k: v for k, v in filtered_data.items() if k != pk_name}
    
    stmt = stmt.on_conflict_do_update(index_elements=[pk_name], set_=update_dict) if update_dict else stmt.on_conflict_do_nothing(index_elements=[pk_name])
    
    db.execute(stmt)

async def fetch_with_semaphore(semaphore: asyncio.Semaphore, endpoint: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Wrapper para chamadas de API com controle de concorrência."""
    async with semaphore:
        return await camara_api_client.get(endpoint=endpoint, params=params)

async def sync_entidade_com_detalhes(db: Session, model: Type[Base], endpoint: str, params: Dict[str, Any] = {}):
    """
    Função genérica otimizada para sincronizar entidades (lista -> detalhes) com concorrência controlada.
    """
    print(f"\n--- Iniciando sincronização com detalhes para {model.__tablename__}... ---")
    
    summary_data = await fetch_and_process_paginated_data(endpoint, params)
    
    if not summary_data:
        print(f"Nenhum item encontrado para {model.__tablename__}.")
        return

    print(f"{len(summary_data)} itens descobertos para {model.__tablename__}. Buscando detalhes...")
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    all_tasks = []
    for item in summary_data:
        if 'uri' in item:
            detail_endpoint = item['uri'].replace(camara_api_client.base_url, "")
            all_tasks.append(fetch_with_semaphore(semaphore, detail_endpoint))

    for i in range(0, len(all_tasks), BATCH_SIZE):
        batch_tasks = all_tasks[i:i + BATCH_SIZE]
        responses = await asyncio.gather(*batch_tasks)
        for response in responses:
            if response and 'dados' in response:
                upsert_entidade(db, model, response['dados'])
        db.commit()
        print(f"Lote {i//BATCH_SIZE + 1} de {len(all_tasks)//BATCH_SIZE + 1} para {model.__tablename__} processado.")
        
    print(f"Sincronização com detalhes para {model.__tablename__} concluída.")

async def sync_child_entidade(db: Session, parent_model: Type[Base], child_model: Type[Base], endpoint_template: str, child_fk_name: str, params: Dict[str, Any] = {}, paginated: bool = True):
    """
    Sincroniza uma entidade 'filha' com concorrência controlada e processamento em lotes.
    """
    print(f"\n--- Iniciando sincronização de entidade filha: {child_model.__tablename__} (Paginado: {paginated}) ---")
    parent_ids: List[Tuple[Any]] = db.query(parent_model.id).all()

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async def fetch_child_data(parent_id):
        endpoint = endpoint_template.format(id=parent_id)
        return await fetch_with_semaphore(semaphore, endpoint, params) if paginated else await fetch_with_semaphore(semaphore, endpoint)

    all_child_data_to_insert = []
    
    for i in range(0, len(parent_ids), BATCH_SIZE):
        parent_batch = parent_ids[i:i + BATCH_SIZE]
        tasks = [fetch_child_data(pid) for (pid,) in parent_batch]
        results = await asyncio.gather(*tasks)
        
        batch_child_data = []
        for idx, result in enumerate(results):
            child_data_list = result if paginated else (result.get('dados') if result else [])
            if not child_data_list:
                continue

            current_parent_id = parent_batch[idx][0]
            for child_data in child_data_list:
                child_data[child_fk_name] = current_parent_id
                child_data.pop('id', None)
                batch_child_data.append(child_data)
        
        if batch_child_data:
            all_child_data_to_insert.extend(batch_child_data)
        
        print(f"Lote de pais {i//BATCH_SIZE + 1} para {child_model.__tablename__} processado.")

    if all_child_data_to_insert:
        print(f"Iniciando inserção em massa de {len(all_child_data_to_insert)} registros para {child_model.__tablename__}...")
        # A conversão de tipos é feita aqui, antes da inserção em massa
        for child_data in all_child_data_to_insert:
            model_columns = {c.name: c.type for c in child_model.__table__.columns}
            for key, value in child_data.items():
                if value is None: continue
                column_type = model_columns.get(key)
                if isinstance(column_type, (Date, DateTime)) and isinstance(value, str):
                    try:
                        parsed_datetime = parse(value)
                        child_data[key] = parsed_datetime.date() if isinstance(column_type, Date) else parsed_datetime
                    except (ValueError, TypeError):
                        child_data[key] = None
        
        db.bulk_insert_mappings(child_model, all_child_data_to_insert)
        db.commit()

    print(f"Sincronização de {child_model.__tablename__} concluída.")

async def main():
    db = SessionLocal()
    try:
        start_date = "2024-01-01"
        current_year = str(datetime.now().year)

        print("--- ETAPA 1: SINCRONIZANDO ENTIDADES PRINCIPAIS ---")
        await sync_entidade_com_detalhes(db, models.Deputado, "/deputados", params={'itens': 100})
        await sync_entidade_com_detalhes(db, models.Partido, "/partidos", params={'itens': 100})
        await sync_entidade_com_detalhes(db, models.Orgao, "/orgaos", params={'itens': 100})
        await sync_entidade_com_detalhes(db, models.Proposicao, "/proposicoes", params={'dataApresentacaoInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entidade_com_detalhes(db, models.Evento, "/eventos", params={'dataInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        await sync_entidade_com_detalhes(db, models.Votacao, "/votacoes", params={'dataInicio': start_date, 'itens': 100, 'ordem': 'ASC', 'ordenarPor': 'id'})
        
        print("\n--- ETAPA 2: SINCRONIZANDO FRENTES, BLOCOS E GRUPOS ---")
        frentes_data = await fetch_and_process_paginated_data("/frentes", {'itens': 100})
        for item in frentes_data: upsert_entidade(db, models.Frente, item)
        
        blocos_data = await fetch_and_process_paginated_data("/blocos", {'itens': 100})
        for item in blocos_data: upsert_entidade(db, models.Bloco, item)

        grupos_data = await fetch_and_process_paginated_data("/grupos", {'itens': 100})
        for item in grupos_data: upsert_entidade(db, models.Grupo, item)
        db.commit()
        print("Frentes, Blocos e Grupos sincronizados.")

        print("\n--- ETAPA 3: LIMPANDO DADOS DE ENTIDADES FILHAS ANTES DA SINCRONIZAÇÃO ---")
        db.execute(models.Despesa.__table__.delete())
        db.execute(models.Discurso.__table__.delete())
        db.execute(models.Tramitacao.__table__.delete())
        db.execute(models.Voto.__table__.delete())
        db.commit()
        print("Limpeza concluída.")

        print("\n--- ETAPA 4: SINCRONIZANDO ENTIDADES FILHAS ---")
        await sync_child_entidade(db, models.Deputado, models.Despesa, "/deputados/{id}/despesas", "deputado_id", params={'ano': current_year, 'itens': 100})
        await sync_child_entidade(db, models.Deputado, models.Discurso, "/deputados/{id}/discursos", "deputado_id", params={'dataInicio': start_date, 'itens': 100})
        await sync_child_entidade(db, models.Proposicao, models.Tramitacao, "/proposicoes/{id}/tramitacoes", "proposicao_id", paginated=False)
        await sync_child_entidade(db, models.Votacao, models.Voto, "/votacoes/{id}/votos", "votacao_id", paginated=False)

    finally:
        db.close()

if __name__ == "__main__":
    print("--- INICIANDO SINCRONIZAÇÃO GERAL (OTIMIZADA E SEQUENCIAL) ---")
    asyncio.run(main())
    print("\n--- SINCRONIZAÇÃO GERAL CONCLUÍDA ---")