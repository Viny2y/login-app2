from database import engine, SessionLocal
from models import Base, EmailVerification
from sqlalchemy import text

def create_email_verification_table():
    """Cria a tabela de verificação de email"""
    try:
        # Criar a tabela
        EmailVerification.__table__.create(engine, checkfirst=True)
        print("✅ Tabela email_verifications criada com sucesso!")
        
        # Verificar se a tabela foi criada
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='email_verifications'"))
            if result.fetchone():
                print("✅ Tabela email_verifications existe no banco de dados")
            else:
                print("❌ Erro: Tabela não foi criada")
                
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")

def add_user_fields():
    """Adiciona campos necessários na tabela users"""
    try:
        with engine.connect() as conn:
            # Verificar se os campos já existem
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Adicionar campo email_verified se não existir
            if 'email_verified' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE"))
                print("✅ Campo email_verified adicionado")
            
            # Adicionar campo admin_approved se não existir
            if 'admin_approved' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN admin_approved BOOLEAN DEFAULT FALSE"))
                print("✅ Campo admin_approved adicionado")
            
            conn.commit()
            print("✅ Campos adicionados com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar campos: {e}")

def update_existing_users():
    """Atualiza usuários existentes para serem aprovados"""
    try:
        db = SessionLocal()
        
        # Atualizar todos os usuários existentes para serem aprovados
        db.execute(text("UPDATE users SET email_verified = TRUE, admin_approved = TRUE, is_active = TRUE"))
        db.commit()
        
        print("✅ Usuários existentes atualizados para serem aprovados")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar usuários: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Configurando sistema de verificação por email...")
    
    # Criar tabela de verificação
    create_email_verification_table()
    
    # Adicionar campos na tabela users
    add_user_fields()
    
    # Atualizar usuários existentes
    update_existing_users()
    
    print("✅ Configuração concluída!")
    print("\n📧 IMPORTANTE: Configure suas credenciais de email no arquivo email_config.py")
    print("   - MAIL_USERNAME: seu email Gmail")
    print("   - MAIL_PASSWORD: senha do app Gmail")
    print("   - MAIL_FROM: seu email Gmail") 