import requests
import json

def test_pending_users_api():
    # Primeiro, fazer login para obter um token válido
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
            print(f"Token: {token[:50]}...")
            
            # Testar a API de usuários pendentes
            headers = {"Authorization": f"Bearer {token}"}
            pending_response = requests.get("http://127.0.0.1:8000/admin/pending-users", headers=headers)
            
            print(f"\n📊 Status da API de usuários pendentes: {pending_response.status_code}")
            
            if pending_response.status_code == 200:
                pending_users = pending_response.json()
                print(f"✅ Usuários pendentes encontrados: {len(pending_users)}")
                
                for user in pending_users:
                    print(f"  - ID: {user['id']}")
                    print(f"    Email: {user['email']}")
                    print(f"    Nome: {user['nome']}")
                    print(f"    Email verificado: {user['email_verified']}")
                    print(f"    Aprovado pelo admin: {user['admin_approved']}")
                    print(f"    Data de criação: {user['created_at']}")
                    print("    ---")
            else:
                print(f"❌ Erro na API: {pending_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_pending_users_api() 