from sqlalchemy import create_engine, text

# Configuração do banco de dados
DATABASE_URL = "sqlite:///../backend/database.db"
engine = create_engine(DATABASE_URL)

def execute_migration():
    with engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS users;"))
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR UNIQUE NOT NULL,
                    name VARCHAR,
                    age INTEGER,
                    birth_date DATETIME,
                    rg VARCHAR,
                    cpf VARCHAR,
                    gender VARCHAR,
                    color VARCHAR,
                    profile_picture VARCHAR,
                    phone VARCHAR,
                    hashed_password VARCHAR NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    role VARCHAR DEFAULT 'morador',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                );
            """))
            print("Tabela users criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabela: {str(e)}")

if __name__ == "__main__":
    execute_migration() 