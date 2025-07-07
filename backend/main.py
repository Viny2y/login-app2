from datetime import timedelta
from typing import Annotated, Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from database import engine, get_db
import models
import schemas
import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
import shutil
from pathlib import Path
from fastapi.responses import FileResponse
from email_config import generate_verification_code, save_verification_code, send_verification_email, verify_code, cleanup_expired_codes

# Criar as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Painel de Login FastAPI", version="1.0.1")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens durante o desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configurar pasta para uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Montar pasta de uploads como estática
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

def log_activity(db: Session, user_id: Optional[int], action: str, details: str, ip_address: Optional[str] = None):
    log = models.ActivityLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address,
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email já registrado"
        )
    return auth.create_user(db=db, user=user)

@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se o usuário foi aprovado pelo admin
    if not user.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta ainda não foi aprovada pelo administrador. Aguarde a aprovação.",
        )
    
    # Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta foi desativada. Entre em contato com o administrador.",
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Atualizar último login
    user.last_login = datetime.now()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = auth.get_current_user(token, db)
    return user

@app.put("/users/me", response_model=schemas.User)
async def update_user_profile(
    user_update: schemas.UserProfileUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        user = auth.get_current_user(token, db)
        
        # Log dos dados recebidos
        print("DEBUG: Dados recebidos (raw):", user_update.dict())
        print("DEBUG: Tipos dos dados recebidos:", {
            field: type(value) for field, value in user_update.dict().items()
        })
        
        # Atualizar campos
        update_data = user_update.dict()
        
        # Log dos dados processados
        print("DEBUG: Dados processados (todos):", update_data)
        print("DEBUG: Todos os dados do schema:", user_update.dict())
        
        # Tratar campos vazios
        for field in ['nome', 'rg', 'cpf', 'gender', 'color', 'phone']:
            if field in update_data and (update_data[field] == '' or update_data[field] == 'null'):
                update_data[field] = None
        
        # Garantir que age seja um número inteiro
        if 'age' in update_data:
            try:
                if update_data['age'] is None or update_data['age'] == '' or update_data['age'] == 'null':
                    update_data['age'] = None
                else:
                    update_data['age'] = int(float(str(update_data['age'])))
            except (TypeError, ValueError) as e:
                print(f"DEBUG: Erro ao converter idade: {e}")
                update_data['age'] = None
        
        # Converter birth_date de string para datetime
        if 'birth_date' in update_data and update_data['birth_date']:
            try:
                update_data['birth_date'] = datetime.strptime(update_data['birth_date'], '%Y-%m-%d')
                print(f"DEBUG: birth_date convertido para: {update_data['birth_date']}")
            except (TypeError, ValueError) as e:
                print(f"DEBUG: Erro ao converter birth_date: {e}")
                update_data['birth_date'] = None
        
        # Log dos dados finais
        print("DEBUG: Dados finais a serem salvos:", update_data)
        print("DEBUG: Usuário antes da atualização:", {
            'id': user.id,
            'nome': user.nome,
            'age': user.age,
            'birth_date': user.birth_date,
            'rg': user.rg,
            'cpf': user.cpf,
            'gender': user.gender,
            'color': user.color
        })
        
        # Atualizar campos
        for field, value in update_data.items():
            if hasattr(user, field):
                old_value = getattr(user, field)
                setattr(user, field, value)
                print(f"DEBUG: Campo {field} atualizado de '{old_value}' para '{value}'")
            else:
                print(f"DEBUG: Campo {field} não existe no modelo User")
        
        print("DEBUG: Tentando fazer commit...")
        db.commit()
        print("DEBUG: Commit realizado com sucesso!")
        db.refresh(user)
        print("DEBUG: Usuário recarregado do banco")
        
        # Registrar atividade
        log_activity(
            db=db,
            user_id=user.id,
            action="update_profile",
            details="Perfil atualizado",
            ip_address=request.client.host if request else None
        )
        
        return user
    except Exception as e:
        print("DEBUG: Erro ao atualizar perfil:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/avisos/", response_model=List[schemas.Aviso])
async def read_avisos(
    skip: int = 0,
    limit: int = 50,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = auth.get_current_user(token, db)
    avisos = db.query(models.Aviso).offset(skip).limit(limit).all()
    return avisos

@app.post("/avisos/", response_model=schemas.Aviso)
async def create_aviso(
    aviso: schemas.AvisoCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = auth.get_current_user(token, db)
    db_aviso = models.Aviso(**aviso.dict(), criador_id=user.id)
    db.add(db_aviso)
    db.commit()
    db.refresh(db_aviso)
    return db_aviso

# Endpoints para Taxas
@app.get("/taxas")
async def get_taxas(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    taxas = db.query(models.Taxa).filter(models.Taxa.morador_id == current_user.id).all()
    return taxas

@app.post("/taxas/", response_model=schemas.Taxa)
async def create_taxa(
    taxa: schemas.TaxaCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    db_taxa = models.Taxa(**taxa.dict(), morador_id=current_user.id)
    db.add(db_taxa)
    db.commit()
    db.refresh(db_taxa)
    return db_taxa

@app.put("/taxas/{taxa_id}/pagar")
async def marcar_taxa_paga(
    taxa_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    taxa = db.query(models.Taxa).filter(models.Taxa.id == taxa_id, models.Taxa.morador_id == current_user.id).first()
    if not taxa:
        raise HTTPException(status_code=404, detail="Taxa não encontrada")
    
    taxa.paga = True
    taxa.data_pagamento = datetime.now()
    db.commit()
    return {"message": "Taxa marcada como paga"}

# Endpoints para Reuniões
@app.get("/reunioes/", response_model=List[schemas.Reuniao])
async def read_reunioes(
    skip: int = 0,
    limit: int = 50,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    reunioes = db.query(models.Reuniao).offset(skip).limit(limit).all()
    return reunioes

@app.post("/reunioes/", response_model=schemas.Reuniao)
async def create_reuniao(
    reuniao: schemas.ReuniaoCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    db_reuniao = models.Reuniao(**reuniao.dict(), criador_id=current_user.id)
    db.add(db_reuniao)
    db.commit()
    db.refresh(db_reuniao)
    return db_reuniao

@app.post("/aluguel/solicitar", response_model=schemas.Aluguel)
async def solicitar_aluguel(
    aluguel: schemas.AluguelCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None
):
    current_user = auth.get_current_user(token, db)
    
    # Criar solicitação de aluguel
    db_aluguel = models.Aluguel(
        **aluguel.dict(),
        user_id=current_user.id,
        status="pendente"
    )
    db.add(db_aluguel)
    db.commit()
    db.refresh(db_aluguel)
    
    # Registrar atividade
    log_activity(
        db=db,
        user_id=current_user.id,
        action="solicitar_aluguel",
        details=f"Solicitação de aluguel para {aluguel.espaco} em {aluguel.data}",
        ip_address=request.client.host if request else None
    )
    
    return db_aluguel

@app.get("/aluguel/minhas-solicitacoes", response_model=List[schemas.Aluguel])
async def listar_minhas_solicitacoes(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    solicitacoes = db.query(models.Aluguel).filter(models.Aluguel.user_id == current_user.id).all()
    return solicitacoes

@app.post("/users/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    
    # Verificar se é uma imagem
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Criar nome único para o arquivo
    timestamp = datetime.now().timestamp()
    filename = f"profile_{current_user.id}_{timestamp}.{file.filename.split('.')[-1]}"
    filepath = UPLOAD_DIR / "fotos_perfil" / filename
    
    # Salvar arquivo
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Atualizar perfil do usuário
    current_user.profile_picture = f"/uploads/fotos_perfil/{filename}"
    db.commit()
    
    return {"filename": filename, "url": current_user.profile_picture}

@app.post("/upload-comprovante")
async def upload_comprovante(
    comprovante: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    
    # Verificar se é uma imagem
    if not comprovante.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Criar nome único para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}_{comprovante.filename}"
    filepath = UPLOAD_DIR / "comprovantes" / filename
    
    # Salvar arquivo
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(comprovante.file, buffer)
    
    # Criar registro de comprovante
    db_comprovante = models.Comprovante(
        morador_id=current_user.id,
        arquivo_path=str(filepath),
        nome_arquivo=filename,
        data_upload=datetime.now()
    )
    db.add(db_comprovante)
    db.commit()
    db.refresh(db_comprovante)
    
    return {"message": "Comprovante enviado com sucesso", "filename": filename}

# ==================== ROTAS ADMINISTRATIVAS ====================

@app.post("/create-admin")
def create_admin_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verifica se já existe algum usuário admin
    admin_exists = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()
    if admin_exists:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário administrador no sistema"
        )
    
    # Verifica se o email já está em uso
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email já registrado"
        )
    
    # Cria o usuário admin
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        nome=user.nome,
        hashed_password=hashed_password,
        is_admin=True,
        is_active=True,
        role=models.UserRole.ADMIN
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Usuário administrador criado com sucesso"}

@app.get("/admin/dashboard")
async def get_dashboard_data(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Contar usuários
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    
    # Contar taxas
    total_taxas = db.query(models.Taxa).count()
    pending_taxas = db.query(models.Taxa).filter(models.Taxa.status == "Pendente").count()
    
    # Contar solicitações
    total_solicitacoes = db.query(models.Solicitacao).count()
    pending_solicitacoes = db.query(models.Solicitacao).filter(models.Solicitacao.status == "pendente").count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_taxas": total_taxas,
        "pending_taxas": pending_taxas,
        "total_solicitacoes": total_solicitacoes,
        "pending_solicitacoes": pending_solicitacoes
    }

@app.get("/admin/users")
async def get_users_admin(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = db.query(models.User)
    
    # Aplicar filtros
    if search:
        query = query.filter(models.User.email.contains(search) | models.User.nome.contains(search))
    if role:
        query = query.filter(models.User.role == role)
    if status:
        is_active = status.lower() == "true"
        query = query.filter(models.User.is_active == is_active)
    
    # Paginação
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@app.get("/admin/users/{user_id}")
async def get_user_admin(
    user_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user

@app.put("/admin/users/{user_id}")
async def update_user_admin(
    user_id: int,
    user_update: schemas.UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar campos
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
        db.commit()
    db.refresh(user)
    
    return user

@app.put("/admin/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    status_update: dict,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.is_active = status_update.get("is_active", not user.is_active)
    db.commit()
    
    return {"message": "Status atualizado", "is_active": user.is_active}

@app.delete("/admin/users/{user_id}")
async def delete_user_admin(
    user_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(user)
    db.commit()
    
    return {"message": "Usuário deletado com sucesso"}

@app.get("/admin/logs")
async def get_activity_logs_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    logs = db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).all()
    return logs

@app.get("/admin/solicitacoes")
async def get_solicitacoes_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Buscar alugueis (solicitações)
    alugueis = db.query(models.Aluguel).join(models.User).order_by(models.Aluguel.created_at.desc()).all()
    
    # Adicionar nome do usuário a cada solicitação
    for aluguel in alugueis:
        aluguel.user_name = aluguel.user.nome if aluguel.user else "N/A"
    
    return alugueis

@app.post("/admin/solicitacoes/{solicitacao_id}/aprovar")
async def aprovar_solicitacao_admin(
    solicitacao_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    aluguel = db.query(models.Aluguel).filter(models.Aluguel.id == solicitacao_id).first()
    if not aluguel:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    aluguel.status = "aprovado"
    db.commit()
    
    return {"message": "Solicitação aprovada com sucesso"}

@app.post("/admin/solicitacoes/{solicitacao_id}/rejeitar")
async def rejeitar_solicitacao_admin(
    solicitacao_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    aluguel = db.query(models.Aluguel).filter(models.Aluguel.id == solicitacao_id).first()
    if not aluguel:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    aluguel.status = "rejeitado"
    db.commit()
    
    return {"message": "Solicitação rejeitada com sucesso"}

@app.get("/admin/taxas")
async def get_taxas_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    taxas = db.query(models.Taxa).join(models.User).all()
    
    # Adicionar nome do morador a cada taxa
    for taxa in taxas:
        taxa.morador_name = taxa.morador.nome if taxa.morador else "N/A"
    
    return taxas

@app.get("/admin/taxas")
async def listar_taxas_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    taxas = db.query(models.Taxa).all()
    return taxas

@app.post("/admin/taxas/{taxa_id}/aprovar")
async def aprovar_taxa(
    taxa_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    taxa = db.query(models.Taxa).filter(models.Taxa.id == taxa_id).first()
    if not taxa:
        raise HTTPException(status_code=404, detail="Taxa não encontrada")
    
    taxa.status = "Pago"
    db.commit()
    
    return {"message": "Taxa aprovada"}

@app.post("/admin/taxas/{taxa_id}/rejeitar")
async def rejeitar_taxa(
    taxa_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    taxa = db.query(models.Taxa).filter(models.Taxa.id == taxa_id).first()
    if not taxa:
        raise HTTPException(status_code=404, detail="Taxa não encontrada")
    
    taxa.status = "Rejeitada"
    db.commit()
    
    return {"message": "Taxa rejeitada"}

@app.get("/admin/taxas/{taxa_id}/comprovante")
async def visualizar_comprovante(
    taxa_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    taxa = db.query(models.Taxa).filter(models.Taxa.id == taxa_id).first()
    if not taxa or not taxa.comprovante_path:
        raise HTTPException(status_code=404, detail="Comprovante não encontrado")
    
    return FileResponse(taxa.comprovante_path)

@app.get("/taxas/")
async def listar_taxas_usuario(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(token, db)
    taxas = db.query(models.Taxa).filter(models.Taxa.morador_id == current_user.id).all()
    return taxas

@app.post("/register/request", response_model=dict)
async def request_registration(user_request: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    """Solicita registro - envia código de verificação por email"""
    try:
        # Verificar se email já existe
        existing_user = auth.get_user(db, email=user_request.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email já registrado"
            )
        
        # Gerar código de verificação
        verification_code = generate_verification_code()
        
        # Salvar código no banco
        save_verification_code(user_request.email, verification_code)
        
        # Enviar email
        email_sent = await send_verification_email(user_request.email, verification_code)
        
        if email_sent:
            return {
                "message": "Código de verificação enviado para seu email",
                "email": user_request.email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Erro ao enviar email de verificação"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/register/verify", response_model=dict)
async def verify_email_and_register(
    verification: schemas.EmailVerificationRequest,
    user_request: schemas.UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Verifica código e cria usuário pendente de aprovação"""
    try:
        # Verificar código
        if not verify_code(verification.email, verification.verification_code):
            raise HTTPException(
                status_code=400,
                detail="Código inválido ou expirado"
            )
        
        # Verificar se email já existe
        existing_user = auth.get_user(db, email=user_request.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email já registrado"
            )
        
        # Criar usuário pendente de aprovação
        hashed_password = auth.get_password_hash(user_request.password)
        db_user = models.User(
            email=user_request.email,
            nome=user_request.email.split('@')[0],  # Usar parte do email como nome inicial
            hashed_password=hashed_password,
            email_verified=True,
            admin_approved=False,
            is_active=False  # Usuário inativo até ser aprovado pelo admin
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Criar taxas automáticas para o novo morador, se não existirem
        if db_user.role == "morador":
            taxas_existentes = db.query(models.Taxa).filter(models.Taxa.morador_id == db_user.id).count()
            if taxas_existentes == 0:
                meses = [datetime.now().month, (datetime.now().month % 12) + 1]  # Mês atual e próximo
                ano_atual = datetime.now().year
                valor_taxa = 150.00
                for i, mes in enumerate(meses):
                    data_venc = datetime(ano_atual, mes, 10)
                    status = "Pendente" if i == 1 else "Pago"
                    taxa = models.Taxa(
                        morador_id=db_user.id,
                        mes=mes,
                        ano=ano_atual,
                        valor=valor_taxa,
                        status=status,
                        data_vencimento=data_venc,
                        comprovante_path=None if status == "Pendente" else "uploads/comprovantes/maio_2025.pdf"
                    )
                    db.add(taxa)
                db.commit()
        
        return {
            "message": "Email verificado com sucesso! Aguarde a aprovação do administrador.",
            "user_id": db_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/admin/pending-users", response_model=List[schemas.PendingUser])
async def get_pending_users(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Lista usuários pendentes de aprovação"""
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    pending_users = db.query(models.User).filter(
        models.User.email_verified == True,
        models.User.admin_approved == False
    ).all()
    
    return pending_users

@app.post("/admin/approve-user/{user_id}")
async def approve_user(
    user_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Aprova um usuário pendente"""
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.admin_approved:
        raise HTTPException(status_code=400, detail="Usuário já foi aprovado")
    
    user.admin_approved = True
    user.is_active = True
    # Se não tiver foto, seta padrão
    if not user.profile_picture:
        user.profile_picture = "/uploads/default_profile.png"
    db.commit()

    # Criar taxas automáticas para o novo morador, se não existirem
    if user.role == "morador":
        taxas_existentes = db.query(models.Taxa).filter(models.Taxa.morador_id == user.id).count()
        if taxas_existentes == 0:
            meses = [datetime.now().month, (datetime.now().month % 12) + 1]  # Mês atual e próximo
            ano_atual = datetime.now().year
            valor_taxa = 150.00
            for i, mes in enumerate(meses):
                data_venc = datetime(ano_atual, mes, 10)
                status = "Pendente" if i == 1 else "Pago"
                taxa = models.Taxa(
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

    # Registrar atividade
    log_activity(
        db=db,
        user_id=current_user.id,
        action="approve_user",
        details=f"Usuário {user.email} aprovado",
        ip_address=None
    )
    
    return {"message": "Usuário aprovado com sucesso"}

@app.post("/admin/reject-user/{user_id}")
async def reject_user(
    user_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Rejeita um usuário pendente"""
    current_user = auth.get_current_user(token, db)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Registrar atividade antes de deletar
    log_activity(
        db=db,
        user_id=current_user.id,
        action="reject_user",
        details=f"Usuário {user.email} rejeitado",
        ip_address=None
    )
    
    # Deletar usuário
    db.delete(user)
    db.commit()

    return {"message": "Usuário rejeitado e removido"}

# Montar o diretório frontend (sempre por último)
app.mount("/", StaticFiles(directory="C:\Users\keviny.pina\Desktop\login-app2\frontend", html=True), name="frontend")
