// Função para mostrar notificações
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Função para validar idade
function validateAge(age) {
    if (!age) return null;
    try {
        const num = parseInt(age, 10);
        if (isNaN(num) || num < 0 || num > 120) {
            return null;
        }
        return num;
    } catch (e) {
        return null;
    }
}

// Função para validar data
function validateDate(dateStr) {
    if (!dateStr) return null;
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return null;
        return date.toISOString().split('T')[0];
    } catch (e) {
        return null;
    }
}

// Função para carregar dados do usuário
async function loadUserData() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const userData = await response.json();
            console.log('Dados do usuário carregados:', userData);
            
            // Preencher campos do formulário
            document.getElementById('nome').value = userData.nome || '';
            document.getElementById('idade').value = userData.age || '';
            document.getElementById('dataNascimento').value = userData.birth_date ? userData.birth_date.split('T')[0] : '';
            document.getElementById('sexo').value = userData.gender || '';
            document.getElementById('rg').value = userData.rg || '';
            document.getElementById('cpf').value = userData.cpf || '';
            document.getElementById('cor').value = userData.color || '';
            
            const img = document.getElementById('fotoPerfil');
            if (userData.profile_picture) {
                img.src = userData.profile_picture;
            } else {
                img.src = 'assets/img/default-profile.png';
            }
            // Adiciona classe especial para o keviny
            if (userData.email === "keviny11felix@gmail.com") {
                img.classList.add("keviny");
                console.log("[DEBUG] Aplicando classe keviny na foto de perfil!");
                // Força o estilo inline também
                img.style.width = "120px";
                img.style.height = "120px";
                img.style.borderRadius = "50%";
                img.style.objectFit = "cover";
                img.style.border = "4px solid gold";
                img.style.boxShadow = "0 0 0 4px #0d6efd";
            } else {
                img.classList.remove("keviny");
            }
            // Sempre que der erro, mostra a imagem padrão
            img.onerror = function() {
                this.src = 'assets/img/default-profile.png';
            };
        } else {
            console.error('Erro ao carregar dados do usuário');
            showNotification('Erro ao carregar dados do usuário', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        showNotification('Erro ao conectar com o servidor', 'error');
    }
}

// Função para salvar dados do usuário
async function saveUserData(event) {
    event.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }

    try {
        // Coletar dados brutos do formulário
        const ageInput = document.getElementById('idade').value;
        const birthDateInput = document.getElementById('dataNascimento').value;
        const nameInput = document.getElementById('nome').value;
        const rgInput = document.getElementById('rg').value;
        const cpfInput = document.getElementById('cpf').value;
        const genderInput = document.getElementById('sexo').value;
        const colorInput = document.getElementById('cor').value;

        console.log("DEBUG: Dados do formulário (crus):", {
            ageInput,
            birthDateInput,
            nameInput,
            rgInput,
            cpfInput,
            genderInput,
            colorInput
        });

        // Preparar dados do formulário
        const formData = {
            nome: nameInput.trim() || null,
            age: ageInput ? parseInt(ageInput, 10) : null,
            birth_date: birthDateInput || null,
            rg: rgInput.trim() || null,
            cpf: cpfInput.trim() || null,
            gender: genderInput || null,
            color: colorInput.trim() || null
        };

        console.log("DEBUG: Dados a serem enviados para o backend (processados):", formData);
        console.log("DEBUG: Tipos dos dados:", {
            nome: typeof formData.nome,
            age: typeof formData.age,
            birth_date: typeof formData.birth_date,
            rg: typeof formData.rg,
            cpf: typeof formData.cpf,
            gender: typeof formData.gender,
            color: typeof formData.color
        });

        const response = await fetch('http://localhost:8000/users/me', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        console.log('DEBUG: Resposta do servidor:', data);

        if (response.ok) {
            showNotification('Dados salvos com sucesso!', 'success');
            loadUserData();
            return true;
        } else {
            let errorMessage = 'Erro ao salvar dados';
            if (data.detail) {
                if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                } else if (Array.isArray(data.detail)) {
                    const errorMessages = data.detail.map(err => 
                        `${err.loc ? err.loc.join('.') : ''} -> ${err.msg}`
                    ).join(', ');
                    errorMessage = errorMessages;
                    console.error("DEBUG: Erro detalhado do FastAPI:", data.detail);
                }
            }
            console.error('DEBUG: Erro completo:', errorMessage);
            showNotification(errorMessage, 'error');
            return false;
        }
    } catch (error) {
        console.error('DEBUG: Erro ao salvar:', error);
        showNotification('Erro ao conectar com o servidor', 'error');
        return false;
    }
}

// Renomear a função para corresponder ao HTML
window.saveUserData = saveUserData;

// Função para lidar com upload de foto
async function handleProfilePictureUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/users/me/profile-picture', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Resposta do upload:', data);
            const img = document.getElementById('fotoPerfil');
            if (img) {
                img.src = data.url || data.profile_picture;
            }
            showNotification('Foto atualizada com sucesso!', 'success');
        } else {
            const error = await response.json();
            console.error('Erro no upload:', error);
            showNotification(error.detail || 'Erro ao atualizar foto', 'error');
        }
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        showNotification('Erro ao atualizar foto', 'error');
    }
}

// Inicializar eventos ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    
    // Setup do formulário
    const form = document.getElementById('profileForm');
    if (form) {
        form.addEventListener('submit', saveUserData);
    }
    
    // Setup do input de foto
    const fotoInput = document.getElementById('fotoPerfilInput');
    if (fotoInput) {
        fotoInput.addEventListener('change', handleProfilePictureUpload);
    }
    
    // Setup do botão de foto
    const btnFoto = document.querySelector('.btn-alterar-foto');
    if (btnFoto) {
        btnFoto.addEventListener('click', (e) => {
            e.preventDefault();
            const input = document.getElementById('fotoPerfilInput');
            if (input) {
                input.click();
            }
        });
    }
}); 