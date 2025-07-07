from database import SessionLocal
from models import User, Taxa
from datetime import datetime, timedelta

def create_taxas():
    db = SessionLocal()
    try:
        # Buscar o usuário morador
        morador = db.query(User).filter(User.email == "user@gmail.com").first()
        if not morador:
            print("Usuário morador não encontrado!")
            return
        
        # Limpar taxas existentes
        db.query(Taxa).filter(Taxa.morador_id == morador.id).delete()
        
        # Taxa de Maio - OK (paga)
        taxa_maio = Taxa(
            morador_id=morador.id,
            mes=5,
            ano=2025,
            valor=150.00,
            status="Pago",
            data_vencimento=datetime(2025, 5, 10),
            comprovante_path="uploads/comprovantes/maio_2025.pdf"
        )
        db.add(taxa_maio)
        
        # Taxa de Junho - Pendente
        taxa_junho = Taxa(
            morador_id=morador.id,
            mes=6,
            ano=2025,
            valor=150.00,
            status="Pendente",
            data_vencimento=datetime(2025, 6, 10)
        )
        db.add(taxa_junho)
        
        db.commit()
        print("Taxas criadas com sucesso!")
        print("Maio: Pago")
        print("Junho: Pendente")
        
    except Exception as e:
        print(f"Erro ao criar taxas: {str(e)}")
        db.rollback()
    finally:
        db.close()

def criar_taxas_para_usuario(email):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Usuário {email} não encontrado!")
        return
    meses = [datetime.now().month, (datetime.now().month % 12) + 1]
    ano_atual = datetime.now().year
    valor_taxa = 150.00
    for i, mes in enumerate(meses):
        data_venc = datetime(ano_atual, mes, 10)
        status = "Pendente" if i == 1 else "Pago"
        taxa = Taxa(
            morador_id=user.id,
            mes=mes,
            ano=ano_atual,
            valor=valor_taxa,
            status=status,
            data_vencimento=data_venc,
            comprovante_path=None if status == "Pendente" else "uploads/comprovantes/maio_2025.pdf"
        )
        db.add(taxa)
    db.commit()
    print(f"Taxas criadas para {email}!")
    db.close()

if __name__ == "__main__":
    create_taxas()
    criar_taxas_para_usuario("keviny11felix@gmail.com") 