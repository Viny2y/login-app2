from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def add_role_column():
    # Conectar ao banco de dados
    conn = engine.connect()
    
    try:
        # Adicionar a coluna role com valor padrão 'morador'
        conn.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'morador'")
        print("Coluna 'role' adicionada com sucesso!")
    except Exception as e:
        print(f"Erro ao adicionar coluna: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_role_column() 