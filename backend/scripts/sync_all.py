# camara_insights/scripts/sync_all.py
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Type, Tuple
from dateutil.parser import parse
from collections.abc import MutableMapping

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

# --- Função Utilitária ---

def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Achata um dicionário aninhado.
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# --- Funções de Sincronização Principais ---

async def fetch_and_process_paginated_data(endpoint: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Busca todos os dados de um endpoint paginado da API da Câmara.
    """
    all_data: List[Dict[str, Any]] = []
    page = 1
    
    # Imprime os parâmetros usados para a busca (sem a página)
    param_str = '&'.join([f"{k}={v}" for k, v in params.items() if k != 'pagina'])
    print(f"Buscando: {endpoint}?{param_str}...")

    while True:
        current_params = params.copy()
        current_params['pagina'] = page
        
        print(f"  - Página: {page}")
        api_response = await camara_api_client.get(endpoint=endpoint, params=current_params)
        
        if api_response and 'dados' in api_response and api_response['dados']:
            all_data.extend(api_response['dados'])
            
            next_link = next((link for link in api_response.get('links', []) if link['rel'] == 'next'), None)
            if not next_link:
                print(f"Fim da paginação para {endpoint}.")
                break
            
            page += 1
        else:
            print(f"Não foram encontrados mais dados ou houve erro para o endpoint {endpoint} na página {page}.")
            break
            
    return all_data

async def fetch_with_semaphore(semaphore: asyncio.Semaphore, endpoint: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Wrapper para chamadas de API com controle de concorrência."""
    async with semaphore:
        return await camara_api_client.get(endpoint=endpoint, params=params)

async def sync_entidade_com_detalhes(db: Session, model: Type[Base], endpoint: str, params: Dict[str, Any] = {}):
    """
    Função genérica e robusta para sincronizar entidades (lista -> detalhes).
    """
    param_str = ', '.join([f"{k}: {v}" for k, v in params.items()])
    print(f"\n--- Iniciando sincronização para {model.__tablename__} com filtros: [{param_str}] ---")
    
    summary_data = await fetch_and_process_paginated_data(endpoint, params)
    
    if not summary_data:
        print(f"Nenhum item encontrado para {model.__tablename__} com os filtros aplicados.")
        return

    print(f"{len(summary_data)} itens descobertos. Buscando detalhes...")
    
    model_columns = {c.name: c.type for c in model.__table__.columns}
    pk_name = model.__mapper__.primary_key[0].name
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    all_tasks = []
    for item in summary_data:
        if 'uri' in item and item['uri']:
            detail_endpoint = item['uri'].replace(camara_api_client.base_url, "")
            all_tasks.append(fetch_with_semaphore(semaphore, detail_endpoint))

    for i in range(0, len(all_tasks), BATCH_SIZE):
        batch_tasks = all_tasks[i:i + BATCH_SIZE]
        responses = await asyncio.gather(*batch_tasks)
        
        all_data_to_upsert = []
        for response in responses:
            if not (response and 'dados' in response):
                continue

            flattened_data = flatten_dict(response['dados'])
            filtered_data = {k: v for k, v in flattened_data.items() if k in model_columns}

            for key, value in filtered_data.items():
                if value is None: continue
                column_type = model_columns.get(key)
                if isinstance(column_type, (Date, DateTime)) and isinstance(value, str):
                    try:
                        parsed_datetime = parse(value)
                        filtered_data[key] = parsed_datetime.date() if isinstance(column_type, Date) else parsed_datetime
                    except (ValueError, TypeError):
                        filtered_data[key] = None
            
            if model == models.Votacao and flattened_data.get('proposicao_id'):
                filtered_data['proposicao_id'] = flattened_data['proposicao_id']

            all_data_to_upsert.append(filtered_data)
        
        if all_data_to_upsert:
            stmt = insert(model).values(all_data_to_upsert)
            update_columns = {
                c.name: getattr(stmt.excluded, c.name) for c in model.__table__.columns if c.name != pk_name
            }
            stmt = stmt.on_conflict_do_update(
                index_elements=[pk_name],
                set_=update_columns
            )
            db.execute(stmt)
            db.commit()
            
        print(f"Lote de detalhes {i//BATCH_SIZE + 1}/{len(all_tasks)//BATCH_SIZE + 1} para {model.__tablename__} processado.")
            
    print(f"Sincronização com detalhes para {model.__tablename__} concluída.")


async def sync_child_entidade(db: Session, parent_model: Type[Base], child_model: Type[Base], endpoint_template: str, child_fk_name: str, params: Dict[str, Any] = {}, paginated: bool = True):
    """
    Sincroniza uma entidade 'filha' de forma otimizada.
    """
    param_str = ', '.join([f"{k}: {v}" for k, v in params.items()])
    print(f"\n--- Sincronizando entidade filha: {child_model.__tablename__} com filtros: [{param_str}] ---")
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
        print(f"Lote de pais {i//BATCH_SIZE + 1}/{len(parent_ids)//BATCH_SIZE+1 if parent_ids else 1} para {child_model.__tablename__} processado.")

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
        print(f"Lote {i//BATCH_SIZE + 1}/{len(proposicoes_uris)//BATCH_SIZE+1 if proposicoes_uris else 1} de autores de proposições processado.")

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
        # Data de início da legislatura atual para filtrar os dados
        start_date = "2025-07-01" 
        current_year = str(datetime.now().year)
        
        base_params = {'itens': 100}
        date_params = {**base_params, 'dataInicio': start_date, 'ordem': 'ASC', 'ordenarPor': 'id'}
        proposicao_params = {**base_params, 'dataApresentacaoInicio': start_date, 'ordem': 'ASC', 'ordenarPor': 'id'}


        print("--- ETAPA 1: SINCRONIZANDO ENTIDADES PRINCIPAIS ---")
        await sync_entidade_com_detalhes(db, models.Deputado, "/deputados", params=base_params)
        await sync_entidade_com_detalhes(db, models.Partido, "/partidos", params=base_params)
        await sync_entidade_com_detalhes(db, models.Orgao, "/orgaos", params=base_params)
        await sync_entidade_com_detalhes(db, models.Proposicao, "/proposicoes", params=proposicao_params)
        await sync_entidade_com_detalhes(db, models.Evento, "/eventos", params=date_params)
        await sync_entidade_com_detalhes(db, models.Votacao, "/votacoes", params=date_params)
        
        print("\n--- ETAPA 2: SINCRONIZANDO FRENTES, BLOCOS E GRUPOS ---")
        for model, endpoint in [(models.Frente, "/frentes"), (models.Bloco, "/blocos"), (models.Grupo, "/grupos")]:
            data = await fetch_and_process_paginated_data(endpoint, base_params)
            if data:
                pk_name = model.__mapper__.primary_key[0].name
                stmt = insert(model).values(data)
                update_cols = {c.name: getattr(stmt.excluded, c.name) for c in model.__table__.columns if c.name != pk_name}
                stmt = stmt.on_conflict_do_update(index_elements=[pk_name], set_=update_cols)
                db.execute(stmt)
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
        despesa_params = {**base_params, 'ano': current_year}
        discurso_params = {**base_params, 'dataInicio': start_date}
        
        await sync_proposicao_autores(db)
        await sync_child_entidade(db, models.Deputado, models.Despesa, "/deputados/{id}/despesas", "deputado_id", params=despesa_params)
        await sync_child_entidade(db, models.Deputado, models.Discurso, "/deputados/{id}/discursos", "deputado_id", params=discurso_params)
        await sync_child_entidade(db, models.Proposicao, models.Tramitacao, "/proposicoes/{id}/tramitacoes", "proposicao_id", paginated=False)
        await sync_child_entidade(db, models.Votacao, models.Voto, "/votacoes/{id}/votos", "votacao_id", paginated=False)

    finally:
        # A linha abaixo foi removida para corrigir o erro 'AttributeError'
        # await camara_api_client.close()
        db.close()

if __name__ == "__main__":
    print("--- INICIANDO SINCRONIZAÇÃO GERAL (OTIMIZADA) ---")
    asyncio.run(main())
    print("\n--- SINCRONIZAÇÃO GERAL CONCLUÍDA ---")