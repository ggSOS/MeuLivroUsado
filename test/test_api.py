#!/usr/bin/env python3
"""
Script de teste para a API Flask
Execute este script com o servidor Flask rodando para testar todos os endpoints
"""

import requests
import json
import base64

# Configuração da API
API_BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Testa um endpoint específico"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        
        print(f"{method} {endpoint}: {response.status_code}")
        
        if response.status_code == expected_status:
            try:
                result = response.json()
                print(f"✓ Sucesso: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"✓ Sucesso: {response.text}")
        else:
            print(f"✗ Erro: {response.text}")
        
        print("-" * 80)
        return response
    
    except Exception as e:
        print(f"✗ Erro de conexão: {e}")
        print("-" * 80)
        return None

def main():
    print("=== TESTANDO API FLASK ===\n")
    
    # Teste de saúde da API
    print("1. Health Check")
    test_endpoint('GET', '/health')
    
    # Testes de Estados
    print("2. Estados")
    test_endpoint('GET', '/estados')
    
    # Criar um novo estado
    novo_estado = {"nm_estado": "Bahia"}
    response = test_endpoint('POST', '/estados', novo_estado, 201)
    estado_id = None
    if response and response.status_code == 201:
        estado_id = response.json().get('id_estado')
    
    # Buscar estado específico
    if estado_id:
        test_endpoint('GET', f'/estados/{estado_id}')
        
        # Atualizar estado
        estado_atualizado = {"nm_estado": "Bahia - Atualizado"}
        test_endpoint('PUT', f'/estados/{estado_id}', estado_atualizado)
    
    # Testes de Cidades
    print("3. Cidades")
    test_endpoint('GET', '/cidades')
    
    # Criar nova cidade
    nova_cidade = {"nm_cidade": "Salvador", "id_estado": 1}
    response = test_endpoint('POST', '/cidades', nova_cidade, 201)
    cidade_id = None
    if response and response.status_code == 201:
        cidade_id = response.json().get('id_cidade')
    
    # Testes de Bairros
    print("4. Bairros")
    test_endpoint('GET', '/bairros')
    
    # Criar novo bairro
    novo_bairro = {"cep": 40070110, "nm_bairro": "Pelourinho", "id_cidade": 1}
    test_endpoint('POST', '/bairros', novo_bairro, 201)
    
    # Testes de Usuários
    print("5. Usuários")
    test_endpoint('GET', '/usuarios')
    
    # Criar novo usuário
    novo_usuario = {
        "login": "teste123",
        "senha": "senha123",
        "nm_usuario": "Usuario Teste",
        "email_contato": "teste@email.com"
    }
    test_endpoint('POST', '/usuarios', novo_usuario, 201)
    
    # Buscar usuário específico
    test_endpoint('GET', '/usuarios/teste123')
    
    # Testes de Autores
    print("6. Autores")
    test_endpoint('GET', '/autores')
    
    # Criar novo autor
    novo_autor = {"nm_autor": "Jorge Amado"}
    response = test_endpoint('POST', '/autores', novo_autor, 201)
    autor_id = None
    if response and response.status_code == 201:
        autor_id = response.json().get('id_autor')
    
    # Testes de Categorias
    print("7. Categorias")
    test_endpoint('GET', '/categorias')
    
    # Criar nova categoria (com imagem base64 fictícia)
    imagem_base64 = base64.b64encode(b"fake_image_data").decode('utf-8')
    nova_categoria = {
        "nm_categoria": "Literatura Regional",
        "img_categoria": imagem_base64
    }
    response = test_endpoint('POST', '/categorias', nova_categoria, 201)
    categoria_id = None
    if response and response.status_code == 201:
        categoria_id = response.json().get('id_categoria')
    
    # Testes de Livros
    print("8. Livros")
    test_endpoint('GET', '/livros')
    
    # Criar novo livro
    novo_livro = {
        "nm_livro": "Gabriela, Cravo e Canela",
        "preco": 29.90,
        "pagamento_eletronico": "S",
        "pagamento_dinheiro": "S",
        "entrega_presencial": "S",
        "entrega_delivery": "N",
        "img_livro": imagem_base64,
        "cep": 1310100,
        "login_comprador": "joao123",
        "login_vendedor": "maria456"
    }
    
    if autor_id and categoria_id:
        novo_livro["autores"] = [autor_id]
        novo_livro["categorias"] = [categoria_id]
    
    response = test_endpoint('POST', '/livros', novo_livro, 201)
    livro_id = None
    if response and response.status_code == 201:
        livro_id = response.json().get('id_livro')
    
    # Buscar livro específico
    if livro_id:
        test_endpoint('GET', f'/livros/{livro_id}')
    
    print("=== TESTES CONCLUÍDOS ===")

if __name__ == "__main__":
    main()