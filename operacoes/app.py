import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16384
logging.basicConfig(level=logging.INFO)
BASE_URL = os.environ['TRACKING_API_URL'].rstrip('/')
if urlsplit(BASE_URL).scheme not in ('http', 'https'):
    raise ValueError('TRACKING_API_URL precisa começar com http:// ou https://')
VERSION = os.getenv('APP_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('APP_ENV', 'local')


def api(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(BASE_URL + path, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=4) as response:
            return json.load(response), response.status
    except HTTPError as error:
        # Erros da dependência não são apresentados literalmente ao navegador.
        return {'erro': f'Rastreamento respondeu HTTP {error.code}.'}, error.code
    except (URLError, TimeoutError, OSError, ValueError):
        return {'erro': 'Não foi possível acessar Rastreamento.'}, 503


@app.after_request
def log_request(response):
    app.logger.info('method=%s path=%s status=%s version=%s environment=%s',
                    request.method, request.path, response.status_code, VERSION, ENVIRONMENT)
    response.headers['X-App-Version'] = VERSION
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'; form-action 'self'"
    return response


@app.get('/healthz')
def health():
    return jsonify(status='alive')


@app.get('/readyz')
def ready():
    _, status = api('/readyz')
    return jsonify(status='ready' if status == 200 else 'not_ready'), 200 if status == 200 else 503


@app.get('/version')
def version():
    return jsonify(servico='operacoes', versao=VERSION, ambiente=ENVIRONMENT)


@app.get('/')
def index():
    return render_template('index.html', version=VERSION, environment=ENVIRONMENT)


@app.route('/api/entregas', methods=['GET'])
@app.route('/api/entregas/<code>', methods=['GET'])
@app.route('/api/entregas/<code>/ocorrencias', methods=['POST'])
def proxy(code=None):
    path = '/entregas' + ('/' + quote(code, safe='') if code else '')
    payload = None
    if request.method == 'POST':
        path += '/ocorrencias'
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(erro='Envie um objeto JSON'), 400
    result, status = api(path, payload)
    return jsonify(result), status
