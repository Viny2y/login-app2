from database import SessionLocal
from models import User, Taxa

def listar_taxas_todos_usuarios():
    db = SessionLocal()
    users = db.query(User).all()
    for user in users:
        print(f"Usuário: {user.email} (ID: {user.id})")
        taxas = db.query(Taxa).filter(Taxa.morador_id == user.id).all()
        if not taxas:
            print("  Nenhuma taxa encontrada")
        else:
            for taxa in taxas:
                print(f"  - {taxa.mes}/{taxa.ano}: {taxa.status} | Venc: {taxa.data_vencimento}")
    db.close()

if __name__ == "__main__":
    listar_taxas_todos_usuarios() 