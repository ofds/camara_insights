# camara_insights/scripts/create_database.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infra.db.session import engine
from app.infra.db.models.referencias import Base as ReferenciasBase
from app.infra.db.models.entidades import Base as EntidadesBase # Adicionar esta linha

def create_database():
    print("Criando tabelas de referência...")
    ReferenciasBase.metadata.create_all(bind=engine)
    print("Tabelas de referência criadas.")
    
    print("Criando tabelas de entidade...")
    EntidadesBase.metadata.create_all(bind=engine) # Adicionar esta linha
    print("Tabelas de entidade criadas com sucesso!")

if __name__ == "__main__":
    create_database()