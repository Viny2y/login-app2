from database import SessionLocal
from models import User, ActivityLog, Aluguel
from sqlalchemy.orm import joinedload

def test_admin_data():
    db = SessionLocal()
    try:
        print("=== TESTE DOS DADOS ADMINISTRATIVOS ===\n")
        
        # Verificar usuários
        print("1. USUÁRIOS:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.nome} ({user.email}) - Role: {user.role} - Ativo: {user.is_active}")
        print()
        
        # Verificar logs
        print("2. LOGS DE ATIVIDADE:")
        logs = db.query(ActivityLog).options(joinedload(ActivityLog.user)).order_by(ActivityLog.created_at.desc()).limit(5).all()
        for log in logs:
            user_name = log.user.nome if log.user else "Sistema"
            print(f"   - {log.created_at.strftime('%d/%m/%Y %H:%M')} | {user_name} | {log.action} | {log.details}")
        print()
        
        # Verificar solicitações
        print("3. SOLICITAÇÕES DE ALUGUEL:")
        alugueis = db.query(Aluguel).options(joinedload(Aluguel.user)).order_by(Aluguel.created_at.desc()).all()
        for aluguel in alugueis:
            user_name = aluguel.user.nome if aluguel.user else "N/A"
            print(f"   - {aluguel.created_at.strftime('%d/%m/%Y')} | {user_name} | {aluguel.comodo} | Status: {aluguel.status}")
        print()
        
        # Estatísticas
        print("4. ESTATÍSTICAS:")
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_logs = db.query(ActivityLog).count()
        pending_requests = db.query(Aluguel).filter(Aluguel.status == "pendente").count()
        
        print(f"   - Total de usuários: {total_users}")
        print(f"   - Usuários ativos: {active_users}")
        print(f"   - Total de logs: {total_logs}")
        print(f"   - Solicitações pendentes: {pending_requests}")
        
    except Exception as e:
        print(f"Erro no teste: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_data() 