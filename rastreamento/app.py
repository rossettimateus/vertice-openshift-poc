import os
import logging
import re
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16384
logging.basicConfig(level=logging.INFO)
VERSION = os.getenv('APP_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('APP_ENV', 'local')
FAIL = os.getenv('FAIL_MODE', 'none')
if FAIL not in ('none', 'readiness', 'business'):
    raise ValueError('FAIL_MODE deve ser none, readiness ou business')


def connection():
    return psycopg.connect(host=os.environ['DB_HOST'], port=os.getenv('DB_PORT', '5432'),
        dbname=os.environ['DB_NAME'], user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
        connect_timeout=3, options='-c statement_timeout=3000', row_factory=dict_row)


@app.after_request
def log_request(response):
    app.logger.info('method=%s path=%s status=%s version=%s environment=%s',
                    request.method, request.path, response.status_code, VERSION, ENVIRONMENT)
    response.headers['X-App-Version'] = VERSION
    return response


@app.errorhandler(psycopg.Error)
def db_error(error):
    # Não registra strings de conexão, senhas nem conteúdo enviado pelo usuário.
    app.logger.error('database_error type=%s', type(error).__name__)
    return jsonify(erro='Banco indisponível ou esquema não inicializado'), 503


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(erro=error.description), error.code


@app.get('/healthz')
def health():
    return jsonify(status='alive')


@app.get('/readyz')
def ready():
    if FAIL == 'readiness':
        return jsonify(status='not_ready', motivo='falha controlada'), 503
    with connection() as conn:
        conn.execute('SELECT codigo FROM entregas LIMIT 1')
    return jsonify(status='ready')


@app.get('/')
@app.get('/version')
def version():
    return jsonify(servico='rastreamento', versao=VERSION, ambiente=ENVIRONMENT)


@app.before_request
def broken_release():
    if FAIL == 'business' and request.path.startswith('/entregas'):
        return jsonify(erro='Falha funcional controlada nesta versão'), 500


def valid_code(code):
    return bool(re.fullmatch(r'ENT-\d{3}', code))


@app.get('/entregas')
def deliveries():
    with connection() as conn:
        rows = conn.execute('SELECT codigo, origem, destino, status FROM entregas ORDER BY codigo').fetchall()
    return jsonify(entregas=rows)


@app.get('/entregas/<code>')
def delivery(code):
    if not valid_code(code):
        return jsonify(erro='Código inválido; exemplo: ENT-001'), 400
    with connection() as conn:
        row = conn.execute('SELECT * FROM entregas WHERE codigo=%s', (code,)).fetchone()
        if row is None:
            return jsonify(erro='Entrega não encontrada'), 404
        row['ocorrencias'] = conn.execute(
            'SELECT id, descricao, criado_em FROM ocorrencias WHERE entrega_codigo=%s ORDER BY id', (code,)).fetchall()
        for event in row['ocorrencias']:
            event['criado_em'] = event['criado_em'].isoformat()
    return jsonify(row)


@app.post('/entregas/<code>/ocorrencias')
def add_event(code):
    if not valid_code(code):
        return jsonify(erro='Código inválido'), 400
    data = request.get_json(silent=True)
    description = data.get('descricao') if isinstance(data, dict) else None
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 500:
        return jsonify(erro='descricao deve ter entre 1 e 500 caracteres'), 400
    with connection() as conn:
        if conn.execute('SELECT codigo FROM entregas WHERE codigo=%s', (code,)).fetchone() is None:
            return jsonify(erro='Entrega não encontrada'), 404
        row = conn.execute('INSERT INTO ocorrencias (entrega_codigo, descricao) VALUES (%s,%s) RETURNING id',
                           (code, description.strip())).fetchone()
    return jsonify(id=row['id'], descricao=description.strip()), 201
