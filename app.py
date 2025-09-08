from flask import Flask, request, jsonify, g, render_template
import sqlite3
import os
import base64
from werkzeug.exceptions import BadRequest
import requests


app = Flask(__name__)
app.config['DATABASE'] = 'biblioteca.db'


## conectar com Banco de Dados
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


## fechar banco
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
## fechar banco no caso de erros/excecoes
@app.teardown_appcontext
def close_db_context(error):
    close_db()


## configurar Banco de Dados
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

## converter resultado para dict
def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

## retornar infos do CEP
class CEP:
	@staticmethod
	def getDadosCEP(cep):
		url_api = (f'https://brasilapi.com.br/api/cep/v1/{cep}')
		try:
			req = requests.get(url_api, headers={"User-Agent": "PythonApp/1.0"}, timeout=5)
			req.raise_for_status()
			dados_json = req.json()
			if "erro" not in dados_json:
				return {"CEP": {dados_json["cep"]},
						"Bairro": {dados_json["neighborhood"]},
						"Cidade": {dados_json["city"]},
						"Estado": {dados_json["state"]}}
			else:
				return {"erro": "cep"}
		except requests.exceptions.RequestException as e:
			return {"CEP": cep,
		   			"erro": "CEP inválido"}
	
	def __new__(cls):
		raise TypeError("Não é possível instanciar esta classe")

# ==================== ESTADO ENDPOINTS ====================

@app.route('/estados', methods=['GET'])
def get_estados():
    db = get_db()
    estados = db.execute('SELECT * FROM ESTADO ORDER BY NM_ESTADO').fetchall()
    return jsonify([row_to_dict(row) for row in estados])

@app.route('/estados/<int:id_estado>', methods=['GET'])
def get_estado(id_estado):
    db = get_db()
    estado = db.execute('SELECT * FROM ESTADO WHERE ID_ESTADO = ?', (id_estado,)).fetchone()
    if estado is None:
        return jsonify({'error': 'Estado não encontrado'}), 404
    return jsonify(row_to_dict(estado))

