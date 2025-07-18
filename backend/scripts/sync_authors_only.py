import logging

# /backend/app/scripts/sync_authors_only.py
import asyncio
import sys
import os
from typing import List, Dict, Any, Tuple

# Adiciona o diretório raiz do projeto ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.infra.db.session import SessionLocal
from app.infra.camara_api import camara_api_client
from app.infra.db.models import entidades as models

# --- Constantes de Otimização ---
# Limita o número de requisições simultâneas à API.
CONCURRENCY_LIMIT = 10
# Define o tamanho dos lotes para BUSCA na API.
API_FETCH_BATCH_SIZE = 50
# Define o tamanho dos lotes para INSERÇÃO no Banco de Dados.
DB_INSERT_BATCH_SIZE = 100


async def fetch_with_semaphore(semaphore: asyncio.Semaphore, endpoint: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Wrapper para chamadas de API com controle de concorrência."""
    async with semaphore:
        logging.info(f"Buscando dados de autores em: {endpoint}")
        return await camara_api_client.get(endpoint=endpoint, params=params)

async def sync_proposicao_autores(db: Session):
    """
    Sincroniza a tabela de associação (M2M) entre proposições e seus autores,
    inserindo os dados em lotes de 100.
    """
    logging.info("--- Iniciando sincronização de autores de proposições (M2M) ---")

    # 1. Limpa a tabela de associação para evitar dados obsoletos
    logging.info("Limpando a tabela proposicao_autores...")
    db.execute(models.proposicao_autores.delete())
    db.commit()
    logging.info("Tabela limpa.")

    # 2. Busca todas as proposições com seu uriAutores para processar
    proposicoes_uris: List[Tuple[int, str]] = db.query(
        models.Proposicao.id,
        models.Proposicao.uriAutores
    ).filter(models.Proposicao.uriAutores.isnot(None)).all()

    if not proposicoes_uris:
        logging.info("Nenhuma proposição com autores para sincronizar.")
        return

    logging.info(f"{len(proposicoes_uris)} proposições com URIs de autores encontradas.")
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    # Lista que acumulará os registros para o lote de inserção
    autores_para_inserir = []

    async def fetch_autores_for_proposicao(proposicao_id: int, uri: str):
        """Busca os autores para uma única proposição."""
        endpoint = uri.replace(camara_api_client.base_url, "")
        response = await fetch_with_semaphore(semaphore, endpoint)
        if response and 'dados' in response:
            return proposicao_id, response['dados']
        return proposicao_id, []

    # 3. Processa em lotes para não sobrecarregar a API
    for i in range(0, len(proposicoes_uris), API_FETCH_BATCH_SIZE):
        batch_uris = proposicoes_uris[i:i + API_FETCH_BATCH_SIZE]
        tasks = [fetch_autores_for_proposicao(pid, uri) for pid, uri in batch_uris]
        results = await asyncio.gather(*tasks)

        for proposicao_id, autores_data in results:
            if not autores_data:
                continue
            for autor_data in autores_data:
                autor_uri = autor_data.get("uri")
                if autor_uri and "/deputados/" in autor_uri:
                    try:
                        deputado_id = int(autor_uri.split("/")[-1])
                        autores_para_inserir.append({
                            "proposicao_id": proposicao_id,
                            "deputado_id": deputado_id
                        })
                    except (ValueError, IndexError):
                        print(f"AVISO: Não foi possível extrair o ID do deputado da URI: {autor_uri}")

        # ---> NOVA LÓGICA DE INSERÇÃO EM LOTES <---
        # Verifica se o lote atingiu o tamanho definido para inserção
        if len(autores_para_inserir) >= DB_INSERT_BATCH_SIZE:
            logging.info(f"Atingido o limite de {DB_INSERT_BATCH_SIZE}. Inserindo {len(autores_para_inserir)} registros no banco de dados...")
            stmt = insert(models.proposicao_autores).values(autores_para_inserir)
            stmt = stmt.on_conflict_do_nothing(index_elements=['proposicao_id', 'deputado_id'])
            db.execute(stmt)
            db.commit()
            autores_para_inserir = [] # Limpa a lista para o próximo lote

        logging.info(f"Lote de busca {i//API_FETCH_BATCH_SIZE + 1} de {len(proposicoes_uris)//API_FETCH_BATCH_SIZE + 1} processado.")

    # 4. Insere quaisquer registros restantes que não formaram um lote completo
    if autores_para_inserir:
        logging.info(f"Inserindo lote final de {len(autores_para_inserir)} autores restantes...")
        stmt = insert(models.proposicao_autores).values(autores_para_inserir)
        stmt = stmt.on_conflict_do_nothing(index_elements=['proposicao_id', 'deputado_id'])
        db.execute(stmt)
        db.commit()
    logging.info("Sincronização de autores de proposições concluída!")



async def main():
    """
    Função principal que inicializa o banco e chama a sincronização.
    """
    db = SessionLocal()
    try:
        await sync_proposicao_autores(db)
    finally:
        db.close()
        await camara_api_client.close()

if __name__ == "__main__":
    logging.info("--- EXECUTANDO SCRIPT PARA SINCRONIZAR APENAS AUTORES DE PROPOSIÇÕES (EM LOTES) ---")
    asyncio.run(main())
    logging.info("\n--- PROCESSO FINALIZADO ---")