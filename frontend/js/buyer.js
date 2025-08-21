// Configuração da API - usa config.js
const API_URL = window.appConfig ? window.appConfig.API_URL : 'http://localhost:8000/api/v1';

// Estado da aplicação
let html5QrCode = null;
let isScanning = false;
let currentProduct = null;
let authToken = null;
let currentUser = null;

// Lista de produtos (será carregada do backend)
let availableProducts = [];

// Histórico de compras (TODO: integrar com backend quando houver endpoint)
let purchaseHistory = [];

const toggleCameraBtn = document.getElementById('toggle-camera');
const scannerPlaceholder = document.getElementById('scanner-placeholder');
const scannerStatus = document.getElementById('scanner-status');
const manualCodeInput = document.getElementById('manual-code');
const searchProductBtn = document.getElementById('search-product');
const availableProductsGrid = document.getElementById('available-products');
const purchasesGrid = document.getElementById('purchases-grid');
const productModal = document.getElementById('product-modal');
const purchaseModal = document.getElementById('purchase-modal');
const successToast = document.getElementById('success-toast');

// Verificar autenticação
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user_data');
    
    if (!token || !user) {
        return false;
    }
    
    authToken = token;
    currentUser = JSON.parse(user);
    
    // Verificar se é comprador
    if (currentUser.role !== 'buyer') {
        showToast('Acesso negado. Apenas compradores podem acessar esta página.', 'error');
        return false;
    }
    
    return true;
}

// Atualizar informações do usuário na navbar
function updateUserInfo() {
    const userMenu = document.querySelector('.user-menu span');
    if (userMenu && currentUser) {
        userMenu.textContent = currentUser.name || currentUser.email;
    }
}

// Função removida - agora usamos autenticação do backend
function requireLogin(next) {
    if (currentUser) {
        next();
    } else {
        showToast('Por favor, faça login para realizar compras', 'error');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    // Verificar autenticação
    if (!checkAuth()) {
        window.location.href = 'index.html';
        return;
    }
    
    // Atualizar informações do usuário
    updateUserInfo();
    
    // Carregar produtos do backend
    await loadProductsFromAPI();
    renderAvailableProducts();
    
    // Carregar histórico de compras (local por enquanto)
    loadData();
    renderPurchaseHistory();
    updatePurchaseStats();
    
    initializeEventListeners();
});

function initializeEventListeners() {
    toggleCameraBtn.addEventListener('click', toggleCamera);
    searchProductBtn.addEventListener('click', searchProductManually);
    manualCodeInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchProductManually();
        }
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterProducts(this.dataset.filter);
        });
    });

    document.querySelectorAll('#close-product-modal, #close-product-modal-btn').forEach(btn => {
        btn.addEventListener('click', closeProductModal);
    });

    document.querySelectorAll('#close-purchase-modal, #cancel-purchase-btn').forEach(btn => {
        btn.addEventListener('click', closePurchaseModal);
    });

    document.getElementById('buy-product-btn').addEventListener('click', showPurchaseModal);
    document.getElementById('confirm-purchase-btn').addEventListener('click', confirmPurchase);

    productModal.addEventListener('click', function(e) {
        if (e.target === productModal) {
            closeProductModal();
        }
    });

    purchaseModal.addEventListener('click', function(e) {
        if (e.target === purchaseModal) {
            closePurchaseModal();
        }
    });

    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                loginModal.classList.remove('active');
            }
        });
    }
}

function toggleCamera() {
    if (!isScanning) {
        startScanning();
    } else {
        stopScanning();
    }
}

function startScanning() {
    const qrReaderElement = document.getElementById('qr-reader');
    
    html5QrCode = new Html5Qrcode("qr-reader");
    
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
    };

    html5QrCode.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        onScanFailure
    ).then(() => {
        isScanning = true;
        toggleCameraBtn.innerHTML = '<i class="fas fa-stop"></i> Parar Câmera';
        toggleCameraBtn.classList.remove('btn-outline');
        toggleCameraBtn.classList.add('btn-primary');
        scannerPlaceholder.style.display = 'none';
        updateScannerStatus('Escaneando... Posicione o QR code na área destacada');
    }).catch(err => {
        console.error('Error starting camera:', err);
        showToast('Erro ao acessar a câmera. Verifique as permissões.', 'error');
        updateScannerStatus('Erro ao acessar a câmera');
    });
}

