import os
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import models
from auth import get_password_hash
from datetime import datetime, timedelta
import random

def setup_database():
    # Remover banco existente se houver
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
        # Verificar se admin já existe
        admin = db.query(models.User).filter(models.User.email == "keviny@gmail.com").first()
        if not admin:
            admin = models.User(
                email="keviny@gmail.com",
                nome="Kevin Admin",
                hashed_password=get_password_hash("123456"),
                role=models.UserRole.ADMIN,
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            print("Usuário admin criado")
        else:
            print("Usuário admin já existe")
        
        # Verificar se morador já existe
        morador = db.query(models.User).filter(models.User.email == "user@gmail.com").first()
        if not morador:
            morador = models.User(
                email="user@gmail.com",
                nome="João Morador",
                hashed_password=get_password_hash("123456"),
                role=models.UserRole.MORADOR,
                is_admin=False,
                is_active=True
            )
            db.add(morador)
            print("Usuário morador criado")
        else:
            print("Usuário morador já existe")
        
        db.commit()
        print("Usuários verificados/criados com sucesso!")
        
        # Criar logs de atividade
        print("Criando logs de atividade...")
        
        # Logs de login
        for i in range(15):
            log = models.ActivityLog(
                user_id=random.choice([admin.id, morador.id]),
                action="login",
                details="Login realizado com sucesso",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                created_at=datetime.now() - timedelta(hours=random.randint(1, 72))
            )
            db.add(log)

        # Logs de outras atividades
        activities = [
            ("update_profile", "Perfil atualizado"),
            ("create_request", "Solicitação de aluguel criada"),
            ("view_notifications", "Visualizou notificações"),
            ("upload_file", "Arquivo enviado"),
            ("logout", "Logout realizado")
        ]

        for i in range(20):
            activity = random.choice(activities)
            log = models.ActivityLog(
                user_id=random.choice([admin.id, morador.id]),
                action=activity[0],
                details=activity[1],
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                created_at=datetime.now() - timedelta(hours=random.randint(1, 48))
            )
            db.add(log)

        # Criar solicitações de aluguel
        print("Criando solicitações de aluguel...")
        
        comodos = ["Salão de Festas", "Academia", "Sala de Reuniões", "Churrasqueira", "Piscina"]
        motivos = ["Aniversário", "Reunião familiar", "Evento corporativo", "Festa", "Treino"]
        
        # Criar apenas 2 solicitações reais
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

        db.commit()
        print("Dados de teste criados com sucesso!")
        
        # Mostrar estatísticas
        total_users = db.query(models.User).count()
        active_users = db.query(models.User).filter(models.User.is_active == True).count()
        total_logs = db.query(models.ActivityLog).count()
        pending_requests = db.query(models.Aluguel).filter(models.Aluguel.status == "pendente").count()
        
        print("\n=== ESTATÍSTICAS ===")
        print(f"Total de usuários: {total_users}")
        print(f"Usuários ativos: {active_users}")
        print(f"Total de logs: {total_logs}")
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
    setup_database() 