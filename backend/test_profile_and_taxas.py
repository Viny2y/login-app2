import requests
import json

def test_profile_and_taxas():
    print("🔍 Testando perfil e taxas do morador...")
    
    # 1. Fazer login como morador
    login_data = {
        "username": "user@gmail.com",
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
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. Testar perfil do usuário
            print("\n📊 Testando perfil do usuário...")
            profile_response = requests.get("http://127.0.0.1:8000/users/me", headers=headers)
            
            print(f"Status do perfil: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"✅ Perfil carregado:")
                print(f"  - Nome: {profile_data.get('nome', 'N/A')}")
                print(f"  - Email: {profile_data.get('email', 'N/A')}")
                print(f"  - Role: {profile_data.get('role', 'N/A')}")
                print(f"  - Ativo: {profile_data.get('is_active', 'N/A')}")
                print(f"  - Foto: {profile_data.get('profile_picture', 'N/A')}")
            else:
                print(f"❌ Erro no perfil: {profile_response.text}")
            
            # 3. Testar taxas do usuário
            print("\n📊 Testando taxas do usuário...")
            taxas_response = requests.get("http://127.0.0.1:8000/taxas/", headers=headers)
            
            print(f"Status das taxas: {taxas_response.status_code}")
            
            if taxas_response.status_code == 200:
                taxas_data = taxas_response.json()
                print(f"✅ Taxas encontradas: {len(taxas_data)}")
                
                for taxa in taxas_data:
                    print(f"  - Taxa {taxa.get('mes')}/{taxa.get('ano')}: {taxa.get('status')}")
                    print(f"    Valor: R$ {taxa.get('valor')}")
                    print(f"    Vencimento: {taxa.get('data_vencimento')}")
                    print("    ---")
            else:
                print(f"❌ Erro nas taxas: {taxas_response.text}")
            
            # 4. Testar upload de comprovante (simular)
            print("\n📊 Testando endpoint de upload de comprovante...")
            upload_response = requests.get("http://127.0.0.1:8000/upload-comprovante", headers=headers)
            print(f"Status do upload: {upload_response.status_code}")
            if upload_response.status_code == 405:  # Method Not Allowed (esperado para GET)
                print("✅ Endpoint de upload existe (só aceita POST)")
            else:
                print(f"❌ Erro no endpoint de upload: {upload_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_profile_and_taxas() 