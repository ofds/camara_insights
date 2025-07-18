import logging

# camara_insights/scripts/create_database.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infra.db.session import engine
from app.infra.db.models.referencias import Base as ReferenciasBase
from app.infra.db.models.entidades import Base as EntidadesBase
from app.infra.db.models.ai_data import Base as AIDataBase # Adicione esta linha

def create_database():
    logging.info("Criando tabelas de referência...")
    ReferenciasBase.metadata.create_all(bind=engine)
    logging.info("Tabelas de referência criadas.")
    
    logging.info("Criando tabelas de entidade...")
    EntidadesBase.metadata.create_all(bind=engine)
    logging.info("Tabelas de entidade criadas.")
    
    logging.info("Criando tabelas de dados de IA...")
    AIDataBase.metadata.create_all(bind=engine) # Adicione esta linha
    logging.info("Tabelas de IA criadas com sucesso!")

if __name__ == "__main__":
    create_database()