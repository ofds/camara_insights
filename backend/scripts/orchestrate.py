# backend/scripts/orchestrate.py
import asyncio
import sys
from datetime import date
from prefect import task, flow

# This block for Windows is still necessary and correct
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# --- Core Daily Flow Tasks ---

@task
async def sync_recent_propositions_task(target_date: date):
    """
    Simulates the logic from daily_priority_sync.py to fetch recent propositions.
    """
    print(f"🚀 Iniciando a sincronização de proposições para a data: {target_date}...")
    await asyncio.sleep(2)
    print(f"✅ Proposições de {target_date} sincronizadas com sucesso.")
    return True

@task
async def score_new_propositions_task():
    """
    Simulates the AI scoring logic from BacklogProcessor or score_propositions.py.
    """
    print("🧠 Iniciando o processo de AI scoring para novas proposições...")
    await asyncio.sleep(3)
    print("✅ Novas proposições analisadas e pontuadas.")
    return True

# --- Other Tasks (unchanged) ---

@task(retries=2, retry_delay_seconds=120, name="sync_all_main_entities")
async def sync_all_entities_task(start_year: int):
    print(f"⏳ Iniciando a sincronização histórica completa de entidades principais desde {start_year}...")
    await asyncio.sleep(5)
    print(f"✅ Sincronização histórica de entidades concluída.")
    return True

@task(retries=3, retry_delay_seconds=10, name="sync_reference_tables")
async def sync_referencias_task():
    print("📚 Iniciando a sincronização de tabelas de referência...")
    await asyncio.sleep(1)
    print("✅ Tabelas de referência sincronizadas.")

@task(retries=1, retry_delay_seconds=300)
async def process_full_ai_backlog_task():
    print(" Processing o backlog completo de itens para análise de IA...")
    await asyncio.sleep(10)
    print("✅ Backlog de IA processado com sucesso.")
    return True


# --- Prefect Flows ---

@flow(name="Core Daily Sync", log_prints=True)
async def core_daily_flow(target_date: date = date.today()):
    """
    Fluxo leve e rápido para sincronização diária.
    --- MODIFIED FOR DEBUGGING: Tasks now run sequentially. ---
    """
    print("--- Iniciando Core Daily Flow ---")

    # Run tasks one after another instead of submitting them to the background.
    # This is less efficient but more stable on some Windows configurations.
    await sync_recent_propositions_task(target_date=target_date)
    await score_new_propositions_task()

    print("--- Core Daily Flow concluído. ---")


@flow(name="Full Historical Sync", log_prints=True)
async def full_historical_sync_flow(start_year: int = 2023):
    """
    Fluxo pesado para realizar a carga histórica completa de dados.
    """
    print("--- Iniciando Full Historical Sync Flow ---")
    
    # We can keep .submit() here for parallelism, as it's less likely to cause issues
    # when the tasks are not co-dependent in the same way.
    sync_all_entities_task.submit(start_year=start_year)
    sync_referencias_task.submit()

    print("--- Full Historical Sync Flow submetido. ---")


@flow(name="AI Backlog Processing", log_prints=True)
async def ai_backlog_processing_flow():
    """
    Fluxo para processar um grande volume de proposições que ainda não possuem
    análise de IA.
    """
    print("--- Iniciando AI Backlog Processing Flow ---")
    process_full_ai_backlog_task.submit()
    print("--- AI Backlog Processing Flow submetido. ---")


# --- Main Execution Block ---

if __name__ == "__main__":
    """
    This block is for creating a deployment when the script is run directly.
    """
    core_daily_flow.deploy(
        name="core-daily-deployment-py",
        work_pool_name="default-agent-pool",
        tags=["daily-sync", "python-defined"]
    )