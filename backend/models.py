from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MORADOR = "morador"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nome = Column(String)
    age = Column(Integer, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    rg = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    color = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.MORADOR)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    email_verified = Column(Boolean, default=False)
    admin_approved = Column(Boolean, default=False)

    # Relacionamentos
    activity_logs = relationship("ActivityLog", back_populates="user")
    avisos = relationship("Aviso", back_populates="criador")
    taxas = relationship("Taxa", back_populates="morador")
    reunioes = relationship("Reuniao", back_populates="criador")
    alugueis = relationship("Aluguel", back_populates="user")
    solicitacoes = relationship("Solicitacao", back_populates="morador")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)  # login, update, delete, etc
    details = Column(String)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relacionamento com usuário
    user = relationship("User", back_populates="activity_logs")

class Aviso(Base):
    __tablename__ = "avisos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    conteudo = Column(String, nullable=False)
    data = Column(DateTime, default=datetime.now)
    criado_por = Column(Integer, ForeignKey("users.id"))
    ativo = Column(Boolean, default=True)

    criador = relationship("User", back_populates="avisos")

class Taxa(Base):
    __tablename__ = "taxas"

    id = Column(Integer, primary_key=True, index=True)
    morador_id = Column(Integer, ForeignKey("users.id"))
    mes = Column(Integer)
    ano = Column(Integer)
    valor = Column(Float)
    status = Column(String)  # Pendente, Pago, Em Atraso
    comprovante_path = Column(String, nullable=True)
    data_vencimento = Column(DateTime)

    morador = relationship("User", back_populates="taxas")

class Reuniao(Base):
    __tablename__ = "reunioes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    data = Column(DateTime, nullable=False)
    local = Column(String, nullable=False)
    criado_por = Column(Integer, ForeignKey("users.id"))
    ativo = Column(Boolean, default=True)

    criador = relationship("User", back_populates="reunioes")

class Aluguel(Base):
    __tablename__ = "alugueis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    comodo = Column(String)
    data = Column(DateTime)
    horario = Column(String)
    duracao = Column(Integer)
    motivo = Column(String)
    status = Column(String, default="pendente")  # pendente, aprovado, rejeitado
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="alugueis")

class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    id = Column(Integer, primary_key=True, index=True)
    morador_id = Column(Integer, ForeignKey("users.id"))
    data_solicitacao = Column(DateTime, default=datetime.now)
    comodo = Column(String)
    data_evento = Column(DateTime)
    horario = Column(String)
    duracao = Column(Float)  # Duração em horas
    status = Column(String)  # Pendente, Aprovado, Rejeitado

    morador = relationship("User", back_populates="solicitacoes")

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    verification_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now) 