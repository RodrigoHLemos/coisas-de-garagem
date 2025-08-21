// Configuração da API
const API_URL = 'http://localhost:8000/api/v1';

// Estado da autenticação
let currentUser = null;
let authToken = null;

// Verificar se há token salvo
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user_data');
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        updateUIForLoggedUser();
    }
}

// Atualizar UI para usuário logado
function updateUIForLoggedUser() {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (authButtons && userMenu) {
        authButtons.style.display = 'none';
        userMenu.style.display = 'flex';
        
        const userName = document.getElementById('user-name');
        if (userName && currentUser) {
            userName.textContent = currentUser.name || currentUser.email;
        }
    }
}

// Função para mostrar modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('active'), 10);
    }
}

// Função para fechar modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.style.display = 'none', 300);
    }
}

// Alternar entre modais
function switchModal(from, to) {
    closeModal(from);
    setTimeout(() => showModal(to), 300);
}

// Função de Registro
async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // Desabilitar botão
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registrando...';
    
    // Obter dados do formulário
    const formData = {
        email: form.email.value.trim(),
        password: form.password.value,
        name: form.name.value.trim(),
        cpf: form.cpf.value.replace(/\D/g, ''), // Remove formatação
        phone: form.phone.value.replace(/\D/g, ''), // Remove formatação
        role: form.role?.value || 'buyer'
    };
    
    // Validar senha
    if (formData.password !== form.confirmPassword.value) {
        showNotification('As senhas não coincidem', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registro realizado com sucesso! Faça login para continuar.', 'success');
            form.reset();
            switchModal('register-modal', 'login-modal');
        } else {
            // Tratar erro detalhado
            let errorMessage = 'Erro ao registrar';
            if (data.detail) {
                if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                } else if (Array.isArray(data.detail)) {
                    // Erros de validação do Pydantic
                    const fieldNames = {
                        'email': 'E-mail',
                        'password': 'Senha',
                        'name': 'Nome',
                        'cpf': 'CPF',
                        'phone': 'Telefone',
                        'role': 'Tipo de usuário'
                    };
                    
                    const errors = data.detail.map(err => {
                        const field = err.loc[err.loc.length - 1];
                        const fieldName = fieldNames[field] || field;
                        let message = err.msg;
                        
                        // Traduções específicas
                        if (message.includes('at least 8 characters')) {
                            message = 'deve ter pelo menos 8 caracteres';
                        } else if (message.includes('maiúscula')) {
                            message = 'deve conter pelo menos uma letra maiúscula';
                        } else if (message.includes('minúscula')) {
                            message = 'deve conter pelo menos uma letra minúscula';
                        } else if (message.includes('número')) {
                            message = 'deve conter pelo menos um número';
                        } else if (message.includes('11 digits')) {
                            message = 'deve ter 11 dígitos';
                        } else if (message.includes('10 or 11 digits')) {
                            message = 'deve ter 10 ou 11 dígitos';
                        }
                        
                        return `${fieldName} ${message}`;
                    });
                    
                    // Se houver erros de senha, adicionar dica
                    const hasPasswordError = data.detail.some(err => 
                        err.loc[err.loc.length - 1] === 'password'
                    );
                    
                    if (hasPasswordError) {
                        errorMessage = errors.join('\n') + '\n\nRequisitos da senha:\n• Mínimo 8 caracteres\n• Pelo menos 1 letra maiúscula\n• Pelo menos 1 letra minúscula\n• Pelo menos 1 número';
                    } else {
                        errorMessage = errors.join('\n');
                    }
                } else if (typeof data.detail === 'object') {
                    errorMessage = JSON.stringify(data.detail);
                }
            }
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Erro no registro:', error);
        showNotification('Erro ao conectar com o servidor', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Função de Login
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    // Desabilitar botão
    submitBtn.disabled = true;
    submitBtn.textContent = 'Entrando...';
    
    // Criar FormData para OAuth2
    const formData = new URLSearchParams();
    formData.append('username', form.email.value.trim());
    formData.append('password', form.password.value);
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Salvar token e buscar dados do usuário
            authToken = data.access_token;
            localStorage.setItem('access_token', authToken);
            localStorage.setItem('refresh_token', data.refresh_token || '');
            
            // Buscar perfil do usuário
            await fetchUserProfile();
            
            showNotification('Login realizado com sucesso!', 'success');
            form.reset();
            closeModal('login-modal');
            
            // Redirecionar baseado no tipo de usuário
            if (currentUser && currentUser.role === 'seller') {
                window.location.href = 'seller.html';
            } else {
                window.location.href = 'buyer.html';
            }
        } else {
            showNotification(data.detail || 'Email ou senha inválidos', 'error');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showNotification('Erro ao conectar com o servidor', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Buscar perfil do usuário
async function fetchUserProfile() {
    try {
        const response = await fetch(`${API_URL}/users/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            localStorage.setItem('user_data', JSON.stringify(currentUser));
            updateUIForLoggedUser();
        }
    } catch (error) {
        console.error('Erro ao buscar perfil:', error);
    }
}

// Função de Logout
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    
    authToken = null;
    currentUser = null;
    
    showNotification('Logout realizado com sucesso', 'success');
    
    // Redirecionar para home
    window.location.href = 'index.html';
}

// Mostrar notificação
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Máscaras para inputs
function applyCPFMask(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{2})/, '$1-$2');
        input.value = value;
    }
}

function applyPhoneMask(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length <= 11) {
        if (value.length === 11) {
            value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (value.length === 10) {
            value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        input.value = value;
    }
}

// Validar senha em tempo real
function validatePasswordRealtime(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };
    
    // Atualizar indicadores visuais
    const reqLength = document.getElementById('req-length');
    const reqUppercase = document.getElementById('req-uppercase');
    const reqLowercase = document.getElementById('req-lowercase');
    const reqNumber = document.getElementById('req-number');
    
    if (reqLength) {
        reqLength.style.color = requirements.length ? '#27ae60' : '#e74c3c';
        reqLength.innerHTML = requirements.length ? '✓ Mínimo 8 caracteres' : '• Mínimo 8 caracteres';
    }
    if (reqUppercase) {
        reqUppercase.style.color = requirements.uppercase ? '#27ae60' : '#e74c3c';
        reqUppercase.innerHTML = requirements.uppercase ? '✓ Uma letra maiúscula' : '• Uma letra maiúscula';
    }
    if (reqLowercase) {
        reqLowercase.style.color = requirements.lowercase ? '#27ae60' : '#e74c3c';
        reqLowercase.innerHTML = requirements.lowercase ? '✓ Uma letra minúscula' : '• Uma letra minúscula';
    }
    if (reqNumber) {
        reqNumber.style.color = requirements.number ? '#27ae60' : '#e74c3c';
        reqNumber.innerHTML = requirements.number ? '✓ Um número' : '• Um número';
    }
    
    return requirements.length && requirements.uppercase && requirements.lowercase && requirements.number;
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticação
    checkAuth();
    
    // Adicionar event listeners para fechar modais
    document.querySelectorAll('.modal-close, .modal-overlay').forEach(element => {
        element.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal-overlay') || e.target.classList.contains('modal-close')) {
                const modal = e.target.closest('.modal');
                if (modal) {
                    closeModal(modal.id);
                }
            }
        });
    });
    
    // Adicionar máscaras aos inputs
    const cpfInputs = document.querySelectorAll('input[name="cpf"]');
    cpfInputs.forEach(input => {
        input.addEventListener('input', () => applyCPFMask(input));
    });
    
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', () => applyPhoneMask(input));
    });
    
    // Adicionar validação de senha em tempo real
    const passwordInput = document.getElementById('register-password');
    const passwordReqs = document.getElementById('password-requirements');
    
    if (passwordInput) {
        passwordInput.addEventListener('focus', () => {
            if (passwordReqs) {
                passwordReqs.style.display = 'block';
            }
        });
        
        passwordInput.addEventListener('blur', () => {
            if (passwordReqs && passwordInput.value === '') {
                passwordReqs.style.display = 'none';
            }
        });
        
        passwordInput.addEventListener('input', (e) => {
            validatePasswordRealtime(e.target.value);
        });
    }
});

// Exportar funções para uso global
window.showModal = showModal;
window.closeModal = closeModal;
window.switchModal = switchModal;
window.handleRegister = handleRegister;
window.handleLogin = handleLogin;
window.handleLogout = handleLogout;