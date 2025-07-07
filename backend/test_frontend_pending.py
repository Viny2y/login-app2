import requests
import json

def test_frontend_pending_users():
    # Simular o que o frontend faz
    print("🔍 Testando carregamento de usuários pendentes...")
    
    # 1. Fazer login como admin
    login_data = {
        "username": "keviny@gmail.com",
        "password": "123456"
    }
    
    try:
        # Fazer login
        login_response = requests.post("http://127.0.0.1:8000/token", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data["access_token"]
            
            print("✅ Login realizado com sucesso!")
            
            # 2. Testar a API de usuários pendentes (como o frontend faz)
            headers = {"Authorization": f"Bearer {token}"}
            pending_response = requests.get("http://127.0.0.1:8000/admin/pending-users", headers=headers)
            
            print(f"📊 Status da API: {pending_response.status_code}")
            
            if pending_response.status_code == 200:
                pending_users = pending_response.json()
                print(f"✅ Usuários pendentes encontrados: {len(pending_users)}")
                
                # 3. Simular o que o displayPendingUsers faria
                if len(pending_users) == 0:
                    print("📋 Tabela seria preenchida com: 'Nenhum usuário pendente'")
                else:
                    print("📋 Tabela seria preenchida com:")
                    for user in pending_users:
                        print(f"  - Email: {user['email']}")
                        print(f"    Nome: {user['nome']}")
                        print(f"    Data: {user['created_at']}")
                        print(f"    Status: Pendente")
                        print(f"    Botões: Aprovar | Rejeitar")
                        print("    ---")
                
                # 4. Simular updatePendingCount
                print(f"🔢 Badge seria atualizado para: {len(pending_users)}")
                
            else:
                print(f"❌ Erro na API: {pending_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_frontend_pending_users() 