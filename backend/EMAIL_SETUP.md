# Configuração do Sistema de Email

## 📧 Configuração do Gmail

Para que o sistema de verificação por email funcione, você precisa configurar suas credenciais do Gmail no arquivo `email_config.py`.

### Passo 1: Ativar Autenticação de 2 Fatores
1. Acesse sua conta Google
2. Vá em "Segurança"
3. Ative a "Verificação em duas etapas"

### Passo 2: Gerar Senha do App
1. Ainda em "Segurança"
2. Clique em "Senhas de app"
3. Selecione "Email" como aplicativo
4. Copie a senha gerada (16 caracteres)

### Passo 3: Configurar o Arquivo
Edite o arquivo `backend/email_config.py` e substitua:

```python
conf = ConnectionConfig(
    MAIL_USERNAME="seu_email@gmail.com",  # Seu email Gmail
    MAIL_PASSWORD="sua_senha_app",        # Senha do app gerada
    MAIL_FROM="seu_email@gmail.com",      # Seu email Gmail
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)
```

### Exemplo:
```python
conf = ConnectionConfig(
    MAIL_USERNAME="meucondominio@gmail.com",
    MAIL_PASSWORD="abcd efgh ijkl mnop",
    MAIL_FROM="meucondominio@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)
```

## 🔄 Como Funciona o Sistema

### 1. Registro do Usuário
- Usuário preenche email e senha
- Sistema envia código de 6 dígitos por email
- Código expira em 5 minutos

### 2. Verificação do Email
- Usuário digita o código recebido
- Sistema verifica se o código está correto
- Se correto, cria usuário pendente de aprovação

### 3. Aprovação do Administrador
- Admin vê usuários pendentes no painel
- Pode aprovar ou rejeitar cada usuário
- Usuário aprovado pode fazer login

## 🚀 Testando o Sistema

1. Configure as credenciais de email
2. Reinicie o servidor: `python main.py`
3. Acesse a página de registro
4. Teste o fluxo completo

## ⚠️ Importante

- **Nunca** compartilhe suas credenciais de email
- Use sempre uma senha de app, nunca sua senha principal
- O sistema funciona apenas com Gmail por padrão
- Para outros provedores, ajuste as configurações SMTP 