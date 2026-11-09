# Roteiro de validação

## Aplicações e dados

- Inicialize cada banco; espere três entregas: ENT-001, ENT-002 e ENT-003.
- Repita o inicializador; confirme que não duplica entregas nem apaga ocorrências.
- Execute `tests/smoke.py` contra cada ambiente (insere um registro sintético).
- Registre uma ocorrência exclusiva em dev e confirme sua ausência em homolog.
- Reinicie a API e confirme que a ocorrência continua presente.
- Após reiniciar o banco com seu armazenamento persistente, confirme novamente.
- Confira `/version` e o ambiente exibido na página.

## Comunicação e operação

- API acessível pela URL externa; banco sem exposição externa.
- Operações consulta Rastreamento do próprio ambiente.
- Tentativas de dev acessar serviços de homolog falham conforme sua política.
- Cada time publica e investiga seus recursos, sem alterar os do outro time.
- Suporte consulta estado e diagnóstico sem modificar configurações.
- Teste os limites de recursos que você definir para demonstrar proteção entre times.
- Use os logs para identificar erros HTTP e indisponibilidade de dependências.

## Falhas e recuperação

1. Com versão 1.0.0 saudável, registre uma ocorrência e anote seu identificador.
2. Publique a imagem com falha de readiness. Confira `/healthz` 200 e `/readyz` 503 diretamente
   no processo/container; uma rota pode deixar de encaminhar tráfego a instâncias não prontas.
3. Observe o comportamento da estratégia de publicação que você configurar. Não assuma rollback automático.
4. Volte à imagem saudável e confirme o acesso e a persistência da ocorrência.
5. Publique a versão com falha funcional. Readiness fica saudável, mas consultas falham com 500.
6. Detecte a falha pela página ou smoke; volte à imagem saudável e repita o teste.
7. Interrompa o acesso ao banco: API fica não pronta, mas liveness continua saudável.
8. Restabeleça o banco: novas requisições reconectam sem precisar reiniciar a API.

Readiness de Operações depende da API: se ela não estiver pronta, Operações também deixa de estar pronta.
Isso é uma decisão demonstrativa do pacote; considere esse efeito ao analisar os resultados.
Rollback de aplicação não equivale a restauração de banco. Estes exercícios usam o mesmo esquema.

## Repetibilidade

Entregue a outro operador as imagens/digests, variáveis necessárias, ordem de inicialização,
procedimento de publicação/recuperação e resultados esperados. Peça que repita sem sua intervenção.

## Resultados da execução

Os resultados obtidos na PoC estão em [RESULTADOS.md](RESULTADOS.md).
