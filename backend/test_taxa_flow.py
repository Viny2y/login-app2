from database import SessionLocal
from models import User, Taxa
from datetime import datetime

def test_taxa_flow():
    db = SessionLocal()
    try:
        # Buscar o usuário morador
        morador = db.query(User).filter(User.email == "user@gmail.com").first()
        if not morador:
            print("Usuário morador não encontrado!")
            return
        
        print(f"Usuário morador: {morador.email} (ID: {morador.id})")
        
        # Verificar taxas atuais
        taxas = db.query(Taxa).filter(Taxa.morador_id == morador.id).all()
        print(f"\nTaxas atuais:")
        for taxa in taxas:
            print(f"- Taxa {taxa.mes}/{taxa.ano}: {taxa.status}")
        
        # Simular upload de comprovante (mudar status para "Em Análise")
        taxa_pendente = db.query(Taxa).filter(
            Taxa.morador_id == morador.id,
            Taxa.status == "Pendente"
        ).first()
        
        if taxa_pendente:
            print(f"\nSimulando upload de comprovante para taxa {taxa_pendente.mes}/{taxa_pendente.ano}")
            taxa_pendente.status = "Em Análise"
            taxa_pendente.comprovante_path = "uploads/comprovantes/teste.pdf"
            db.commit()
            print(f"Status alterado para: {taxa_pendente.status}")
        
        # Simular aprovação pelo admin
        taxa_analise = db.query(Taxa).filter(
            Taxa.morador_id == morador.id,
            Taxa.status == "Em Análise"
        ).first()
        
        if taxa_analise:
            print(f"\nSimulando aprovação pelo admin para taxa {taxa_analise.mes}/{taxa_analise.ano}")
            taxa_analise.status = "Pago"
            db.commit()
            print(f"Status alterado para: {taxa_analise.status}")
        
        # Verificar taxas finais
        taxas_finais = db.query(Taxa).filter(Taxa.morador_id == morador.id).all()
        print(f"\nTaxas após simulação:")
        for taxa in taxas_finais:
            print(f"- Taxa {taxa.mes}/{taxa.ano}: {taxa.status}")
        
        print("\n✅ Fluxo de taxas funcionando corretamente!")
        
    except Exception as e:
        print(f"Erro no teste: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_taxa_flow() 