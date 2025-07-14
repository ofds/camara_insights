import asyncio
from prefect import task, flow

# To simulate real async work (like I/O), we add a small sleep.
# In your actual code, these would be your httpx or database calls.

@task(retries=3, retry_delay_seconds=10)
async def sync_referencias_task():
    """Esta tarefa executa a lógica de sync_referencias.py"""
    print("Iniciando a sincronização de tabelas de referência...")
    await asyncio.sleep(0.1)
    print("Tabelas de referência sincronizadas.")

@task(retries=2, retry_delay_seconds=120)
async def sync_entidades_principais_task(ano_inicio: int = 2023):
    """Esta tarefa executa a lógica de sync_all.py"""
    print(f"Iniciando a sincronização de entidades principais desde {ano_inicio}...")
    await asyncio.sleep(0.2) # Make it slightly longer to see the dependency work
    print("Entidades principais sincronizadas.")

@task
async def score_propositions_task():
    """Esta tarefa executa a lógica de score_propositions.py"""
    print("Iniciando o enriquecimento com IA...")
    await asyncio.sleep(0.1)
    print("Enriquecimento com IA concluído.")


@flow(name="ETL Câmara Insights V1", log_prints=True)
async def etl_camara_insights(ano: int = 2024):
    print("🚀 Iniciando o fluxo de ETL principal...")

    # Submit the main task
    task_entidades_future = sync_entidades_principais_task.submit(ano_inicio=ano)

    # Submit the scoring task with an explicit dependency on the previous task
    score_propositions_task.submit(
        wait_for=[task_entidades_future]
    )

    # Submit the parallel task. It will run concurrently with the others.
    sync_referencias_task.submit()

    # --- THE FIX ---
    # We do NOT need to await anything here. The flow will automatically
    # wait for all of its submitted child tasks to complete.
    
    print("✅ Todas as tarefas foram submetidas. O fluxo irá aguardar a conclusão.")


if __name__ == "__main__":
    # This line is all you need. asyncio.run() will not exit until the
    # etl_camara_insights coroutine and all its child tasks are complete.
    asyncio.run(etl_camara_insights(ano=2023))