from database import SessionLocal
from models import User, UserRole, ActivityLog, Aluguel
from auth import get_password_hash
from datetime import datetime, timedelta
import random

def create_test_data():
    db = SessionLocal()
    try:
        # Criar usuário morador se não existir
        morador = db.query(User).filter(User.email == "user@gmail.com").first()
        if not morador:
            morador = User(
                email="user@gmail.com",
                nome="João Morador",
                hashed_password=get_password_hash("123456"),
                role=UserRole.MORADOR,
                is_admin=False,
                is_active=True
            )
            db.add(morador)
            print("Usuário morador criado: user@gmail.com / 123456")

        # Verificar se admin existe
        admin = db.query(User).filter(User.email == "keviny@gmail.com").first()
        if not admin:
            admin = User(
                email="keviny@gmail.com",
                nome="Kevin Admin",
                hashed_password=get_password_hash("123456"),
                role=UserRole.ADMIN,
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            print("Usuário admin criado: keviny@gmail.com / 123456")

        db.commit()

        # Criar logs de atividade
        print("Criando logs de atividade...")
        
        # Logs de login
        for i in range(10):
            log = ActivityLog(
                user_id=random.choice([admin.id, morador.id]),
                action="login",
                details="Login realizado com sucesso",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            db.add(log)

        # Logs de outras atividades
        activities = [
            ("update_profile", "Perfil atualizado"),
            ("create_request", "Solicitação de aluguel criada"),
            ("view_notifications", "Visualizou notificações"),
            ("upload_file", "Arquivo enviado")
        ]

        for i in range(15):
            activity = random.choice(activities)
            log = ActivityLog(
                user_id=random.choice([admin.id, morador.id]),
                action=activity[0],
                details=activity[1],
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.add(log)

        # Criar solicitações de aluguel
        print("Criando solicitações de aluguel...")
        
        comodos = ["Salão de Festas", "Academia", "Sala de Reuniões", "Churrasqueira"]
        motivos = ["Aniversário", "Reunião familiar", "Evento corporativo", "Festa"]
        status_options = ["pendente", "aprovado", "rejeitado"]
        
        for i in range(8):
            aluguel = Aluguel(
                user_id=morador.id,
                comodo=random.choice(comodos),
                data=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                horario=f"{random.randint(8, 20)}:00",
                duracao=random.randint(1, 4),
                motivo=random.choice(motivos),
                status=random.choice(status_options),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7))
            )
            db.add(aluguel)

        db.commit()
        print("Dados de teste criados com sucesso!")
        print(f"Total de usuários: {db.query(User).count()}")
        print(f"Total de logs: {db.query(ActivityLog).count()}")
        print(f"Total de solicitações: {db.query(Aluguel).count()}")

    except Exception as e:
        print(f"Erro ao criar dados de teste: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 