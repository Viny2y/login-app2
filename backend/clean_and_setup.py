import os
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import models
from auth import get_password_hash
from datetime import datetime, timedelta

def clean_and_setup():
    # Remover banco existente
    if os.path.exists("database.db"):
        print("Removendo banco de dados existente...")
        os.remove("database.db")
    
    # Criar novo banco de dados
    print("Criando novo banco de dados...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    models.Base.metadata.create_all(bind=engine)
    
    # Criar usuários
    print("Criando usuários...")
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Criar usuário admin
        admin = models.User(
            email="keviny@gmail.com",
            nome="Kevin Admin",
            hashed_password=get_password_hash("123456"),
            role=models.UserRole.ADMIN,
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        
        # Criar usuário morador
        morador = models.User(
            email="user@gmail.com",
            nome="João Morador",
            hashed_password=get_password_hash("123456"),
            role=models.UserRole.MORADOR,
            is_admin=False,
            is_active=True
        )
        db.add(morador)
        
        db.commit()
        print("Usuários criados com sucesso!")
        
        # Criar apenas 2 solicitações reais
        print("Criando solicitações de aluguel...")
        
        aluguel1 = models.Aluguel(
            user_id=morador.id,
            comodo="Salão de Festas",
            data=datetime.now() + timedelta(days=5),
            horario="15:00",
            duracao=2,
            motivo="Aniversário da minha filha",
            status="pendente",
            created_at=datetime.now() - timedelta(days=1)
        )
        db.add(aluguel1)
        
        aluguel2 = models.Aluguel(
            user_id=morador.id,
            comodo="Academia",
            data=datetime.now() + timedelta(days=3),
            horario="19:00",
            duracao=1,
            motivo="Treino de musculação",
            status="pendente",
            created_at=datetime.now() - timedelta(hours=6)
        )
        db.add(aluguel2)
        
        # Criar alguns logs de login
        print("Criando logs de atividade...")
        
        log1 = models.ActivityLog(
            user_id=admin.id,
            action="login",
            details="Login realizado com sucesso",
            ip_address="192.168.1.100",
            created_at=datetime.now() - timedelta(hours=2)
        )
        db.add(log1)
        
        log2 = models.ActivityLog(
            user_id=morador.id,
            action="login",
            details="Login realizado com sucesso",
            ip_address="192.168.1.101",
            created_at=datetime.now() - timedelta(hours=1)
        )
        db.add(log2)
        
        log3 = models.ActivityLog(
            user_id=morador.id,
            action="create_request",
            details="Solicitação de aluguel criada",
            ip_address="192.168.1.101",
            created_at=datetime.now() - timedelta(hours=6)
        )
        db.add(log3)

        db.commit()
        print("Dados criados com sucesso!")
        
        # Mostrar estatísticas
        total_users = db.query(models.User).count()
        active_users = db.query(models.User).filter(models.User.is_active == True).count()
        total_logs = db.query(models.ActivityLog).count()
        pending_requests = db.query(models.Aluguel).filter(models.Aluguel.status == "pendente").count()
        total_requests = db.query(models.Aluguel).count()
        
        print("\n=== ESTATÍSTICAS ===")
        print(f"Total de usuários: {total_users}")
        print(f"Usuários ativos: {active_users}")
        print(f"Total de logs: {total_logs}")
        print(f"Total de solicitações: {total_requests}")
        print(f"Solicitações pendentes: {pending_requests}")
        
        print("\n=== CREDENCIAIS ===")
        print("Admin: keviny@gmail.com / 123456")
        print("Morador: user@gmail.com / 123456")
        
    except Exception as e:
        print(f"Erro ao configurar banco: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_setup() 