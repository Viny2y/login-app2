// Função para fazer logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

// Função para verificar se o usuário está autenticado
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Função para fazer login
async function login(email, password) {
    try {
        const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            window.location.href = 'profile.html';
            return true;
        } else {
            throw new Error(data.detail || 'Erro ao fazer login');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        throw error;
    }
}

// Exportar funções
window.auth = {
    login,
    logout,
    checkAuth
}; 