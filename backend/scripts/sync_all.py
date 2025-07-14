# camara_insights/scripts/sync_all.py
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Type, Tuple
from dateutil.parser import parse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Date, DateTime
from app.infra.db.session import SessionLocal
from app.infra.db.models.entidades import Base
from app.infra.camara_api import camara_api_client
from app.infra.db.models import entidades as models

# --- Constantes de Otimização ---
CONCURRENCY_LIMIT = 10
BATCH_SIZE = 50

# --- Funções de Sincronização Principais ---

async def fetch_and_process_paginated_data(endpoint: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Busca todos os dados de um endpoint paginado da API da Câmara.
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
    Função genérica otimizada para sincronizar entidades (lista -> detalhes).
    """
    print(f"\n--- Iniciando sincronização com detalhes para {model.__tablename__}... ---")
    
    summary_data = await fetch_and_process_paginated_data(endpoint, params)
    
    if not summary_data:
        print(f"Nenhum item encontrado para {model.__tablename__}.")
        return

    print(f"{len(summary_data)} itens descobertos. Buscando detalhes...")
    
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
        print(f"Lote {i//BATCH_SIZE + 1}/{len(all_tasks)//BATCH_SIZE + 1} para {model.__tablename__} processado.")
        
    print(f"Sincronização com detalhes para {model.__tablename__} concluída.")

async def sync_child_entidade(db: Session, parent_model: Type[Base], child_model: Type[Base], endpoint_template: str, child_fk_name: str, params: Dict[str, Any] = {}, paginated: bool = True):
    """
    Sincroniza uma entidade 'filha' de forma otimizada.
    """
    print(f"\n--- Sincronizando entidade filha: {child_model.__tablename__} ---")
    parent_ids: List[Tuple[Any]] = db.query(parent_model.id).all()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async def fetch_child_data(parent_id):
        endpoint = endpoint_template.format(id=parent_id)
        if paginated:
            return await fetch_and_process_paginated_data(endpoint, params)
        else:
            response = await fetch_with_semaphore(semaphore, endpoint)
            return response.get('dados', []) if response else []

    all_child_data_to_insert = []
    for i in range(0, len(parent_ids), BATCH_SIZE):
        parent_batch = parent_ids[i:i + BATCH_SIZE]
        tasks = [fetch_child_data(pid) for (pid,) in parent_batch]
        results = await asyncio.gather(*tasks)
        
        for idx, child_data_list in enumerate(results):
            if not child_data_list: continue
            current_parent_id = parent_batch[idx][0]
            for child_data in child_data_list:
                child_data[child_fk_name] = current_parent_id
                child_data.pop('id', None)
                all_child_data_to_insert.append(child_data)
        print(f"Lote de pais {i//BATCH_SIZE + 1} para {child_model.__tablename__} processado.")

    if all_child_data_to_insert:
        print(f"Iniciando inserção em massa de {len(all_child_data_to_insert)} registros para {child_model.__tablename__}...")
        db.bulk_insert_mappings(child_model, all_child_data_to_insert)
        db.commit()
    print(f"Sincronização de {child_model.__tablename__} concluída.")

async def sync_proposicao_autores(db: Session):
    """
    Sincroniza a tabela de associação (M2M) entre proposições e seus autores.
    """
    print("\n--- Iniciando sincronização de autores de proposições (M2M) ---")

    proposicoes_uris: List[Tuple[int, str]] = db.query(
        models.Proposicao.id,
        models.Proposicao.uriAutores
    ).filter(models.Proposicao.uriAutores.isnot(None)).all()

    if not proposicoes_uris:
        print("Nenhuma proposição com autores para sincronizar.")
        return

    print(f"{len(proposicoes_uris)} proposições com URIs de autores encontradas.")
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    all_autores_to_insert = []

    async def fetch_autores(proposicao_id: int, uri: str):
        endpoint = uri.replace(camara_api_client.base_url, "")
        response = await fetch_with_semaphore(semaphore, endpoint)
        return proposicao_id, response.get('dados', []) if response else []

    for i in range(0, len(proposicoes_uris), BATCH_SIZE):
        batch_uris = proposicoes_uris[i:i + BATCH_SIZE]
        tasks = [fetch_autores(pid, uri) for pid, uri in batch_uris]
        results = await asyncio.gather(*tasks)

        for proposicao_id, autores_data in results:
            for autor_data in autores_data:
                autor_uri = autor_data.get("uri", "")
                if "/deputados/" in autor_uri:
                    try:
                        deputado_id = int(autor_uri.split("/")[-1])
                        all_autores_to_insert.append({
                            "proposicao_id": proposicao_id,
                            "deputado_id": deputado_id
                        })
                    except (ValueError, IndexError):
                        pass
        print(f"Lote {i//BATCH_SIZE + 1} de autores de proposições processado.")

    if all_autores_to_insert:
        print(f"Inserindo {len(all_autores_to_insert)} links autor-proposição...")
        stmt = insert(models.proposicao_autores).values(all_autores_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=['proposicao_id', 'deputado_id'])
        db.execute(stmt)
        db.commit()
    print("Sincronização de autores de proposições concluída.")


async def main():
    """
    Função principal que orquestra todas as etapas de sincronização.
    """
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
        for model, endpoint in [(models.Frente, "/frentes"), (models.Bloco, "/blocos"), (models.Grupo, "/grupos")]:
            data = await fetch_and_process_paginated_data(endpoint, {'itens': 100})
            for item in data: upsert_entidade(db, model, item)
        db.commit()
        print("Frentes, Blocos e Grupos sincronizados.")

        print("\n--- ETAPA 3: LIMPANDO DADOS DE RELACIONAMENTOS ---")
        db.execute(models.proposicao_autores.delete())
        db.execute(models.Despesa.__table__.delete())
        db.execute(models.Discurso.__table__.delete())
        db.execute(models.Tramitacao.__table__.delete())
        db.execute(models.Voto.__table__.delete())
        db.commit()
        print("Limpeza concluída.")

        print("\n--- ETAPA 4: SINCRONIZANDO RELACIONAMENTOS E ENTIDADES FILHAS ---")
        await sync_proposicao_autores(db) # <-- LÓGICA DE AUTORES INCORPORADA AQUI
        await sync_child_entidade(db, models.Deputado, models.Despesa, "/deputados/{id}/despesas", "deputado_id", params={'ano': current_year, 'itens': 100})
        await sync_child_entidade(db, models.Deputado, models.Discurso, "/deputados/{id}/discursos", "deputado_id", params={'dataInicio': start_date, 'itens': 100})
        await sync_child_entidade(db, models.Proposicao, models.Tramitacao, "/proposicoes/{id}/tramitacoes", "proposicao_id", paginated=False)
        await sync_child_entidade(db, models.Votacao, models.Voto, "/votacoes/{id}/votos", "votacao_id", paginated=False)

    finally:
        await camara_api_client.close()
        db.close()

if __name__ == "__main__":
    print("--- INICIANDO SINCRONIZAÇÃO GERAL (OTIMIZADA) ---")
    asyncio.run(main())
    print("\n--- SINCRONIZAÇÃO GERAL CONCLUÍDA ---")