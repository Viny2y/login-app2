// Verificar autenticação e carregar dados iniciais
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadDashboardData();
    loadPendingUsers();
    loadActivityLogs();

    // Recarregar taxas ao clicar na aba
    const taxasTab = document.getElementById('taxas-tab');
    if (taxasTab) {
        taxasTab.addEventListener('click', function() {
            loadTaxas();
        });
    }

    // Configurar listener para mudança de abas
    const tabElements = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabElements.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            
            // Recarregar dados quando a aba for ativada
            if (targetId === '#users') {
                loadUsers();
            } else if (targetId === '#pending-users') {
                loadPendingUsers();
            } else if (targetId === '#logs') {
                loadActivityLogs();
            } else if (targetId === '#solicitacoes') {
                loadSolicitacoes();
            } else if (targetId === '#taxas') {
                loadTaxas();
            }
        });
    });
});

// Verificar autenticação
async function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/users/me", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const userData = await response.json();
            
            // Verificar se é admin
            if (userData.role !== "admin") {
                window.location.href = "morador/painel.html";
                return;
            }

            // Carregar nome do administrador
            const adminName = document.getElementById("adminName");
            if (adminName) {
                adminName.textContent = userData.name || "Administrador";
            }

            // Carregar dados iniciais
            loadUsers(1);
            loadLogs();
            loadSolicitacoes();
            loadTaxas();
        } else {
            throw new Error("Erro ao verificar autenticação");
        }
    } catch (error) {
        console.error("Erro ao verificar autenticação:", error);
        window.location.href = "login.html";
    }
}

// Carregar dados do dashboard
async function loadDashboardData() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/admin/dashboard", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById("totalUsers").textContent = data.total_users || 0;
            document.getElementById("activeUsers").textContent = data.active_users || 0;
            document.getElementById("pendingRequests").textContent = data.pending_requests || 0;
            document.getElementById("totalTaxas").textContent = data.total_taxas || 0;
        }
    } catch (error) {
        console.error("Erro ao carregar dados do dashboard:", error);
    }
}