function stopScanning() {
    if (html5QrCode && isScanning) {
        html5QrCode.stop().then(() => {
            isScanning = false;
            toggleCameraBtn.innerHTML = '<i class="fas fa-camera"></i> Ativar Câmera';
            toggleCameraBtn.classList.remove('btn-primary');
            toggleCameraBtn.classList.add('btn-outline');
            scannerPlaceholder.style.display = 'block';
            updateScannerStatus('Posicione o QR code dentro da área de escaneamento');
        }).catch(err => {
            console.error('Error stopping camera:', err);
        });
    }
}

function onScanSuccess(decodedText, decodedResult) {
    console.log('QR Code scanned:', decodedText);

    const productId = extractProductIdFromQR(decodedText);
    
    if (productId) {
        const product = findProductById(productId);
        if (product) {
            showProductModal(product);
            showToast('Produto encontrado!');
        } else {
            showToast('Produto não encontrado', 'error');
        }
    } else {
        showToast('QR Code inválido', 'error');
    }

    stopScanning();
}

function onScanFailure(error) {
    // log de falhas
    // ex: console.warn('Falha ao escanear:', error);
}

function updateScannerStatus(message) {
    scannerStatus.innerHTML = `<p>${message}</p>`;
}

function extractProductIdFromQR(qrText) {
    const match = qrText.match(/(\d+)/);
    if (match) {
        return parseInt(match[1]);
    }
    return null;
}

function findProductById(productId) {
    return availableProducts.find(product => product.id === productId || product.id === String(productId));
}

function searchProductManually() {
    const code = manualCodeInput.value.trim();
    if (!code) {
        showToast('Digite um código válido', 'error');
        return;
    }
    
    const productId = extractProductIdFromQR(code);
    if (productId) {
        const product = findProductById(productId);
        if (product) {
            showProductModal(product);
            showToast('Produto encontrado!');
            manualCodeInput.value = '';
        } else {
            showToast('Produto não encontrado', 'error');
        }
    } else {
        showToast('Código inválido', 'error');
    }
}

