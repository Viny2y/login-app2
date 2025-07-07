from database import SessionLocal
from models import ActivityLog
from datetime import datetime

def clean_old_logs():
    db = SessionLocal()
    try:
        # Deletar todos os logs antigos
        db.query(ActivityLog).delete()
        db.commit()
        print("Todos os logs antigos foram removidos!")
        
        # Criar um log de teste com a data correta
        test_log = ActivityLog(
            user_id=None,
            action="system",
            details="Logs antigos removidos - sistema reiniciado",
            ip_address="127.0.0.1",
            created_at=datetime.now()
        )
        db.add(test_log)
        db.commit()
        print("Log de teste criado com data correta!")
        
    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_old_logs() 