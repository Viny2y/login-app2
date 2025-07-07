from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    nome: str
    role: UserRole = UserRole.MORADOR

class UserCreate(UserBase):
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('As senhas não coincidem')
        return v

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('As senhas não coincidem')
        return v

class EmailVerificationRequest(BaseModel):
    email: EmailStr
    verification_code: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserProfileUpdate(BaseModel):
    nome: Optional[str] = None
    age: Optional[int] = None
    birth_date: Optional[str] = None
    rg: Optional[str] = None
    cpf: Optional[str] = None
    gender: Optional[str] = None
    color: Optional[str] = None
    phone: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    age: Optional[int] = None
    birth_date: Optional[datetime] = None
    rg: Optional[str] = None
    cpf: Optional[str] = None
    gender: Optional[str] = None
    color: Optional[str] = None
    profile_picture: Optional[str] = None
    phone: Optional[str] = None
    email_verified: bool
    admin_approved: bool

    class Config:
        from_attributes = True

class PendingUser(BaseModel):
    id: int
    email: str
    nome: str
    created_at: datetime
    email_verified: bool
    admin_approved: bool

    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: List[User]
    total: int
    page: int
    per_page: int

class ActivityLog(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    details: str
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AluguelBase(BaseModel):
    comodo: str
    data: datetime
    horario: str
    duracao: int
    motivo: str

class AluguelCreate(AluguelBase):
    pass

class Aluguel(AluguelBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    user_name: Optional[str] = None

    class Config:
        from_attributes = True

class AluguelStatusUpdate(BaseModel):
    status: str

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['aprovado', 'rejeitado', 'pendente']
        if v not in valid_statuses:
            raise ValueError(f"Status inválido. Use um dos seguintes: {', '.join(valid_statuses)}")
        return v

    class Config:
        from_attributes = True

class AvisoBase(BaseModel):
    titulo: str
    conteudo: str
    ativo: bool = True

class AvisoCreate(AvisoBase):
    pass

class Aviso(AvisoBase):
    id: int
    data: datetime
    criado_por: int

    class Config:
        from_attributes = True

class TaxaBase(BaseModel):
    mes: int
    ano: int
    valor: float
    data_vencimento: datetime

class TaxaCreate(TaxaBase):
    morador_id: int

class Taxa(TaxaBase):
    id: int
    morador_id: int
    status: str
    comprovante_path: Optional[str] = None

    class Config:
        from_attributes = True

class ReuniaoBase(BaseModel):
    titulo: str
    descricao: str
    data: datetime
    local: str
    ativo: bool = True

class ReuniaoCreate(ReuniaoBase):
    pass

class Reuniao(ReuniaoBase):
    id: int
    criado_por: int

    class Config:
        from_attributes = True

class SolicitacaoBase(BaseModel):
    comodo: str
    data_evento: datetime
    horario: str
    duracao: float

class SolicitacaoCreate(SolicitacaoBase):
    pass

class Solicitacao(SolicitacaoBase):
    id: int
    morador_id: int
    data_solicitacao: datetime
    status: str

    class Config:
        from_attributes = True 