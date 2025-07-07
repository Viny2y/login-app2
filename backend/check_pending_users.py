from database import SessionLocal
from models import User

def check_pending_users():
    db = SessionLocal()
    try:
        # Buscar usuários pendentes
        pending_users = db.query(User).filter(User.admin_approved == False).all()
        
        print("=== USUÁRIOS PENDENTES DE APROVAÇÃO ===")
        if not pending_users:
            print("Nenhum usuário pendente encontrado.")
        else:
            for user in pending_users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Email verificado: {user.email_verified}")
                print(f"Aprovado pelo admin: {user.admin_approved}")
                print(f"Data de criação: {user.created_at}")
                print("-" * 40)
        
        # Mostrar total de usuários
        total_users = db.query(User).count()
        print(f"\nTotal de usuários no sistema: {total_users}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_pending_users() 