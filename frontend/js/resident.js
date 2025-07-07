// Verificar autenticação
async function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "../login.html";
        return;
    }

    try {
        // Buscar dados do usuário do backend
        const response = await fetch("http://127.0.0.1:8000/users/me", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const userData = await response.json();
            
            // Verificar se é admin
            if (userData.role === "admin") {
                window.location.href = "../admin.html";
                return;
            }

            // Carregar nome do usuário
            const nomeUsuario = document.getElementById("nomeUsuario");
            if (nomeUsuario) {
                nomeUsuario.textContent = `Bem-vindo, ${userData.name || "Morador"}`;
            }

            // Carregar email do usuário
            const userEmail = document.getElementById("userEmail");
            if (userEmail) {
                userEmail.textContent = userData.email || "";
            }

            // Carregar foto do perfil
            const userProfilePicture = document.getElementById("userProfilePicture");
            if (userProfilePicture) {
                if (userData.email === "keviny11felix@gmail.com") {
                    userProfilePicture.src = "../image/demo-1-bg.jpg";
                    userProfilePicture.style.width = "60px";
                    userProfilePicture.style.height = "60px";
                    userProfilePicture.style.border = "3px solid gold";
                    userProfilePicture.style.boxShadow = "0 0 0 3px #0d6efd";
                } else if (userData.profile_picture) {
                    userProfilePicture.src = userData.profile_picture;
                } else {
                    userProfilePicture.src = "../image/demo-1-bg.jpg";
                }
                userProfilePicture.onerror = function() {
                    this.src = "../image/demo-1-bg.jpg";
                };
            }

            // Salvar dados do usuário no localStorage
            localStorage.setItem("usuarioLogado", JSON.stringify(userData));
        } else {
            throw new Error("Erro ao carregar dados do usuário");
        }
    } catch (error) {
        console.error("Erro ao verificar autenticação:", error);
        window.location.href = "../login.html";
    }
}

// Função de logout
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("usuarioLogado");
    window.location.href = "../login.html";
}

// Carregar avisos
async function loadAvisos() {
    // Função mantida para compatibilidade, mas não será usada
    console.log("Função loadAvisos chamada");
}

// Carregar reuniões
async function loadReunioes() {
    // Função mantida para compatibilidade, mas não será usada
    console.log("Função loadReunioes chamada");
}

// Função para upload de comprovante
async function uploadComprovante() {
    const token = localStorage.getItem("token");
    if (!token) return;

    const fileInput = document.getElementById('comprovantePix');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Por favor, selecione um arquivo');
        return;
    }

    const formData = new FormData();
    formData.append('comprovante', file);

    try {
        const response = await fetch("http://127.0.0.1:8000/upload-comprovante", {
            method: 'POST',
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            renderTaxas(); // Atualiza painel após upload
        } else {
            const error = await response.json();
            alert('Erro ao enviar comprovante: ' + error.detail);
        }
    } catch (error) {
        console.error("Erro ao enviar comprovante:", error);
        alert('Erro ao enviar comprovante');
    }
}

// Função para buscar e renderizar as taxas do backend
async function renderTaxas() {
    const token = localStorage.getItem("token");
    const container = document.getElementById("taxasContainer");
    if (!token || !container) return;

    container.innerHTML = `<div class='text-center'><div class='spinner-border text-primary' role='status'></div><p class='mt-2'>Carregando taxas...</p></div>`;

    try {
        const response = await fetch("http://127.0.0.1:8000/taxas/", {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!response.ok) throw new Error("Erro ao buscar taxas");
        const taxas = await response.json();
        if (!taxas.length) {
            container.innerHTML = `<p class='text-center'>Nenhuma taxa encontrada</p>`;
            return;
        }
        let html = "";
        taxas.sort((a, b) => (b.ano - a.ano) || (b.mes - a.mes));
        taxas.forEach(taxa => {
            const statusClass = getStatusClass(taxa.status);
            const statusText = getStatusText(taxa.status);
            const mesNome = getMonthName(taxa.mes);
            const venc = new Date(taxa.data_vencimento).toLocaleDateString('pt-BR');
            html += `<div class='d-flex justify-content-between align-items-center mb-3'>
                <div>
                    <h6 class='mb-0'>${mesNome}</h6>
                    <small class='text-muted'>Vencimento: ${venc}</small>
                </div>
                <span class='badge ${statusClass}'>${statusText}</span>
            </div>`;
            if (taxa.status === 'Pendente') {
                html += `<div class='mb-3'>
                    <label for='comprovantePix' class='form-label'>Anexar Comprovante PIX</label>
                    <input type='file' class='form-control' id='comprovantePix' accept='.pdf,.jpg,.jpeg,.png'>
                    <div class='form-text'>Formatos aceitos: PDF, JPG, PNG</div>
                    <button class='btn btn-primary btn-sm mt-2' onclick='uploadComprovante()'>
                        <i class='bi bi-upload'></i> Enviar Comprovante
                    </button>
                </div>`;
            }
        });
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<p class='text-center text-danger'>Erro ao carregar taxas</p>`;
    }
}

function getStatusClass(status) {
    switch (status) {
        case 'Pendente': return 'bg-warning';
        case 'Em Análise': return 'bg-info';
        case 'Pago': return 'bg-success';
        case 'Rejeitado': return 'bg-danger';
        default: return 'bg-secondary';
    }
}
function getStatusText(status) {
    switch (status) {
        case 'Pendente': return 'Pendente';
        case 'Em Análise': return 'Em Análise';
        case 'Pago': return 'Pago';
        case 'Rejeitado': return 'Rejeitado';
        default: return status;
    }
}
function getMonthName(mes) {
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return meses[mes - 1];
}

console.log("Script resident.js carregado");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM carregado, iniciando preenchimento dos dados");
    
    // Verificar autenticação e carregar dados do usuário
    checkAuth();

    // Renderizar taxas reais do backend
    renderTaxas();

    // Forçar carregamento dos dados imediatamente
    setTimeout(() => {
        // Dados dos avisos
        const avisos = [
            "Recolhimento de lixo será às segundas-feiras",
            "Prazo maximo para pagamentos será dia 10/06",
            "Faltará água no dia 15/06",
            "Faltará energia no dia 18/06",
            "Doação de alimentos será no dia 20/06",
        ];
        
        const listaAvisos = document.getElementById("listaAvisos");
        if (listaAvisos) {
            listaAvisos.innerHTML = '';
            avisos.forEach(aviso => {
                const li = document.createElement("li");
                li.className = "list-group-item";
                li.textContent = aviso;
                listaAvisos.appendChild(li);
            });
        }

        // Dados das reuniões
        const reunioes = [
            "20/06 - Assembleia Geral às 19h no salão",
            "05/07 - Reunião sobre portaria"
        ];
        
        const listaReunioes = document.getElementById("listaReunioes");
        if (listaReunioes) {
            listaReunioes.innerHTML = '';
            reunioes.forEach(reuniao => {
                const li = document.createElement("li");
                li.className = "list-group-item";
                li.textContent = reuniao;
                listaReunioes.appendChild(li);
            });
        }
    }, 100);

    // Configurando o nome do usuário
    const nomeUsuario = document.getElementById("nomeUsuario");
    if (nomeUsuario) {
        nomeUsuario.textContent = "Morador";
    }
});
