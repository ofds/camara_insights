# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Importa a nova função mestre do nosso serviço de automação
from app.services.automation_service import run_daily_update_task

scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")

def start_scheduler():
    """
    Adiciona as tarefas ao agendador e o inicia.
    """
    print("Configurando tarefas agendadas...")
    
    # Adiciona a tarefa de atualização completa para rodar 2 vezes ao dia
    scheduler.add_job(
        run_daily_update_task, 
        'cron', 
        hour='9,18', # Roda às 9h e às 18h
        minute=0,
        id='daily_update_task', 
        replace_existing=True
    )
    
    print("Agendador iniciado com as tarefas configuradas.")
    scheduler.start()