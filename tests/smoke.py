"""Teste integrado contra URLs em execução; insere uma ocorrência sintética.
python tests/smoke.py --tracking http://localhost:8081 --operations http://localhost:8082
"""
import argparse
import json
import uuid
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tracking', required=True)
parser.add_argument('--operations', required=True)
args = parser.parse_args()

def call(base, path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    with urlopen(Request(base.rstrip('/') + path, data=body,
                         headers={'Content-Type':'application/json'}), timeout=10) as response:
        return response.status, json.load(response)

for base in (args.tracking, args.operations):
    assert call(base, '/healthz')[0] == 200
    assert call(base, '/readyz')[0] == 200
    assert call(base, '/version')[0] == 200
assert len(call(args.tracking, '/entregas')[1]['entregas']) >= 3
marker = 'Teste integrado ' + str(uuid.uuid4())
assert call(args.operations, '/api/entregas/ENT-001/ocorrencias', {'descricao':marker})[0] == 201
record = call(args.tracking, '/entregas/ENT-001')[1]
assert any(event['descricao'] == marker for event in record['ocorrencias'])
assert call(args.operations, '/api/entregas/ENT-001')[1]['codigo'] == 'ENT-001'
print('OK: saúde, consulta, escrita via Operações e leitura pelo Rastreamento.')
