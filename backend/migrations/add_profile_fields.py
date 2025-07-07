from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração do banco de dados
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def execute_migration():
    # Criar uma sessão
    db = SessionLocal()
    
    try:
        # Adicionar novas colunas à tabela users
        db.execute("""
            ALTER TABLE users ADD COLUMN age INTEGER;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN birth_date DATETIME;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN rg VARCHAR;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN cpf VARCHAR;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN gender VARCHAR;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN color VARCHAR;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN profile_picture VARCHAR;
        """)
        
        db.execute("""
            ALTER TABLE users ADD COLUMN phone VARCHAR;
        """)
        
        # Criar tabela de aluguéis
        db.execute("""
            CREATE TABLE IF NOT EXISTS alugueis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                comodo VARCHAR NOT NULL,
                data DATETIME NOT NULL,
                horario VARCHAR NOT NULL,
                duracao INTEGER NOT NULL,
                motivo VARCHAR NOT NULL,
                status VARCHAR DEFAULT 'pendente',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # Commit das alterações
        db.commit()
        print("Migração executada com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    execute_migration() 