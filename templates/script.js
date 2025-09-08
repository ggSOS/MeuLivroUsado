/**
 * Cliente JavaScript para API da Biblioteca
 * Facilita a integração da API em aplicações web
 */

class BibliotecaAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    /**
     * Método genérico para fazer requisições HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return {
                success: true,
                data: data,
                status: response.status
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                status: error.status || 500
            };
        }
    }

    // ==================== MÉTODOS DE SISTEMA ====================

    /**
     * Verifica se a API está funcionando
     */
    async health() {
        return await this.request('/health');
    }

    /**
     * Obtém informações gerais da API
     */
    async info() {
        return await this.request('/');
    }

    // ==================== MÉTODOS DE ESTADOS ====================

    /**
     * Lista todos os estados
     */
    async getEstados() {
        return await this.request('/estados');
    }

    /**
     * Busca um estado específico por ID
     */
    async getEstado(id) {
        return await this.request(`/estados/${id}`);
    }

    /**
     * Cria um novo estado
     */
    async createEstado(nome) {
        return await this.request('/estados', {
            method: 'POST',
            body: JSON.stringify({ nm_estado: nome })
        });
    }

    /**
     * Atualiza um estado existente
     */
    async updateEstado(id, nome) {
        return await this.request(`/estados/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ nm_estado: nome })
        });
    }

    /**
     * Remove um estado
     */
    async deleteEstado(id) {
        return await this.request(`/estados/${id}`, {
            method: 'DELETE'
        });
    }

    // ==================== MÉTODOS DE CIDADES ====================

    /**
     * Lista todas as cidades
     */
    async getCidades() {
        return await this.request('/cidades');
    }

    /**
     * Busca uma cidade específica por ID
     */
    async getCidade(id) {
        return await this.request(`/cidades/${id}`);
    }

    /**
     * Cria uma nova cidade
     */
    async createCidade(nome, idEstado) {
        return await this.request('/cidades', {
            method: 'POST',
            body: JSON.stringify({ 
                nm_cidade: nome, 
                id_estado: idEstado 
            })
        });
    }

    // ==================== MÉTODOS DE USUÁRIOS ====================

    /**
     * Lista todos os usuários (sem senhas)
     */
    async getUsuarios() {
        return await this.request('/usuarios');
    }

    /**
     * Busca um usuário específico por login
     */
    async getUsuario(login) {
        return await this.request(`/usuarios/${login}`);
    }

    /**
     * Cria um novo usuário
     */
    async createUsuario(login, senha, nome, email = null) {
        const userData = {
            login: login,
            senha: senha,
            nm_usuario: nome
        };
        
        if (email) {
            userData.email_contato = email;
        }

        return await this.request('/usuarios', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // ==================== MÉTODOS DE AUTORES ====================

    /**
     * Lista todos os autores
     */
    async getAutores() {
        return await this.request('/autores');
    }

    /**
     * Cria um novo autor
     */
    async createAutor(nome) {
        return await this.request('/autores', {
            method: 'POST',
            body: JSON.stringify({ nm_autor: nome })
        });
    }

    // ==================== MÉTODOS DE CATEGORIAS ====================

    /**
     * Lista todas as categorias
     */
    async getCategorias() {
        return await this.request('/categorias');
    }

    /**
     * Cria uma nova categoria
     */
    async createCategoria(nome, imagemBase64) {
        return await this.request('/categorias', {
            method: 'POST',
            body: JSON.stringify({ 
                nm_categoria: nome,
                img_categoria: imagemBase64
            })
        });
    }

    // ==================== MÉTODOS DE LIVROS ====================

    /**
     * Lista todos os livros
     */
    async getLivros() {
        return await this.request('/livros');
    }

    /**
     * Busca um livro específico por ID
     */
    async getLivro(id) {
        return await this.request(`/livros/${id}`);
    }

    /**
     * Cria um novo livro
     */
    async createLivro(dadosLivro) {
        const requiredFields = [
            'nm_livro', 'preco', 'pagamento_eletronico', 'pagamento_dinheiro',
            'entrega_presencial', 'entrega_delivery', 'img_livro', 'cep',
            'login_comprador', 'login_vendedor'
        ];

        // Validar campos obrigatórios
        for (let field of requiredFields) {
            if (!dadosLivro[field]) {
                return {
                    success: false,
                    error: `Campo obrigatório ausente: ${field}`
                };
            }
        }

        return await this.request('/livros', {
            method: 'POST',
            body: JSON.stringify(dadosLivro)
        });
    }

    // ==================== MÉTODOS UTILITÁRIOS ====================

    /**
     * Converte uma imagem File para base64
     */
    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Remove o prefixo data:image/...;base64,
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    /**
     * Valida CPF simples
     */
    validateCEP(cep) {
        const cepPattern = /^\d{8}$/;
        return cepPattern.test(cep.toString());
    }

    /**
     * Valida email simples
     */
    validateEmail(email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    }

    // ==================== MÉTODOS DE CONVENIÊNCIA ====================

    /**
     * Busca livros por autor
     */
    async getLivrosByAutor(nomeAutor) {
        const livros = await this.getLivros();
        if (!livros.success) return livros;

        // Filtrar livros que contenham o autor (implementação simples)
        const livrosFiltrados = livros.data.filter(livro => 
            livro.autores && livro.autores.some(autor => 
                autor.NM_AUTOR.toLowerCase().includes(nomeAutor.toLowerCase())
            )
        );

        return {
            success: true,
            data: livrosFiltrados
        };
    }

    /**
     * Busca livros por categoria
     */
    async getLivrosByCategoria(nomeCategoria) {
        const livros = await this.getLivros();
        if (!livros.success) return livros;

        const livrosFiltrados = livros.data.filter(livro => 
            livro.categorias && livro.categorias.some(categoria => 
                categoria.NM_CATEGORIA.toLowerCase().includes(nomeCategoria.toLowerCase())
            )
        );

        return {
            success: true,
            data: livrosFiltrados
        };
    }

    /**
     * Busca livros por faixa de preço
     */
    async getLivrosByPreco(precoMin, precoMax) {
        const livros = await this.getLivros();
        if (!livros.success) return livros;

        const livrosFiltrados = livros.data.filter(livro => 
            livro.PRECO >= precoMin && livro.PRECO <= precoMax
        );

        return {
            success: true,
            data: livrosFiltrados
        };
    }

    /**
     * Estatísticas gerais
     */
    async getEstatisticas() {
        try {
            const [estados, cidades, usuarios, autores, categorias, livros] = await Promise.all([
                this.getEstados(),
                this.getCidades(),
                this.getUsuarios(),
                this.getAutores(),
                this.getCategorias(),
                this.getLivros()
            ]);

            return {
                success: true,
                data: {
                    total_estados: estados.success ? estados.data.length : 0,
                    total_cidades: cidades.success ? cidades.data.length : 0,
                    total_usuarios: usuarios.success ? usuarios.data.length : 0,
                    total_autores: autores.success ? autores.data.length : 0,
                    total_categorias: categorias.success ? categorias.data.length : 0,
                    total_livros: livros.success ? livros.data.length : 0
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// ==================== EXEMPLOS DE USO ====================

/**
 * Exemplos de como usar a classe BibliotecaAPI
 */
class ExemplosUso {
    constructor() {
        this.api = new BibliotecaAPI();
    }

    async exemploBasico() {
        console.log('=== Exemplo Básico ===');
        
        // Verificar se API está funcionando
        const health = await this.api.health();
        console.log('Health check:', health);
        
        // Listar estados
        const estados = await this.api.getEstados();
        console.log('Estados:', estados);
        
        // Criar novo estado
        const novoEstado = await this.api.createEstado('Santa Catarina');
        console.log('Novo estado:', novoEstado);
    }

    async exemploCompleto() {
        console.log('=== Exemplo Completo ===');
        
        try {
            // 1. Criar estado
            console.log('1. Criando estado...');
            const estado = await this.api.createEstado('Goiás');
            
            // 2. Criar usuário
            console.log('2. Criando usuário...');
            const usuario = await this.api.createUsuario(
                'teste123',
                'senha123', 
                'Usuário Teste',
                'teste@email.com'
            );
            
            // 3. Criar autor
            console.log('3. Criando autor...');
            const autor = await this.api.createAutor('Érico Veríssimo');
            
            // 4. Obter estatísticas
            console.log('4. Obtendo estatísticas...');
            const stats = await this.api.getEstatisticas();
            console.log('Estatísticas:', stats);
            
        } catch (error) {
            console.error('Erro no exemplo:', error);
        }
    }

    async exemploComImagem() {
        console.log('=== Exemplo com Imagem ===');
        
        // Simular upload de imagem
        const imagemFake = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
        
        const categoria = await this.api.createCategoria('Terror', imagemFake);
        console.log('Categoria com imagem:', categoria);
    }
}

// Disponibilizar globalmente se estiver no browser
if (typeof window !== 'undefined') {
    window.BibliotecaAPI = BibliotecaAPI;
    window.ExemplosUso = ExemplosUso;
}

// Exportar para Node.js se estiver em ambiente de módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BibliotecaAPI, ExemplosUso };
}

// ==================== EXEMPLO DE USO RÁPIDO ====================

/*
// Inicializar API
const api = new BibliotecaAPI();

// Usar async/await
async function exemplo() {
    // Verificar status
    const status = await api.health();
    console.log(status);
    
    // Listar livros
    const livros = await api.getLivros();
    if (livros.success) {
        console.log('Livros encontrados:', livros.data.length);
    } else {
        console.error('Erro:', livros.error);
    }
    
    // Criar usuário
    const novoUsuario = await api.createUsuario(
        'joao123',
        'senha123',
        'João Silva',
        'joao@email.com'
    );
    
    if (novoUsuario.success) {
        console.log('Usuário criado com sucesso!');
    }
}

// Executar exemplo
exemplo();
*/