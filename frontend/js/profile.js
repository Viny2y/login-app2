document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    setupFormSubmit();
    // Adicionar event listener para upload de foto
    const fotoInput = document.getElementById('fotoPerfilInput');
    if (fotoInput) {
        fotoInput.addEventListener('change', uploadFoto);
    }
});

async function loadUserProfile() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/login.html';
            return;
        }

        const response = await fetch('http://localhost:8000/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            document.getElementById('nome').value = user.nome || '';
            document.getElementById('email').value = user.email || '';
            document.getElementById('idade').value = user.idade || '';
            document.getElementById('dataNascimento').value = user.data_nascimento ? new Date(user.data_nascimento).toISOString().split('T')[0] : '';
            document.getElementById('sexo').value = user.sexo || '';
            document.getElementById('rg').value = user.rg || '';
            document.getElementById('cpf').value = user.cpf || '';
            document.getElementById('cor').value = user.cor || '';
            
            const fotoPerfil = document.getElementById('fotoPerfil');
            if (fotoPerfil) {
                if (user.email === "keviny11felix@gmail.com") {
                    fotoPerfil.src = "../image/demo-1-bg.jpg";
                    fotoPerfil.style.width = "150px";
                    fotoPerfil.style.height = "150px";
                    fotoPerfil.style.border = "3px solid gold";
                    fotoPerfil.style.boxShadow = "0 0 0 3px #0d6efd";
                } else if (user.profile_picture) {
                    fotoPerfil.src = user.profile_picture.startsWith('http') ? user.profile_picture : `http://localhost:8000${user.profile_picture}`;
                }
            }
        } else {
            showNotification('Erro ao carregar perfil', 'error');
        }
    } catch (error) {
        showNotification('Erro ao carregar perfil: ' + error.message, 'error');
    }
}

function setupFormSubmit() {
    const form = document.getElementById('profileForm');
    if (!form) return;
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const userData = {
            nome: formData.get('nome'),
            email: formData.get('email'),
            idade: parseInt(formData.get('idade')) || null,
            data_nascimento: formData.get('dataNascimento') || null,
            sexo: formData.get('sexo'),
            rg: formData.get('rg'),
            cpf: formData.get('cpf'),
            cor: formData.get('cor')
        };

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8000/users/me', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const updatedUser = await response.json();
                showNotification('Perfil atualizado com sucesso!', 'success');
                
                // Atualizar os campos com os dados retornados
                document.getElementById('nome').value = updatedUser.nome || '';
                document.getElementById('email').value = updatedUser.email || '';
                document.getElementById('idade').value = updatedUser.idade || '';
                document.getElementById('dataNascimento').value = updatedUser.data_nascimento ? new Date(updatedUser.data_nascimento).toISOString().split('T')[0] : '';
                document.getElementById('sexo').value = updatedUser.sexo || '';
                document.getElementById('rg').value = updatedUser.rg || '';
                document.getElementById('cpf').value = updatedUser.cpf || '';
                document.getElementById('cor').value = updatedUser.cor || '';
            } else {
                const error = await response.json();
                showNotification(error.detail || 'Erro ao atualizar perfil', 'error');
            }
        } catch (error) {
            showNotification('Erro ao atualizar perfil: ' + error.message, 'error');
        }
    });
}

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Função para upload de foto
async function uploadFoto(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/users/me/profile-picture', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const fotoPerfil = document.getElementById('fotoPerfil');
            if (fotoPerfil) {
                fotoPerfil.src = data.url;
            }
            showNotification('Foto atualizada com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erro ao fazer upload da foto', 'error');
        }
    } catch (error) {
        showNotification('Erro ao fazer upload da foto: ' + error.message, 'error');
    }
}
window.uploadFoto = uploadFoto;

const fotoPerfil = document.getElementById('fotoPerfil');
if (fotoPerfil) {
    fotoPerfil.onerror = function() {
        this.src = "../image/demo-1-bg.jpg";
    };
} 