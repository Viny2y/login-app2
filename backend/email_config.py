from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from database import SessionLocal
from models import EmailVerification

# Configuração do email (você precisará configurar com suas credenciais)
conf = ConnectionConfig(
    MAIL_USERNAME="kevinypina4@gmail.com",  # Substitua pelo seu email
    MAIL_PASSWORD="ejrf ljfz cyic lmpb",        # Substitua pela senha do app
    MAIL_FROM="kevinypina4@gmail.com",      # Substitua pelo seu email
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)

def generate_verification_code() -> str:
    """Gera um código de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

def save_verification_code(email: str, code: str) -> None:
    """Salva o código de verificação no banco"""
    db = SessionLocal()
    try:
        # Remove códigos antigos para este email
        db.query(EmailVerification).filter(
            EmailVerification.email == email
        ).delete()
        
        # Cria novo código
        verification = EmailVerification(
            email=email,
            verification_code=code,
            expires_at=datetime.now() + timedelta(minutes=5)
        )
        db.add(verification)
        db.commit()
    finally:
        db.close()

async def send_verification_email(email: str, code: str) -> bool:
    """Envia email de verificação"""
    try:
        message = MessageSchema(
            subject="Código de Verificação - Sistema do Condomínio",
            recipients=[email],
            body=f"""
            <html>
            <body>
                <h2>Verificação de Email</h2>
                <p>Olá! Você solicitou o registro no sistema do condomínio.</p>
                <p>Use o código abaixo para verificar seu email:</p>
                <h1 style="color: #007bff; font-size: 2em; text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">{code}</h1>
                <p><strong>Este código expira em 5 minutos.</strong></p>
                <p>Se você não solicitou este registro, ignore este email.</p>
                <hr>
                <p style="color: #6c757d; font-size: 0.9em;">Sistema de Gerenciamento do Condomínio</p>
            </body>
            </html>
            """,
            subtype="html"
        )
        
        await fastmail.send_message(message)
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def verify_code(email: str, code: str) -> bool:
    """Verifica se o código está correto e não expirou"""
    db = SessionLocal()
    try:
        verification = db.query(EmailVerification).filter(
            EmailVerification.email == email,
            EmailVerification.verification_code == code,
            EmailVerification.is_used == False,
            EmailVerification.expires_at > datetime.now()
        ).first()
        
        if verification:
            verification.is_used = True
            db.commit()
            return True
        return False
    finally:
        db.close()

def cleanup_expired_codes():
    """Remove códigos expirados"""
    db = SessionLocal()
    try:
        db.query(EmailVerification).filter(
            EmailVerification.expires_at < datetime.now()
        ).delete()
        db.commit()
    finally:
        db.close() 