// Carregar usuários
async function loadUsers(page = 1) {
    try {
        const token = localStorage.getItem("token");
        const search = document.getElementById("searchInput")?.value || "";
        const role = document.getElementById("roleFilter")?.value || "";
        const status = document.getElementById("statusFilter")?.value || "";

        let url = `http://127.0.0.1:8000/admin/users?page=${page}`;
        if (search) url += `&search=${search}`;
        if (role) url += `&role=${role}`;
        if (status) url += `&status=${status}`;

        const response = await fetch(url, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayUsers(data.users);
        } else {
            showNotification("Erro ao carregar usuários", "error");
        }
    } catch (error) {
        console.error("Erro ao carregar usuários:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Carregar logs
async function loadLogs() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/admin/logs", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const logs = await response.json();
            displayLogs(logs);
        } else {
            showNotification("Erro ao carregar logs", "error");
        }
    } catch (error) {
        console.error("Erro ao carregar logs:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Carregar solicitações
async function loadSolicitacoes() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/admin/solicitacoes", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
        const solicitacoes = await response.json();
            displaySolicitacoes(solicitacoes);
        } else {
            showNotification("Erro ao carregar solicitações", "error");
        }
    } catch (error) {
        console.error("Erro ao carregar solicitações:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Carregar taxas
async function loadTaxas() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/admin/taxas", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const taxas = await response.json();
            displayTaxas(taxas);
            document.getElementById('totalTaxas').textContent = taxas.length;
        } else {
            console.error('Erro ao carregar taxas');
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Exibir usuários na tabela
function displayUsers(users) {
    const tbody = document.getElementById("usersTableBody");
    tbody.innerHTML = "";

    users.forEach(user => {
        const tr = document.createElement("tr");
        let lastLoginText = 'Nunca';
        if (user.last_login) {
            const lastLoginDate = new Date(user.last_login);
            lastLoginText = lastLoginDate.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        tr.innerHTML = `
            <td>${user.email}</td>
            <td>${user.name || '-'}</td>
            <td><span class="badge bg-${getRoleBadgeColor(user.role)}">${translateRole(user.role)}</span></td>
            <td><span class="badge bg-${user.is_active ? 'success' : 'danger'}">${user.is_active ? 'Ativo' : 'Inativo'}</span></td>
            <td>${lastLoginText}</td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-${user.is_active ? 'danger' : 'success'}" onclick="toggleUserStatus(${user.id}, ${!user.is_active})" title="${user.is_active ? 'Desativar' : 'Ativar'}">
                        <i class="bi bi-${user.is_active ? 'person-x' : 'person-check'}"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Exibir logs na tabela
function displayLogs(logs) {
    const tbody = document.getElementById("logsTableBody");
    tbody.innerHTML = "";

    logs.forEach(log => {
        const tr = document.createElement("tr");
        const date = new Date(log.created_at);
        const formattedDate = date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        tr.innerHTML = `
            <td>${formattedDate}</td>
            <td>${log.user ? log.user.email : 'Sistema'}</td>
            <td>${log.action}</td>
            <td>${log.details}</td>
            <td>${log.ip_address || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Exibir solicitações na tabela
function displaySolicitacoes(solicitacoes) {
    const tbody = document.getElementById("solicitacoesTableBody");
    tbody.innerHTML = "";

    solicitacoes.forEach(solicitacao => {
        const tr = document.createElement("tr");
        const createdDate = new Date(solicitacao.created_at);
        const eventDate = new Date(solicitacao.data);
        
        const formattedCreatedDate = createdDate.toLocaleDateString('pt-BR');
        const formattedEventDate = eventDate.toLocaleDateString('pt-BR');
        
        tr.innerHTML = `
            <td>${formattedCreatedDate}</td>
            <td>${solicitacao.user_name || solicitacao.user?.nome || 'N/A'}</td>
            <td>${solicitacao.comodo}</td>
            <td>${formattedEventDate}</td>
            <td>${solicitacao.horario}</td>
            <td>${solicitacao.duracao}h</td>
            <td><span class="badge bg-${getStatusBadgeColor(solicitacao.status)}">${translateStatus(solicitacao.status)}</span></td>
            <td>
                <div class="btn-group" role="group">
                    ${solicitacao.status === 'pendente' ? `
                        <button class="btn btn-sm btn-success" onclick="aprovarSolicitacao(${solicitacao.id})" title="Aprovar">
                            <i class="bi bi-check-lg"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="rejeitarSolicitacao(${solicitacao.id})" title="Rejeitar">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Exibir taxas na tabela
function displayTaxas(taxas) {
    const taxasList = document.getElementById('taxasList');
    taxasList.innerHTML = '';
    
    taxas.forEach(taxa => {
        const row = document.createElement('tr');
        
        const statusClass = getStatusClass(taxa.status);
        const statusText = getStatusText(taxa.status);
        
        row.innerHTML = `
            <td>${taxa.morador.email}</td>
            <td>${getMonthName(taxa.mes)}/${taxa.ano}</td>
            <td>R$ ${taxa.valor.toFixed(2)}</td>
            <td><span class="badge ${statusClass}">${statusText}</span></td>
            <td>
                ${taxa.comprovante_path ? 
                    `<button class="btn btn-sm btn-outline-primary" onclick="viewComprovante(${taxa.id})">
                        <i class="bi bi-eye"></i> Ver
                    </button>` : 
                    '<span class="text-muted">Nenhum</span>'
                }
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-success" onclick="aprovarTaxa(${taxa.id})" title="Aprovar">
                        <i class="bi bi-check-lg"></i> Aprovar
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="rejeitarTaxa(${taxa.id})" title="Rejeitar">
                        <i class="bi bi-x-lg"></i> Rejeitar
                    </button>
                </div>
            </td>
        `;
        
        taxasList.appendChild(row);
    });
}

// Funções auxiliares
function getRoleBadgeColor(role) {
    switch (role) {
        case 'admin': return 'danger';
        case 'morador': return 'primary';
        default: return 'secondary';
    }
}

function getStatusBadgeColor(status) {
    switch (status) {
        case 'aprovado': return 'success';
        case 'rejeitado': return 'danger';
        case 'pendente': return 'warning';
        default: return 'secondary';
    }
}

function getTaxaStatusBadgeColor(status) {
    switch (status) {
        case 'Pago': return 'success';
        case 'Pendente': return 'warning';
        case 'Em Atraso': return 'danger';
        default: return 'secondary';
    }
}

function translateRole(role) {
    switch (role) {
        case 'admin':
            return 'Administrador';
        case 'morador':
            return 'Morador';
        default:
            return role;
    }
}

function translateStatus(status) {
    switch (status) {
        case 'aprovado':
            return 'Aprovado';
        case 'rejeitado':
            return 'Rejeitado';
        case 'pendente':
            return 'Pendente';
        default:
            return status;
    }
}

function translateTaxaStatus(status) {
    switch (status) {
        case 'Pago':
            return 'Pago';
        case 'Pendente':
            return 'Pendente';
        case 'Em Atraso':
            return 'Em Atraso';
        default:
            return status;
    }
}

// Aplicar filtros
function applyFilters() {
    loadUsers(1);
}

// Limpar filtros
function clearFilters() {
    document.getElementById("searchInput").value = "";
    document.getElementById("roleFilter").value = "";
    document.getElementById("statusFilter").value = "";
    loadUsers(1);
}

// Editar usuário
async function editUser(userId) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/users/${userId}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            
            document.getElementById("editUserId").value = user.id;
            document.getElementById("editUserName").value = user.name || "";
            document.getElementById("editUserEmail").value = user.email;
            document.getElementById("editUserRole").value = user.role;
            document.getElementById("editUserPassword").value = "";

            const modal = new bootstrap.Modal(document.getElementById("editUserModal"));
            modal.show();
        } else {
            showNotification("Erro ao carregar dados do usuário", "error");
        }
    } catch (error) {
        console.error("Erro ao editar usuário:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Salvar edição do usuário
async function saveUserEdit() {
    try {
        const token = localStorage.getItem("token");
        const userId = document.getElementById("editUserId").value;
        const userData = {
            name: document.getElementById("editUserName").value,
            role: document.getElementById("editUserRole").value,
            password: document.getElementById("editUserPassword").value || null
        };

        const response = await fetch(`http://127.0.0.1:8000/admin/users/${userId}`, {
            method: "PUT",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            showNotification("Usuário atualizado com sucesso!", "success");
            const modal = bootstrap.Modal.getInstance(document.getElementById("editUserModal"));
            modal.hide();
            loadUsers(1);
        } else {
            const error = await response.json();
            showNotification(error.detail || "Erro ao atualizar usuário", "error");
        }
    } catch (error) {
        console.error("Erro ao salvar usuário:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Alternar status do usuário
async function toggleUserStatus(userId, newStatus) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/users/${userId}/toggle-status`, {
            method: "PUT",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ is_active: newStatus })
        });

        if (response.ok) {
            showNotification(`Usuário ${newStatus ? 'ativado' : 'desativado'} com sucesso!`, "success");
            loadUsers(1);
        } else {
            const error = await response.json();
            showNotification(error.detail || "Erro ao alterar status do usuário", "error");
        }
    } catch (error) {
        console.error("Erro ao alterar status do usuário:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Deletar usuário
async function deleteUser(userId) {
    if (!confirm("Tem certeza que deseja deletar este usuário?")) {
        return;
    }

    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/users/${userId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            showNotification("Usuário deletado com sucesso!", "success");
            loadUsers(1);
        } else {
            const error = await response.json();
            showNotification(error.detail || "Erro ao deletar usuário", "error");
        }
    } catch (error) {
        console.error("Erro ao deletar usuário:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Aprovar solicitação
async function aprovarSolicitacao(solicitacaoId) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/solicitacoes/${solicitacaoId}/aprovar`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            showNotification("Solicitação aprovada com sucesso!", "success");
            loadSolicitacoes();
        } else {
            const error = await response.json();
            showNotification(error.detail || "Erro ao aprovar solicitação", "error");
        }
    } catch (error) {
        console.error("Erro ao aprovar solicitação:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Rejeitar solicitação
async function rejeitarSolicitacao(solicitacaoId) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/solicitacoes/${solicitacaoId}/rejeitar`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            showNotification("Solicitação rejeitada com sucesso!", "success");
            loadSolicitacoes();
        } else {
            const error = await response.json();
            showNotification(error.detail || "Erro ao rejeitar solicitação", "error");
        }
    } catch (error) {
        console.error("Erro ao rejeitar solicitação:", error);
        showNotification("Erro ao conectar com o servidor", "error");
    }
}

// Função para visualizar comprovante
async function viewComprovante(taxaId) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/taxas/${taxaId}/comprovante`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } else {
            showNotification('Erro ao carregar comprovante', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao carregar comprovante', 'error');
    }
}

// Ver como morador
function viewAsResident() {
    // Abrir o painel do morador em modo demo em uma nova aba
    window.open("morador/painel-demo.html", "_blank");
}

// Logout
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("usuarioLogado");
    window.location.href = "login.html";
}

// Alternar tema
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    
    body.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    
    const icon = document.querySelector(".theme-switch i");
    icon.className = newTheme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-fill";
}

// Mostrar notificação
function showNotification(message, type) {
    const notification = document.getElementById("notification");
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = "block";
    
    setTimeout(() => {
        notification.style.display = "none";
    }, 3000);
}

// Carregar tema salvo
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        document.body.setAttribute("data-theme", savedTheme);
        const icon = document.querySelector(".theme-switch i");
        icon.className = savedTheme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-fill";
    }
});

// Função para obter classe CSS do status
function getStatusClass(status) {
    switch (status) {
        case 'Pendente': return 'bg-warning';
        case 'Em Análise': return 'bg-info';
        case 'Pago': return 'bg-success';
        case 'Rejeitado': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// Função para obter texto do status
function getStatusText(status) {
    switch (status) {
        case 'Pendente': return 'Pendente';
        case 'Em Análise': return 'Em Análise';
        case 'Pago': return 'Pago';
        case 'Rejeitado': return 'Rejeitado';
        default: return status;
    }
}

// Função para obter nome do mês
function getMonthName(mes) {
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return meses[mes - 1];
}

// Função para aprovar taxa
async function aprovarTaxa(taxaId) {
    if (!confirm('Confirmar aprovação desta taxa? A taxa será marcada como PAGO.')) return;
    
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/taxas/${taxaId}/aprovar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            showNotification('Taxa aprovada com sucesso! Status alterado para PAGO.', 'success');
            loadTaxas();
            loadStats();
        } else {
            showNotification('Erro ao aprovar taxa', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao aprovar taxa', 'error');
    }
}

// Função para rejeitar taxa
async function rejeitarTaxa(taxaId) {
    if (!confirm('Confirmar rejeição desta taxa? A taxa será marcada como REJEITADA.')) return;
    
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/taxas/${taxaId}/rejeitar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            showNotification('Taxa rejeitada com sucesso! Status alterado para REJEITADO.', 'success');
            loadTaxas();
            loadStats();
        } else {
            showNotification('Erro ao rejeitar taxa', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao rejeitar taxa', 'error');
    }
}

// Carregar estatísticas
async function loadStats() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/admin/dashboard", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById("totalUsers").textContent = data.total_users || 0;
            document.getElementById("activeUsers").textContent = data.active_users || 0;
            document.getElementById("pendingRequests").textContent = data.pending_requests || 0;
            document.getElementById("totalTaxas").textContent = data.total_taxas || 0;
        }
    } catch (error) {
        console.error("Erro ao carregar estatísticas:", error);
    }
}

// Função para carregar usuários pendentes
async function loadPendingUsers() {
    console.log('🔍 Carregando usuários pendentes...');
    try {
        const token = localStorage.getItem("token");
        console.log('🔑 Token obtido:', token ? 'Sim' : 'Não');
        
        const response = await fetch('http://127.0.0.1:8000/admin/pending-users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        console.log('📊 Status da resposta:', response.status);

        if (response.ok) {
            const pendingUsers = await response.json();
            console.log('✅ Usuários pendentes recebidos:', pendingUsers);
            displayPendingUsers(pendingUsers);
            updatePendingCount(pendingUsers.length);
        } else {
            console.error('❌ Erro ao carregar usuários pendentes:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('❌ Detalhes do erro:', errorText);
        }
    } catch (error) {
        console.error('❌ Erro na função loadPendingUsers:', error);
    }
}

// Função para exibir usuários pendentes
function displayPendingUsers(pendingUsers) {
    console.log('📋 Exibindo usuários pendentes:', pendingUsers);
    const tbody = document.getElementById('pendingUsersTableBody');
    console.log('🔍 Elemento tbody encontrado:', tbody ? 'Sim' : 'Não');
    
    if (pendingUsers.length === 0) {
        console.log('📝 Nenhum usuário pendente, exibindo mensagem');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum usuário pendente</td></tr>';
        return;
    }

    console.log('📝 Gerando HTML para', pendingUsers.length, 'usuários');
    const html = pendingUsers.map(user => `
        <tr>
            <td>${user.email}</td>
            <td>${user.nome}</td>
            <td>${formatDateTime(user.created_at)}</td>
            <td>
                <span class="badge bg-warning">Pendente</span>
            </td>
            <td>
                <button class="btn btn-success btn-sm" onclick="approveUser(${user.id})">
                    <i class="bi bi-check-circle"></i> Aprovar
                </button>
                <button class="btn btn-danger btn-sm" onclick="rejectUser(${user.id})">
                    <i class="bi bi-x-circle"></i> Rejeitar
                </button>
            </td>
        </tr>
    `).join('');
    
    console.log('📝 HTML gerado:', html);
    tbody.innerHTML = html;
    console.log('✅ Tabela atualizada com sucesso');
}

// Função para atualizar contador de pendentes
function updatePendingCount(count) {
    console.log('🔢 Atualizando contador de pendentes para:', count);
    const badge = document.getElementById('pending-count');
    console.log('🔍 Elemento badge encontrado:', badge ? 'Sim' : 'Não');
    
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
        console.log('✅ Badge atualizado com sucesso');
    } else {
        console.error('❌ Elemento badge não encontrado');
    }
}

// Função para aprovar usuário
async function approveUser(userId) {
    if (!confirm('Tem certeza que deseja aprovar este usuário?')) {
        return;
    }

    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/approve-user/${userId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showNotification('Usuário aprovado com sucesso!', 'success');
            loadPendingUsers(); // Recarregar lista
            loadUsers(); // Recarregar lista de usuários
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erro ao aprovar usuário', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao aprovar usuário', 'error');
    }
}

// Função para rejeitar usuário
async function rejectUser(userId) {
    if (!confirm('Tem certeza que deseja rejeitar este usuário? Esta ação não pode ser desfeita.')) {
        return;
    }

    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`http://127.0.0.1:8000/admin/reject-user/${userId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showNotification('Usuário rejeitado e removido!', 'success');
            loadPendingUsers(); // Recarregar lista
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Erro ao rejeitar usuário', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao rejeitar usuário', 'error');
    }
}

// Função para formatar data e hora
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Data inválida';
    }
} 