async function loadProductsFromAPI() {
    try {
        const response = await fetch(`${API_URL}/products/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            availableProducts = await response.json();
        } else {
            showToast('Erro ao carregar produtos', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        showToast('Erro ao conectar com o servidor', 'error');
    }
}

function renderAvailableProducts(filter = 'all') {
    availableProductsGrid.innerHTML = '';
    
    const filteredProducts = filter === 'all' 
        ? availableProducts 
        : availableProducts.filter(product => product.category === filter);
    
    filteredProducts.forEach(product => {
        const productCard = createProductCard(product);
        availableProductsGrid.appendChild(productCard);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.onclick = () => showProductModal(product);
    
    card.innerHTML = `
        <div class="product-image">
            ${product.images && product.images.length > 0 ? 
                `<img src="${product.images[0]}" alt="${product.name}">` : 
                '<i class="fas fa-image"></i>'
            }
            ${product.status === 'available' ? '<div class="product-badge">Disponível</div>' : ''}
        </div>
        <div class="product-content">
            <h3 class="product-name">${product.name}</h3>
            <div class="product-price">R$ ${parseFloat(product.price).toFixed(2)}</div>
            <div class="product-seller">
                <i class="fas fa-store"></i>
                <span>${product.seller_name || 'Vendedor'}</span>
            </div>
            <div class="product-actions">
                <button class="btn btn-primary btn-small" onclick="event.stopPropagation(); showProductModal('${product.id}')">
                    Ver Detalhes
                </button>
            </div>
        </div>
    `;
    
    return card;
}

function filterProducts(category) {
    renderAvailableProducts(category);
}

function renderPurchaseHistory() {
    purchasesGrid.innerHTML = '';
    
    purchaseHistory.forEach(purchase => {
        const purchaseCard = createPurchaseCard(purchase);
        purchasesGrid.appendChild(purchaseCard);
    });
}

function createPurchaseCard(purchase) {
    const card = document.createElement('div');
    card.className = 'purchase-card';
    
    const statusClass = purchase.status === 'completed' ? 'completed' : 'pending';
    const statusText = purchase.status === 'completed' ? 'Concluída' : 'Pendente';
    
    card.innerHTML = `
        <div class="purchase-image">
            ${purchase.image ? 
                `<img src="${purchase.image}" alt="${purchase.productName}">` : 
                '<i class="fas fa-shopping-bag"></i>'
            }
        </div>
        <div class="purchase-info">
            <h3 class="purchase-name">${purchase.productName}</h3>
            <div class="purchase-details">
                <span class="purchase-price">R$ ${purchase.price.toFixed(2)}</span>
                <span class="purchase-date">${formatDate(purchase.date)}</span>
            </div>
            <div class="purchase-seller">Vendedor: ${purchase.seller}</div>
        </div>
        <div class="purchase-status">
            <span class="status-badge ${statusClass}">${statusText}</span>
        </div>
    `;
    
    return card;
}

function updatePurchaseStats() {
    const totalPurchases = purchaseHistory.length;
    const totalSpent = purchaseHistory.reduce((sum, purchase) => sum + purchase.price, 0);
    
    document.getElementById('total-purchases').textContent = totalPurchases;
    document.getElementById('total-spent').textContent = `R$ ${totalSpent.toFixed(2)}`;
}

function showProductModal(product) {
    if (typeof product === 'string' || typeof product === 'number') {
        product = findProductById(product);
    }
    
    if (!product) return;
    
    currentProduct = product;

    const modalImage = document.getElementById('modal-product-image');
    modalImage.innerHTML = product.images && product.images.length > 0 ? 
        `<img src="${product.images[0]}" alt="${product.name}">` : 
        '<i class="fas fa-image"></i>';
    
    document.getElementById('modal-product-name').textContent = product.name;
    document.getElementById('modal-product-price').textContent = `R$ ${parseFloat(product.price).toFixed(2)}`;
    document.getElementById('modal-product-description').textContent = product.description;
    document.getElementById('modal-seller-name').textContent = product.seller_name || 'Vendedor';
    
    productModal.classList.add('active');
}

function closeProductModal() {
    productModal.classList.remove('active');
    currentProduct = null;
}

function showPurchaseModal() {
    if (!currentProduct) return;
    requireLogin(() => {
        document.getElementById('purchase-product-name').textContent = currentProduct.name;
        document.getElementById('purchase-product-price').textContent = `R$ ${parseFloat(currentProduct.price).toFixed(2)}`;
        document.getElementById('purchase-seller-name').textContent = currentProduct.seller_name || 'Vendedor';
        document.getElementById('purchase-total-price').textContent = `R$ ${parseFloat(currentProduct.price).toFixed(2)}`;
        closeProductModal();
        purchaseModal.classList.add('active');
    });
}

function closePurchaseModal() {
    purchaseModal.classList.remove('active');
}

async function confirmPurchase() {
    if (!currentProduct) return;
    
    // TODO: Implementar endpoint de compra no backend
    // Por enquanto, salvar localmente
    const newPurchase = {
        id: Date.now(),
        productName: currentProduct.name,
        price: parseFloat(currentProduct.price),
        seller: currentProduct.seller_name || 'Vendedor',
        date: new Date().toISOString().split('T')[0],
        status: 'completed',
        image: currentProduct.images && currentProduct.images[0],
        buyer: currentUser
    };
    
    purchaseHistory.unshift(newPurchase);
    renderPurchaseHistory();
    updatePurchaseStats();
    closePurchaseModal();
    showToast('Compra realizada com sucesso!');
    currentProduct = null;
    saveData();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('success-toast');
    const toastMessage = document.getElementById('toast-message');

    toast.style.display = 'none';
    toast.classList.remove('show');
    void toast.offsetWidth;

    toastMessage.textContent = message;
    
    if (type === 'error') {
        toast.style.background = 'var(--error-color)';
        toast.querySelector('i').className = 'fas fa-exclamation-circle';
    } else {
        toast.style.background = 'var(--success-color)';
        toast.querySelector('i').className = 'fas fa-check-circle';
    }
    
    toast.style.display = 'flex';
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.style.display = 'none';
        }, 300);
    }, 3000);
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

function saveData() {
    localStorage.setItem('garage_sale_purchases', JSON.stringify(purchaseHistory));
}

function loadData() {
    const savedPurchases = localStorage.getItem('garage_sale_purchases');
    if (savedPurchases) {
        purchaseHistory = JSON.parse(savedPurchases);
    }
}

// Função de logout
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    window.location.href = 'index.html';
}

// Adicionar event listener para logout
document.addEventListener('DOMContentLoaded', function() {
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.style.cursor = 'pointer';
        userMenu.addEventListener('click', function() {
            if (confirm('Deseja fazer logout?')) {
                handleLogout();
            }
        });
    }
});

document.addEventListener('visibilitychange', function() {
    if (document.hidden && isScanning) {
        stopScanning();
    }
});

window.addEventListener('beforeunload', function() {
    if (isScanning) {
        stopScanning();
    }
});

