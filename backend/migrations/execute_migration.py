import sqlite3
import os

def execute_migration():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Criar tabela users
        create_table_path = os.path.join(os.path.dirname(__file__), "create_tables.sql")
        with open(create_table_path, 'r') as file:
            create_table_sql = file.read()
        cursor.executescript(create_table_sql)
        
        conn.commit()
        print("Migração executada com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    execute_migration() 