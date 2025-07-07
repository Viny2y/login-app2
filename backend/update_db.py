from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import os

def update_database():
    # Criar engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Conectar ao banco de dados
    with engine.connect() as connection:
        try:
            # Criar tabela temporária com a nova estrutura
            print("Criando tabela temporária...")
            connection.execute(text("""
                CREATE TABLE users_temp (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE,
                    nome TEXT,
                    age INTEGER,
                    birth_date DATETIME,
                    rg TEXT,
                    cpf TEXT,
                    gender TEXT,
                    color TEXT,
                    phone TEXT,
                    hashed_password TEXT,
                    is_active BOOLEAN,
                    is_admin BOOLEAN,
                    role TEXT,
                    created_at DATETIME,
                    last_login DATETIME,
                    foto_perfil TEXT,
                    idade INTEGER,
                    data_nascimento DATE,
                    sexo TEXT,
                    cor TEXT
                )
            """))
            
            # Copiar dados da tabela antiga para a nova
            print("Copiando dados...")
            connection.execute(text("""
                INSERT INTO users_temp (
                    id, email, hashed_password, is_active, is_admin, role, created_at, last_login
                )
                SELECT 
                    id, email, hashed_password, is_active, is_admin, role, created_at, last_login
                FROM users
            """))
            
            # Remover tabela antiga
            print("Removendo tabela antiga...")
            connection.execute(text("DROP TABLE users"))
            
            # Renomear tabela temporária
            print("Renomeando tabela...")
            connection.execute(text("ALTER TABLE users_temp RENAME TO users"))
            
            # Criar índices
            print("Criando índices...")
            connection.execute(text("CREATE INDEX ix_users_email ON users(email)"))
            
            connection.commit()
            print("Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"Erro durante a migração: {str(e)}")
            connection.rollback()
            raise e

if __name__ == "__main__":
    # Fazer backup do banco de dados
    if os.path.exists("backend/database.db"):
        print("Fazendo backup do banco de dados...")
        os.rename("backend/database.db", "backend/database.db.backup")
    
    update_database() 