@app.route('/estados', methods=['POST'])
def create_estado():
    data = request.get_json()
    if not data or 'nm_estado' not in data:
        return jsonify({'error': 'Nome do estado é obrigatório'}), 400
    
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO ESTADO (NM_ESTADO) VALUES (?)',
            (data['nm_estado'],)
        )
        db.commit()
        return jsonify({'id_estado': cursor.lastrowid, 'message': 'Estado criado com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/estados/<int:id_estado>', methods=['PUT'])
def update_estado(id_estado):
    data = request.get_json()
    if not data or 'nm_estado' not in data:
        return jsonify({'error': 'Nome do estado é obrigatório'}), 400
    
    db = get_db()
    try:
        db.execute(
            'UPDATE ESTADO SET NM_ESTADO = ? WHERE ID_ESTADO = ?',
            (data['nm_estado'], id_estado)
        )
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Estado não encontrado'}), 404
        return jsonify({'message': 'Estado atualizado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/estados/<int:id_estado>', methods=['DELETE'])
def delete_estado(id_estado):
    db = get_db()
    try:
        db.execute('DELETE FROM ESTADO WHERE ID_ESTADO = ?', (id_estado,))
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Estado não encontrado'}), 404
        return jsonify({'message': 'Estado deletado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== CIDADE ENDPOINTS ====================

@app.route('/cidades', methods=['GET'])
def get_cidades():
    db = get_db()
    cidades = db.execute('''
        SELECT c.*, e.NM_ESTADO 
        FROM CIDADE c 
        JOIN ESTADO e ON c.ID_ESTADO = e.ID_ESTADO 
        ORDER BY c.NM_CIDADE
    ''').fetchall()
    return jsonify([row_to_dict(row) for row in cidades])

@app.route('/cidades/<int:id_cidade>', methods=['GET'])
def get_cidade(id_cidade):
    db = get_db()
    cidade = db.execute('''
        SELECT c.*, e.NM_ESTADO 
        FROM CIDADE c 
        JOIN ESTADO e ON c.ID_ESTADO = e.ID_ESTADO 
        WHERE c.ID_CIDADE = ?
    ''', (id_cidade,)).fetchone()
    if cidade is None:
        return jsonify({'error': 'Cidade não encontrada'}), 404
    return jsonify(row_to_dict(cidade))

@app.route('/cidades', methods=['POST'])
def create_cidade():
    data = request.get_json()
    if not data or 'nm_cidade' not in data or 'id_estado' not in data:
        return jsonify({'error': 'Nome da cidade e ID do estado são obrigatórios'}), 400
    
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO CIDADE (NM_CIDADE, ID_ESTADO) VALUES (?, ?)',
            (data['nm_cidade'], data['id_estado'])
        )
        db.commit()
        return jsonify({'id_cidade': cursor.lastrowid, 'message': 'Cidade criada com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/cidades/<int:id_cidade>', methods=['PUT'])
def update_cidade(id_cidade):
    data = request.get_json()
    if not data or 'nm_cidade' not in data or 'id_estado' not in data:
        return jsonify({'error': 'Nome da cidade e ID do estado são obrigatórios'}), 400
    
    db = get_db()
    try:
        db.execute(
            'UPDATE CIDADE SET NM_CIDADE = ?, ID_ESTADO = ? WHERE ID_CIDADE = ?',
            (data['nm_cidade'], data['id_estado'], id_cidade)
        )
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Cidade não encontrada'}), 404
        return jsonify({'message': 'Cidade atualizada com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/cidades/<int:id_cidade>', methods=['DELETE'])
def delete_cidade(id_cidade):
    db = get_db()
    try:
        db.execute('DELETE FROM CIDADE WHERE ID_CIDADE = ?', (id_cidade,))
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Cidade não encontrada'}), 404
        return jsonify({'message': 'Cidade deletada com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== BAIRRO ENDPOINTS ====================

@app.route('/bairros', methods=['GET'])
def get_bairros():
    db = get_db()
    bairros = db.execute('''
        SELECT b.*, c.NM_CIDADE, e.NM_ESTADO 
        FROM BAIRRO b 
        JOIN CIDADE c ON b.ID_CIDADE = c.ID_CIDADE 
        JOIN ESTADO e ON c.ID_ESTADO = e.ID_ESTADO 
        ORDER BY b.NM_BAIRRO
    ''').fetchall()
    return jsonify([row_to_dict(row) for row in bairros])

@app.route('/bairros/<int:cep>', methods=['GET'])
def get_bairro(cep):
    db = get_db()
    bairro = db.execute('''
        SELECT b.*, c.NM_CIDADE, e.NM_ESTADO 
        FROM BAIRRO b 
        JOIN CIDADE c ON b.ID_CIDADE = c.ID_CIDADE 
        JOIN ESTADO e ON c.ID_ESTADO = e.ID_ESTADO 
        WHERE b.CEP = ?
    ''', (cep,)).fetchone()
    if bairro is None:
        return jsonify({'error': 'Bairro não encontrado'}), 404
    return jsonify(row_to_dict(bairro))

@app.route('/bairros', methods=['POST'])
def create_bairro():
    data = request.get_json()
    if not data or 'cep' not in data or 'nm_bairro' not in data or 'id_cidade' not in data:
        return jsonify({'error': 'CEP, nome do bairro e ID da cidade são obrigatórios'}), 400
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO BAIRRO (CEP, NM_BAIRRO, ID_CIDADE) VALUES (?, ?, ?)',
            (data['cep'], data['nm_bairro'], data['id_cidade'])
        )
        db.commit()
        return jsonify({'message': 'Bairro criado com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/bairros/<int:cep>', methods=['PUT'])
def update_bairro(cep):
    data = request.get_json()
    if not data or 'nm_bairro' not in data or 'id_cidade' not in data:
        return jsonify({'error': 'Nome do bairro e ID da cidade são obrigatórios'}), 400
    
    db = get_db()
    try:
        db.execute(
            'UPDATE BAIRRO SET NM_BAIRRO = ?, ID_CIDADE = ? WHERE CEP = ?',
            (data['nm_bairro'], data['id_cidade'], cep)
        )
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Bairro não encontrado'}), 404
        return jsonify({'message': 'Bairro atualizado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/bairros/<int:cep>', methods=['DELETE'])
def delete_bairro(cep):
    db = get_db()
    try:
        db.execute('DELETE FROM BAIRRO WHERE CEP = ?', (cep,))
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Bairro não encontrado'}), 404
        return jsonify({'message': 'Bairro deletado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== USUARIO ENDPOINTS ====================

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    db = get_db()
    usuarios = db.execute('SELECT LOGIN, NM_USUARIO, EMAIL_CONTATO FROM USUARIO ORDER BY NM_USUARIO').fetchall()
    return jsonify([row_to_dict(row) for row in usuarios])

@app.route('/usuarios/<login>', methods=['GET'])
def get_usuario(login):
    db = get_db()
    usuario = db.execute('SELECT LOGIN, NM_USUARIO, EMAIL_CONTATO FROM USUARIO WHERE LOGIN = ?', (login,)).fetchone()
    if usuario is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(row_to_dict(usuario))

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    if not data or 'login' not in data or 'senha' not in data or 'nm_usuario' not in data:
        return jsonify({'error': 'Login, senha e nome do usuário são obrigatórios'}), 400
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO USUARIO (LOGIN, SENHA, NM_USUARIO, EMAIL_CONTATO) VALUES (?, ?, ?, ?)',
            (data['login'], data['senha'], data['nm_usuario'], data.get('email_contato'))
        )
        db.commit()
        return jsonify({'message': 'Usuário criado com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/usuarios/<login>', methods=['PUT'])
def update_usuario(login):
    data = request.get_json()
    if not data or 'nm_usuario' not in data:
        return jsonify({'error': 'Nome do usuário é obrigatório'}), 400
    
    db = get_db()
    try:
        query = 'UPDATE USUARIO SET NM_USUARIO = ?, EMAIL_CONTATO = ?'
        params = [data['nm_usuario'], data.get('email_contato')]
        
        if 'senha' in data:
            query += ', SENHA = ?'
            params.append(data['senha'])
        
        query += ' WHERE LOGIN = ?'
        params.append(login)
        
        db.execute(query, params)
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify({'message': 'Usuário atualizado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/usuarios/<login>', methods=['DELETE'])
def delete_usuario(login):
    db = get_db()
    try:
        db.execute('DELETE FROM USUARIO WHERE LOGIN = ?', (login,))
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify({'message': 'Usuário deletado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== AUTOR ENDPOINTS ====================

@app.route('/autores', methods=['GET'])
def get_autores():
    db = get_db()
    autores = db.execute('SELECT * FROM AUTOR ORDER BY NM_AUTOR').fetchall()
    return jsonify([row_to_dict(row) for row in autores])

@app.route('/autores/<int:id_autor>', methods=['GET'])
def get_autor(id_autor):
    db = get_db()
    autor = db.execute('SELECT * FROM AUTOR WHERE ID_AUTOR = ?', (id_autor,)).fetchone()
    if autor is None:
        return jsonify({'error': 'Autor não encontrado'}), 404
    return jsonify(row_to_dict(autor))

@app.route('/autores', methods=['POST'])
def create_autor():
    data = request.get_json()
    if not data or 'nm_autor' not in data:
        return jsonify({'error': 'Nome do autor é obrigatório'}), 400
    
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO AUTOR (NM_AUTOR) VALUES (?)',
            (data['nm_autor'],)
        )
        db.commit()
        return jsonify({'id_autor': cursor.lastrowid, 'message': 'Autor criado com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/autores/<int:id_autor>', methods=['PUT'])
def update_autor(id_autor):
    data = request.get_json()
    if not data or 'nm_autor' not in data:
        return jsonify({'error': 'Nome do autor é obrigatório'}), 400
    
    db = get_db()
    try:
        db.execute(
            'UPDATE AUTOR SET NM_AUTOR = ? WHERE ID_AUTOR = ?',
            (data['nm_autor'], id_autor)
        )
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Autor não encontrado'}), 404
        return jsonify({'message': 'Autor atualizado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/autores/<int:id_autor>', methods=['DELETE'])
def delete_autor(id_autor):
    db = get_db()
    try:
        db.execute('DELETE FROM AUTOR WHERE ID_AUTOR = ?', (id_autor,))
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Autor não encontrado'}), 404
        return jsonify({'message': 'Autor deletado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== CATEGORIA ENDPOINTS ====================

@app.route('/categorias', methods=['GET'])
def get_categorias():
    db = get_db()
    categorias = db.execute('SELECT ID_CATEGORIA, NM_CATEGORIA FROM CATEGORIA ORDER BY NM_CATEGORIA').fetchall()
    result = []
    for row in categorias:
        categoria = row_to_dict(row)
        # Get image separately to avoid loading all images at once
        result.append(categoria)
    return jsonify(result)

@app.route('/categorias/<int:id_categoria>', methods=['GET'])
def get_categoria(id_categoria):
    db = get_db()
    categoria = db.execute('SELECT * FROM CATEGORIA WHERE ID_CATEGORIA = ?', (id_categoria,)).fetchone()
    if categoria is None:
        return jsonify({'error': 'Categoria não encontrada'}), 404
    
    result = row_to_dict(categoria)
    if result['IMG_CATEGORIA']:
        result['IMG_CATEGORIA'] = base64.b64encode(result['IMG_CATEGORIA']).decode('utf-8')
    return jsonify(result)

@app.route('/categorias', methods=['POST'])
def create_categoria():
    data = request.get_json()
    if not data or 'nm_categoria' not in data or 'img_categoria' not in data:
        return jsonify({'error': 'Nome da categoria e imagem são obrigatórios'}), 400
    
    try:
        img_data = base64.b64decode(data['img_categoria'])
    except:
        return jsonify({'error': 'Imagem deve estar em base64'}), 400
    
    db = get_db()
    try:
        cursor = db.execute(
            'INSERT INTO CATEGORIA (NM_CATEGORIA, IMG_CATEGORIA) VALUES (?, ?)',
            (data['nm_categoria'], img_data)
        )
        db.commit()
        return jsonify({'id_categoria': cursor.lastrowid, 'message': 'Categoria criada com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/categorias/<int:id_categoria>', methods=['PUT'])
def update_categoria(id_categoria):
    data = request.get_json()
    if not data or 'nm_categoria' not in data:
        return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
    
    db = get_db()
    try:
        if 'img_categoria' in data:
            try:
                img_data = base64.b64decode(data['img_categoria'])
                db.execute(
                    'UPDATE CATEGORIA SET NM_CATEGORIA = ?, IMG_CATEGORIA = ? WHERE ID_CATEGORIA = ?',
                    (data['nm_categoria'], img_data, id_categoria)
                )
            except:
                return jsonify({'error': 'Imagem deve estar em base64'}), 400
        else:
            db.execute(
                'UPDATE CATEGORIA SET NM_CATEGORIA = ? WHERE ID_CATEGORIA = ?',
                (data['nm_categoria'], id_categoria)
            )
        
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        return jsonify({'message': 'Categoria atualizada com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/categorias/<int:id_categoria>', methods=['DELETE'])
def delete_categoria(id_categoria):
    db = get_db()
    try:
        db.execute('DELETE FROM CATEGORIA WHERE ID_CATEGORIA = ?', (id_categoria,))
        db.commit()
        if db.total_changes == 0:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        return jsonify({'message': 'Categoria deletada com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== LIVRO ENDPOINTS ====================

@app.route('/livros', methods=['GET'])
def get_livros():
    db = get_db()
    livros = db.execute('''
        SELECT l.ID_LIVRO, l.NM_LIVRO, l.PRECO, l.PAGAMENTO_ELETRONICO, 
               l.PAGAMENTO_DINHEIRO, l.ENTREGA_PRESENCIAL, l.ENTREGA_DELIVERY,
               l.CEP, l.LOGIN_COMPRADOR, l.LOGIN_VENDEDOR,
               b.NM_BAIRRO, c.NM_CIDADE, e.NM_ESTADO
        FROM LIVRO l 
        JOIN BAIRRO b ON l.CEP = b.CEP
        JOIN CIDADE c ON b.ID_CIDADE = c.ID_CIDADE
        JOIN ESTADO e ON c.ID_ESTADO = e.ID_ESTADO
        ORDER BY l.NM_LIVRO
    ''').fetchall()
    return jsonify([row_to_dict(row) for row in livros])

@app.route('/livros/<int:id_livro>', methods=['GET'])
def get_livro(id_livro):
    db = get_db()
    livro = db.execute('''
        SELECT l.*, b.NM_BAIRRO, c.NM_CIDADE, e.NM_ESTADO
        FROM LIVRO l 
        JOIN BAIRRO b ON l.CEP = b.CEP
        JOIN CIDADE c ON b.ID_CIDADE = c.ID_CIDADE
        JOIN ESTADO e ON c.ID_ESTADO = e.ID_ESTADO
        WHERE l.ID_LIVRO = ?
    ''', (id_livro,)).fetchone()
    if livro is None:
        return jsonify({'error': 'Livro não encontrado'}), 404
    
    result = row_to_dict(livro)
    if result['IMG_LIVRO']:
        result['IMG_LIVRO'] = base64.b64encode(result['IMG_LIVRO']).decode('utf-8')
    
    # Get authors
    autores = db.execute('''
        SELECT a.* FROM AUTOR a 
        JOIN LIVRO_AUTOR la ON a.ID_AUTOR = la.ID_AUTOR 
        WHERE la.ID_LIVRO = ?
    ''', (id_livro,)).fetchall()
    result['autores'] = [row_to_dict(row) for row in autores]
    
    # Get categories
    categorias = db.execute('''
        SELECT c.ID_CATEGORIA, c.NM_CATEGORIA FROM CATEGORIA c 
        JOIN LIVRO_CATEGORIA lc ON c.ID_CATEGORIA = lc.ID_CATEGORIA 
        WHERE lc.ID_LIVRO = ?
    ''', (id_livro,)).fetchall()
    result['categorias'] = [row_to_dict(row) for row in categorias]
    
    return jsonify(result)

@app.route('/livros', methods=['POST'])
def create_livro():
    data = request.get_json()
    required_fields = ['nm_livro', 'preco', 'pagamento_eletronico', 'pagamento_dinheiro', 
                      'entrega_presencial', 'entrega_delivery', 'img_livro', 'cep', 
                      'login_comprador', 'login_vendedor']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    try:
        img_data = base64.b64decode(data['img_livro'])
    except:
        return jsonify({'error': 'Imagem deve estar em base64'}), 400
    
    db = get_db()
    try:
        cursor = db.execute('''
            INSERT INTO LIVRO (NM_LIVRO, PRECO, PAGAMENTO_ELETRONICO, PAGAMENTO_DINHEIRO, 
                              ENTREGA_PRESENCIAL, ENTREGA_DELIVERY, IMG_LIVRO, CEP, 
                              LOGIN_COMPRADOR, LOGIN_VENDEDOR) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['nm_livro'], data['preco'], data['pagamento_eletronico'], 
              data['pagamento_dinheiro'], data['entrega_presencial'], data['entrega_delivery'],
              img_data, data['cep'], data['login_comprador'], data['login_vendedor']))
        
        id_livro = cursor.lastrowid
        
        # Add authors if provided
        if 'autores' in data:
            for id_autor in data['autores']:
                db.execute('INSERT INTO LIVRO_AUTOR (ID_AUTOR, ID_LIVRO) VALUES (?, ?)', 
                          (id_autor, id_livro))
        
        # Add categories if provided
        if 'categorias' in data:
            for id_categoria in data['categorias']:
                db.execute('INSERT INTO LIVRO_CATEGORIA (ID_CATEGORIA, ID_LIVRO) VALUES (?, ?)', 
                          (id_categoria, id_livro))
        
        db.commit()
        return jsonify({'id_livro': id_livro, 'message': 'Livro criado com sucesso'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/livros/<int:id_livro>', methods=['PUT'])
def update_livro(id_livro):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados são obrigatórios'}), 400
    
    db = get_db()
    try:
        # Update main fields
        update_fields = []
        params = []
        
        for field in ['nm_livro', 'preco', 'pagamento_eletronico', 'pagamento_dinheiro', 
                     'entrega_presencial', 'entrega_delivery', 'cep', 'login_comprador', 'login_vendedor']:
            if field in data:
                update_fields.append(f'{field.upper()} = ?')
                params.append(data[field])
        
        if 'img_livro' in data:
            try:
                img_data = base64.b64decode(data['img_livro'])
                update_fields.append('IMG_LIVRO = ?')
                params.append(img_data)
            except:
                return jsonify({'error': 'Imagem deve estar em base64'}), 400
        
        if update_fields:
            params.append(id_livro)
            db.execute(f'UPDATE LIVRO SET {", ".join(update_fields)} WHERE ID_LIVRO = ?', params)
        
        # Update authors if provided
        if 'autores' in data:
            db.execute('DELETE FROM LIVRO_AUTOR WHERE ID_LIVRO = ?', (id_livro,))
            for id_autor in data['autores']:
                db.execute('INSERT INTO LIVRO_AUTOR (ID_AUTOR, ID_LIVRO) VALUES (?, ?)', 
                          (id_autor, id_livro))
        
        # Update categories if provided
        if 'categorias' in data:
            db.execute('DELETE FROM LIVRO_CATEGORIA WHERE ID_LIVRO = ?', (id_livro,))
            for id_categoria in data['categorias']:
                db.execute('INSERT INTO LIVRO_CATEGORIA (ID_CATEGORIA, ID_LIVRO) VALUES (?, ?)', 
                          (id_categoria, id_livro))
        
        db.commit()
        return jsonify({'message': 'Livro atualizado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/livros/<int:id_livro>', methods=['DELETE'])
def delete_livro(id_livro):
    db = get_db()
    try:
        # Delete relationships first
        db.execute('DELETE FROM LIVRO_AUTOR WHERE ID_LIVRO = ?', (id_livro,))
        db.execute('DELETE FROM LIVRO_CATEGORIA WHERE ID_LIVRO = ?', (id_livro,))
        
        # Delete main record
        db.execute('DELETE FROM LIVRO WHERE ID_LIVRO = ?', (id_livro,))
        db.commit()
        
        if db.total_changes == 0:
            return jsonify({'error': 'Livro não encontrado'}), 404
        return jsonify({'message': 'Livro deletado com sucesso'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ==================== ROTAS DE TESTE ====================

@app.route('/dados', methods=['GET'])
def index():
    return jsonify({
        'message': 'API da Biblioteca funcionando!',
        'endpoints': {
            'estados': '/estados',
            'cidades': '/cidades', 
            'usuarios': '/usuarios',
            'autores': '/autores',
            'categorias': '/categorias',
            'livros': '/livros',
            'health': '/health'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'API funcionando corretamente'})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Requisição inválida'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

## template da api
@app.route("/api")
def api_page():
    return render_template("index.html")

## template do app
@app.route("/")
def app_page():
    return render_template("app.html")

if __name__ == '__main__':
    if os.path.exists(app.config['DATABASE']):
        print("Removendo banco existente...")
        os.remove(app.config['DATABASE'])
    
    init_db()
    print("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=5000)