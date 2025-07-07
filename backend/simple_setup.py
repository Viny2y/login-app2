from database import SessionLocal
from models import User, UserRole, ActivityLog, Aluguel
from auth import get_password_hash
from datetime import datetime, timedelta

def simple_setup():
    db = SessionLocal()
    try:
        # Limpar dados existentes
        print("Limpando dados existentes...")
        db.query(Aluguel).delete()
        db.query(ActivityLog).delete()
        db.query(User).delete()
        db.commit()
        
        # Criar usuário admin
        admin = User(
            email="keviny@gmail.com",
            nome="Kevin Admin",
            hashed_password=get_password_hash("123456"),
            role=UserRole.ADMIN,
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        
        # Criar usuário morador
        morador = User(
            email="user@gmail.com",
            nome="João Morador",
            hashed_password=get_password_hash("123456"),
            role=UserRole.MORADOR,
            is_admin=False,
            is_active=True
        )
        db.add(morador)
        
        db.commit()
        print("Usuários criados com sucesso!")
        
        # Criar apenas 2 solicitações
        print("Criando 2 solicitações...")
        
        aluguel1 = Aluguel(
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
        
        aluguel2 = Aluguel(
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
        
        # Criar alguns logs
        print("Criando logs...")
        
        log1 = ActivityLog(
            user_id=admin.id,
            action="login",
            details="Login realizado com sucesso",
            ip_address="192.168.1.100",
            created_at=datetime.now() - timedelta(hours=2)
        )
        db.add(log1)
        
        log2 = ActivityLog(
            user_id=morador.id,
            action="login",
            details="Login realizado com sucesso",
            ip_address="192.168.1.101",
            created_at=datetime.now() - timedelta(hours=1)
        )
        db.add(log2)

        db.commit()
        print("Dados criados com sucesso!")
        
        # Estatísticas
        total_users = db.query(User).count()
        total_logs = db.query(ActivityLog).count()
        total_requests = db.query(Aluguel).count()
        pending_requests = db.query(Aluguel).filter(Aluguel.status == "pendente").count()
        
        print(f"\n=== ESTATÍSTICAS ===")
        print(f"Total de usuários: {total_users}")
        print(f"Total de logs: {total_logs}")
        print(f"Total de solicitações: {total_requests}")
        print(f"Solicitações pendentes: {pending_requests}")
        
        print(f"\n=== CREDENCIAIS ===")
        print("Admin: keviny@gmail.com / 123456")
        print("Morador: user@gmail.com / 123456")
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simple_setup() 