from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
from passlib.context import CryptContext
import sys
import os

# Adicionar o diretório pai ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import UserRole

# Configuração do banco de dados
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuração de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def recreate_users():
    db = SessionLocal()
    try:
        # Criar usuário administrador
        db.execute(text("""
            INSERT INTO users (
                email, hashed_password, is_active, is_admin, role, created_at
            ) VALUES (
                'keviny@gmail.com',
                :password,
                TRUE,
                TRUE,
                :role,
                :created_at
            )
        """), {
            "password": get_password_hash("123456"),
            "role": UserRole.ADMIN.value,
            "created_at": datetime.now(UTC)
        })

        # Criar usuário morador
        db.execute(text("""
            INSERT INTO users (
                email, hashed_password, is_active, is_admin, role, created_at
            ) VALUES (
                'user@gmail.com',
                :password,
                TRUE,
                FALSE,
                :role,
                :created_at
            )
        """), {
            "password": get_password_hash("123456"),
            "role": UserRole.MORADOR.value,
            "created_at": datetime.now(UTC)
        })

        db.commit()
        print("Usuários criados com sucesso!")
        print("Admin - Email: keviny@gmail.com, Senha: 123456")
        print("Morador - Email: user@gmail.com, Senha: 123456")
        
    except Exception as e:
        print(f"Erro ao recriar usuários: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_users() 