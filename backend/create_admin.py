from database import SessionLocal
from models import User, UserRole
from auth import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Verifica se já existe um admin
        admin = db.query(User).filter(User.email == "keviny@gmail.com").first()
        if not admin:
            # Cria o usuário admin
            admin_user = User(
                email="keviny@gmail.com",
                nome="Kevin Admin",
                hashed_password=get_password_hash("123456"),
                role=UserRole.ADMIN,
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Usuário admin criado com sucesso!")
            print("Email: keviny@gmail.com")
            print("Senha: 123456")
            print("Role: ADMIN")
        else:
            print("Usuário admin já existe!")
            print("Email: keviny@gmail.com")
            print("Senha: 123456")
            print("Role: ADMIN")

    except Exception as e:
        print(f"Erro ao criar admin: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 