from flask import Flask, render_template, redirect, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

app.config['dados_usuario'] = []

UPLOAD = 'static/assets'
app.config['UPLOAD'] = UPLOAD

# Função para inicializar o banco de dados
def inicializar_banco():
    if not os.path.exists('models'):
        os.makedirs('models')  # Cria a pasta models se não existir
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    # Criação da tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    );
    ''')

    # Criação da tabela de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_clientes (
        cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        telefone TEXT,
        rua TEXT,
        numero TEXT,
        cidade TEXT,
        estado TEXT,
        cep TEXT,
        data_cadastro TEXT,
        cpf TEXT,
        usuario_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES tb_usuario(id) ON DELETE CASCADE
    );
    ''')

    # Criação da tabela de fornecedores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_fornecedores (
        fornecedor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        site TEXT,
        rua TEXT,
        numero TEXT,
        cidade TEXT,
        estado TEXT,
        cep TEXT,
        cnpj TEXT,
        data_cadastro TEXT,
        usuario_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES tb_usuario(id) ON DELETE CASCADE
    );
    ''')

    conexao.commit()
    conexao.close()

# Inicializa o banco de dados ao iniciar o app
inicializar_banco()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conexao = sqlite3.connect('models/projeto.db')
        cursor = conexao.cursor()

        # Verifica se o usuário e senha existem
        sql = "SELECT * FROM tb_usuario WHERE usuario=? AND senha=?"
        cursor.execute(sql, (usuario, senha))
        dados_usuario = cursor.fetchone()

        if dados_usuario:
            app.config['dados_usuario'] = dados_usuario
            return redirect('/bem_vindo')  # Redireciona para a página de boas-vindas
        else:
            return "Login ou senha incorretos.", 401
    return render_template('index.html')

@app.route('/bem_vindo')
def bem_vindo():
    if not app.config['dados_usuario']:
        return redirect('/')
    return render_template('bem_vindo.html', usuario=app.config['dados_usuario'])

@app.route('/pre_cadastro', methods=['GET', 'POST'])
def pre_cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        senha = request.form['senha']

        nome_imagem = None
        imagem = request.files.get('imagem')
        
        if imagem:
            extensao = imagem.filename.split('.')[-1]
            nome_imagem = f"{nome.strip().lower().replace(' ', '_')}.{extensao}"
            caminho_imagem = os.path.join(app.config['UPLOAD'], nome_imagem)
            imagem.save(caminho_imagem)

        conexao = sqlite3.connect('models/projeto.db')
        cursor = conexao.cursor()

        sql = '''INSERT INTO tb_usuario (nome, usuario, senha, imagem) 
                VALUES (?, ?, ?, ?)'''
        cursor.execute(sql, (nome, usuario, senha, nome_imagem))

        conexao.commit()
        conexao.close()

        return redirect('/')
    return render_template('pre_cadastro.html')

@app.route('/cadastro_cl')
def cadastro_cl():
    if not app.config['dados_usuario']:
        return redirect('/')
    return render_template('cadastro_cl.html', usuario=app.config['dados_usuario'])

@app.route("/cadastro_cliente", methods=['POST'])
def enviar_cliente():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    rua = request.form['end_rua']
    num = request.form['end_num']
    cid = request.form['end_cid']
    est = request.form['end_est']
    cep = request.form['end_cep']
    cpf = request.form['cpf']

    data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    sql = '''INSERT INTO tb_clientes 
             (nome, email, telefone, rua, numero, cidade, estado, cep, data_cadastro, cpf) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor.execute(sql, (nome, email, telefone, rua, num, cid, est, cep, data_cadastro, cpf))

    conexao.commit()
    conexao.close()

    return redirect('/consulta_cl')

@app.route('/consulta_cl')
def consulta_clientes():
    if not app.config['dados_usuario']:
        return redirect('/')

    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    sql = 'SELECT * FROM tb_clientes'
    cursor.execute(sql)
    clientes = cursor.fetchall()

    conexao.close()

    return render_template("consulta_cl.html", clientes=clientes, usuario=app.config['dados_usuario'])

