import logging
# scripts/score_propositions.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infra.db.session import SessionLocal
from app.infra.db.crud.ai_data import get_unscored_propositions
from app.services.scoring_service import analyze_and_score_propositions
from app.core.rate_limiter import RateLimiter

async def process_backlog():
    """
    Processa o backlog de proposições em lotes, utilizando um rate limiter
    dinâmico para maximizar o uso da API.
    """
    # Usamos 18 em vez de 20 para ter uma margem de segurança.
    limiter = RateLimiter(requests_per_minute=18)
    
    batch_number = 1
    while True:
        db = SessionLocal()
        try:
            # Tenta buscar um lote completo de 10 proposições
            logging.info(f"\n--- Lote #{batch_number}: Buscando até 10 proposições... ---")
            propositions_to_score = get_unscored_propositions(db, limit=10)

            if not propositions_to_score:
                logging.info("\nParabéns! Todo o backlog de proposições foi analisado.")
                break

            logging.info(f"Encontradas {len(propositions_to_score)} proposições. Iniciando processamento concorrente...")

            # --- Lógica de Processamento em Lote ---
            
            # Criamos uma função interna (worker) para cada tarefa
            async def task_worker(prop):
                # Cada worker primeiro adquire permissão do limiter
                await limiter.acquire()
                logging.info(f"Analisando proposição ID: {prop.id}...")
                # Passamos uma lista com um único item para a função de análise
                await analyze_and_score_propositions(db, [prop])

            # Criamos uma lista de tarefas, uma para cada proposição no lote
            tasks = [task_worker(prop) for prop in propositions_to_score]
            
            # Executamos todas as tarefas do lote concorrentemente
            await asyncio.gather(*tasks)
            
            logging.info(f"--- Lote #{batch_number} finalizado. ---")
            batch_number += 1

        except Exception as e:
            logging.warning(f"Ocorreu um erro inesperado: {e}. Aguardando 1 minuto antes de continuar.")
            await asyncio.sleep(60)
        finally:
            db.close()

if __name__ == "__main__":
    logging.info("--- INICIANDO WORKER DE ANÁLISE DE BACKLOG (COM LOTES OTIMIZADOS) ---")
    logging.info("Este script irá rodar continuamente até que todas as proposições sejam analisadas.")
    logging.info("Pressione CTRL+C para parar a qualquer momento.")
    asyncio.run(process_backlog())
    logging.info("--- WORKER FINALIZADO ---")