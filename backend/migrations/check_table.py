import sqlite3
import os

def check_table_structure():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Obter informações da tabela
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\nEstrutura da tabela users:")
        print("-" * 50)
        for col in columns:
            print(f"Coluna: {col[1]}")
            print(f"Tipo: {col[2]}")
            print(f"NotNull: {col[3]}")
            print(f"Valor Padrão: {col[4]}")
            print(f"PK: {col[5]}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Erro ao verificar estrutura: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_structure() 