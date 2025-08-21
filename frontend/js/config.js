// Configuração centralizada da aplicação
const config = {
    // Detecção automática do ambiente baseado no hostname
    isProduction: !window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1'),
    
    // URL da API - muda automaticamente entre desenvolvimento e produção
    get API_URL() {
        // Permite override via meta tag ou variável global
        if (window.API_URL) {
            return window.API_URL;
        }
        
        // Verifica se há uma meta tag com a URL da API
        const metaApiUrl = document.querySelector('meta[name="api-url"]');
        if (metaApiUrl && metaApiUrl.content) {
            return metaApiUrl.content;
        }
        
        // URLs padrão baseadas no ambiente
        if (this.isProduction) {
            // Em produção, usa subdomínio api do mesmo domínio ou URL conhecida
            const currentDomain = window.location.hostname;
            
            // Se estiver no Vercel, usa a URL do Render
            if (currentDomain.includes('vercel.app')) {
                return 'https://coisas-de-garagem-api.onrender.com/api/v1';
            }
            
            // Se tiver domínio próprio no futuro
            if (currentDomain.includes('coisasdegaragem.com')) {
                return 'https://api.coisasdegaragem.com/api/v1';
            }
            
            // Fallback para produção
            return 'https://coisas-de-garagem-api.onrender.com/api/v1';
        } else {
            // Desenvolvimento local
            return 'http://localhost:8000/api/v1';
        }
    },
    
    // Configurações de storage
    storage: {
        tokenKey: 'access_token',
        refreshTokenKey: 'refresh_token',
        userDataKey: 'user_data'
    },
    
    // Timeouts e retry
    request: {
        timeout: 30000, // 30 segundos
        retryAttempts: 3,
        retryDelay: 1000 // 1 segundo
    },
    
    // Configurações de debug
    debug: !this.isProduction,
    
    // Versão da aplicação (útil para cache busting)
    version: '1.0.2'
};

// Tornar config global para fácil acesso
window.appConfig = config;

// Log do ambiente atual (apenas em desenvolvimento)
if (config.debug) {
    console.log('Ambiente:', config.isProduction ? 'Produção' : 'Desenvolvimento');
    console.log('API URL:', config.API_URL);
}