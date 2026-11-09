"""Testes de contrato sem PostgreSQL. Execute: python -m unittest discover -s tests -v"""
import importlib.util
import os
import sys
from pathlib import Path
from unittest import TestCase, mock
import psycopg

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('TRACKING_API_URL', 'http://127.0.0.1:18080')

def load(name, folder):
    spec = importlib.util.spec_from_file_location(name, ROOT / folder / 'app.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

tracking = load('tracking', 'rastreamento')
operations = load('operations', 'operacoes')

class TrackingTests(TestCase):
    def setUp(self):
        self.client = tracking.app.test_client()

    def test_liveness_without_database(self):
        with mock.patch.object(tracking, 'connection', side_effect=AssertionError):
            self.assertEqual(self.client.get('/healthz').status_code, 200)

    def test_unavailable_database(self):
        with mock.patch.object(tracking, 'connection', side_effect=psycopg.OperationalError):
            self.assertEqual(self.client.get('/readyz').status_code, 503)
            self.assertEqual(self.client.get('/entregas').status_code, 503)

    def test_fault_modes(self):
        with mock.patch.object(tracking, 'FAIL', 'readiness'):
            self.assertEqual(self.client.get('/readyz').status_code, 503)
            self.assertEqual(self.client.get('/healthz').status_code, 200)
        with mock.patch.object(tracking, 'FAIL', 'business'):
            self.assertEqual(self.client.get('/entregas').status_code, 500)
            self.assertEqual(self.client.get('/healthz').status_code, 200)

    def test_invalid_payloads(self):
        for payload in ({}, [], {'descricao': 23}, {'descricao': ' '}, {'descricao': 'x'*501}):
            self.assertEqual(self.client.post('/entregas/ENT-001/ocorrencias', json=payload).status_code, 400)
        self.assertEqual(self.client.get('/entregas/invalid').status_code, 400)

    def test_insert_uses_parameters(self):
        with mock.patch.object(tracking, 'connection') as factory:
            conn = factory.return_value.__enter__.return_value
            conn.execute.return_value.fetchone.side_effect = [{'codigo':'ENT-001'}, {'id': 42}]
            text = "Tentativa ' ; DROP TABLE entregas; --"
            response = self.client.post('/entregas/ENT-001/ocorrencias', json={'descricao':text})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(conn.execute.call_args.args[1], ('ENT-001', text))
            self.assertNotIn(text, conn.execute.call_args.args[0])

    def test_not_found(self):
        with mock.patch.object(tracking, 'connection') as factory:
            factory.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = None
            self.assertEqual(self.client.get('/entregas/ENT-999').status_code, 404)

class OperationsTests(TestCase):
    def setUp(self):
        self.client = operations.app.test_client()

    def test_home_and_script(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        with self.client.get('/static/app.js') as response:
            self.assertEqual(response.status_code, 200)

    def test_dependency_failure(self):
        with mock.patch.object(operations, 'api', return_value=({'erro':'indisponivel'},503)):
            self.assertEqual(self.client.get('/readyz').status_code, 503)
            self.assertEqual(self.client.get('/healthz').status_code, 200)
            self.assertEqual(self.client.get('/api/entregas').status_code, 503)

    def test_server_side_post(self):
        with mock.patch.object(operations, 'api', return_value=({'id':1},201)) as call:
            result = self.client.post('/api/entregas/ENT-001/ocorrencias', json={'descricao':'Teste'})
            self.assertEqual(result.status_code, 201)
            call.assert_called_once_with('/entregas/ENT-001/ocorrencias', {'descricao':'Teste'})

    def test_network_failure(self):
        with mock.patch.object(operations, 'urlopen', side_effect=TimeoutError):
            self.assertEqual(operations.api('/readyz')[1], 503)