@app.route('/ver_cl/<int:id>', methods=['GET', 'POST'])
def ver(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tb_clientes WHERE cliente_id = ?", (id,))
    clientes = cursor.fetchone()
    conexao.close()
    return render_template('ver_cl.html', clientes=clientes, usuario = app.config['dados_usuario'])


@app.route('/editar_cl/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
 
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        rua = request.form['end_rua']
        num = request.form['end_num']
        cid = request.form['end_cid']
        est = request.form['end_est']
        cep = request.form['end_cep']
        cpf = request.form['cpf']

        sql = "UPDATE tb_clientes SET nome = ?, email = ?, telefone = ?, rua=?, numero=?, cidade=?, estado=?, cep=?, cpf=? WHERE cliente_id = ?"
        cursor.execute(sql, (nome, email, telefone, rua, num, cid, est, cep, cpf, id))
 
        conexao.commit()
        conexao.close()
 
        return redirect('/consulta_cl')
    else:
        cursor.execute("SELECT * FROM tb_clientes WHERE cliente_id = ?", (id,))
        clientes = cursor.fetchone()
        conexao.close()
        
        return render_template('editar_cl.html', clientes = clientes, usuario = app.config['dados_usuario'])
    
@app.route('/excluir_cl/<int:id>', methods=['GET'])
def excluir(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
 
    sql = 'DELETE FROM tb_clientes WHERE cliente_id = ?'
    cursor.execute(sql, (id,))
 
    conexao.commit()
    conexao.close()
 
    return redirect('/consulta_cl')


@app.route('/cadastro_fn')
def cadastro_fn():
    if not app.config['dados_usuario']:
        return redirect('/')
    return render_template('cadastro_fn.html', usuario=app.config['dados_usuario'])


@app.route("/cadastro_fornecedor", methods=['POST'])
def enviar_fornecedor():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    site = request.form['site']
    rua = request.form['end_rua']
    num = request.form['end_num']
    cid = request.form['end_cid']
    est = request.form['end_est']
    cep = request.form['end_cep']
    cnpj = request.form['cnpj']
    usuario_id = app.config['dados_usuario'][0]

    data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    sql = '''INSERT INTO tb_fornecedores 
             (nome, email, telefone, site, rua, numero, cidade, estado, cep, cnpj, data_cadastro, usuario_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cursor.execute(sql, (nome, email, telefone, site, rua, num, cid, est, cep, cnpj, data_cadastro, usuario_id))

    conexao.commit()
    conexao.close()

    return redirect('/consulta_fn')


@app.route('/consulta_fn')
def consulta_fornecedores():
    if not app.config['dados_usuario']:
        return redirect('/')

    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    sql = 'SELECT * FROM tb_fornecedores'
    cursor.execute(sql)
    fornecedores = cursor.fetchall()

    conexao.close()

    return render_template("consulta_fn.html", fornecedores=fornecedores, usuario=app.config['dados_usuario'])

@app.route('/ver_fn/<int:id>', methods=['GET', 'POST'])
def ver_fn(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tb_fornecedores WHERE fornecedor_id = ?", (id,))
    fornecedores = cursor.fetchone()
    conexao.close()
    return render_template('ver_fn.html', fornecedores=fornecedores, usuario = app.config['dados_usuario'])


@app.route('/editar_fn/<int:id>', methods=['GET', 'POST'])
def editar_fn(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
 
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        site = request.form['site']
        rua = request.form['end_rua']
        num = request.form['end_num']
        cid = request.form['end_cid']
        est = request.form['end_est']
        cep = request.form['end_cep']
        cnpj = request.form['cnpj']

        sql = "UPDATE tb_fornecedores SET nome = ?, email = ?, telefone = ?, site=?, rua=?, numero=?, cidade=?, estado=?, cep=?, cnpj=? WHERE fornecedor_id = ?"
        cursor.execute(sql, (nome, email, telefone, site, rua, num, cid, est, cep, cnpj, id))
 
        conexao.commit()
        conexao.close()
 
        return redirect('/consulta_fn')
    else:
        cursor.execute("SELECT * FROM tb_fornecedores WHERE fornecedor_id = ?", (id,))
        fornecedores = cursor.fetchone()
        conexao.close()
        
        return render_template('editar_fn.html', fornecedores = fornecedores, usuario = app.config['dados_usuario'])


@app.route('/excluir_fn/<int:id>', methods=['GET'])
def excluir_fn(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
 
    sql = 'DELETE FROM tb_fornecedores WHERE fornecedor_id = ?'
    cursor.execute(sql, (id,))
 
    conexao.commit()
    conexao.close()
 
    return redirect('/consulta_fn')


@app.route('/cadastro_us')
def cadastro_us():
    if not app.config['dados_usuario']:
        return redirect('/')
    return render_template('cadastro_us.html', usuario=app.config['dados_usuario'])

@app.route("/cadastro_usuario", methods=['POST'])
def enviar_usuarios():
    nome = request.form['nome']
    usuario = request.form['usuario']
    senha = request.form['senha']

    nome_imagem = None
    imagem = request.files.get('imagem')
    
    if imagem:
        extensao = imagem.filename.split('.')[-1]
        nome_imagem = f"{nome.strip().lower().replace(' ', '_')}.{extensao}"
        caminho_imagem = os.path.join(app.config['UPLOAD'], nome_imagem)
        imagem.save(caminho_imagem)

    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    sql = '''INSERT INTO tb_usuario (nome, usuario, senha, imagem) 
             VALUES (?, ?, ?, ?)'''
    cursor.execute(sql, (nome, usuario, senha, nome_imagem)) 

    conexao.commit()
    conexao.close()

    return redirect('/consulta_us')

@app.route('/consulta_us')
def consulta_usuarios():
    if not app.config['dados_usuario']:
        return redirect('/')

    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()

    sql = 'SELECT * FROM tb_usuario'
    cursor.execute(sql)
    usuarinhos = cursor.fetchall()

    conexao.close()

    return render_template("consulta_us.html", usuarinhos=usuarinhos, usuario=app.config['dados_usuario'])

@app.route('/ver_us/<int:id>', methods=['GET', 'POST'])
def ver_us(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tb_usuario WHERE id = ?", (id,))
    usuarioos = cursor.fetchone()
    conexao.close()
    return render_template('ver_us.html', usuarioos=usuarioos, usuario = app.config['dados_usuario'])


@app.route('/editar_us/<int:id>', methods=['GET', 'POST'])
def editar_us(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
 
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        senha = request.form['senha']

        sql = "UPDATE tb_usuario SET nome = ?, usuario = ?, senha = ? WHERE id = ?"
        cursor.execute(sql, (nome, usuario, senha, id))
 
        conexao.commit()
        conexao.close()
 
        return redirect('/consulta_us')
    else:
        cursor.execute("SELECT * FROM tb_usuario WHERE id = ?", (id,))
        usuarinho = cursor.fetchone()
        conexao.close()
        
        return render_template('editar_us.html', usuarinho = usuarinho, usuario = app.config['dados_usuario'])
    
@app.route('/excluir_us/<int:id>', methods=['GET'])
def excluir_us(id):
    conexao = sqlite3.connect('models/projeto.db')
    cursor = conexao.cursor()
 
    sql = 'DELETE FROM tb_usuario WHERE id = ?'
    cursor.execute(sql, (id,))
 
    conexao.commit()
    conexao.close()
 
    return redirect('/consulta_us')

@app.route('/sair', methods=['POST'])
def logout():
    app.config['dados_usuario'] = []
    return redirect('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)
