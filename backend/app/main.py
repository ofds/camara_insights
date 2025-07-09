# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Importe o agendador e os roteadores da API
from app.core.scheduler import start_scheduler
from app.api.v1 import deputados, proposicoes, partidos, orgaos, eventos, votacoes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ser executado na inicialização
    print("--- Aplicação iniciando ---")
    start_scheduler()
    yield
    # Código a ser executado no encerramento (não faremos nada aqui por enquanto)
    print("--- Aplicação encerrando ---")


app = FastAPI(
    title="Câmara Insights API",
    description="Uma API para coletar, processar e analisar dados da Câmara dos Deputados do Brasil.",
    version="0.1.0",
    lifespan=lifespan # Adiciona o gerenciador de ciclo de vida
)

# Inclua os roteadores
app.include_router(deputados.router, prefix="/api/v1", tags=["Deputados"])
app.include_router(proposicoes.router, prefix="/api/v1", tags=["Proposições"])
app.include_router(partidos.router, prefix="/api/v1", tags=["Partidos"])
app.include_router(orgaos.router, prefix="/api/v1", tags=["Órgãos"])
app.include_router(eventos.router, prefix="/api/v1", tags=["Eventos"])
app.include_router(votacoes.router, prefix="/api/v1", tags=["Votações"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Câmara Insights!"}

@app.get("/health-check")
def health_check():
    return {"status": "ok"}