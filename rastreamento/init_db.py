"""Inicialização explícita e idempotente. Execute com as mesmas DB_* da API."""
from app import connection

with connection() as conn:
    # Serializa execuções simultâneas do inicializador neste banco.
    conn.execute('SELECT pg_advisory_xact_lock(782103)')
    conn.execute('''CREATE TABLE IF NOT EXISTS entregas (
        codigo VARCHAR(7) PRIMARY KEY, origem TEXT NOT NULL,
        destino TEXT NOT NULL, status TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS ocorrencias (
        id BIGSERIAL PRIMARY KEY, entrega_codigo VARCHAR(7) NOT NULL REFERENCES entregas(codigo),
        descricao VARCHAR(500) NOT NULL, criado_em TIMESTAMPTZ NOT NULL DEFAULT now())''')
    for row in [('ENT-001','Barueri','Campinas','em_transito'),
                ('ENT-002','São Paulo','Santos','entregue'),
                ('ENT-003','Osasco','Sorocaba','aguardando_coleta')]:
        conn.execute('INSERT INTO entregas VALUES (%s,%s,%s,%s) ON CONFLICT (codigo) DO NOTHING', row)
print('Banco inicializado. Dados existentes preservados.')
