# Progresso da PoC — Vértice Logística

## Persistência após substituição do pod PostgreSQL — aprovada pelo responsável

O responsável pelo laboratório informou ter executado o roteiro de registrar uma
ocorrência pela interface de Operações, excluir somente o pod PostgreSQL em
`project-rastreamento`, aguardar seu substituto e consultar novamente a ocorrência.
A ocorrência continuou disponível após a substituição do pod do banco.

Conclusão: os dados observados sobreviveram à substituição do pod PostgreSQL,
com o armazenamento persistente mantido. Validação manual relatada pelo responsável;
esta etapa não foi reproduzida independentemente pelo Codex.
Não equivale a teste de backup/restauração nem à preservação após exclusão do PVC/PV.

## 2026-11-09 — Rotação da credencial: concluída em desenvolvimento

- Escopo executado: `project-rastreamento` (adaptação do cenário originalmente previsto em homologação).
- Responsável pelo laboratório atualizou o Secret e reiniciou o rollout de Rastreamento.
- Codex alterou a senha do usuário no PostgreSQL conforme o Secret atual.
- Smoke posterior validou saúde, consulta, gravação via Operações e leitura via Rastreamento.
- Teste de conexão PostgreSQL via TCP: senha atual autenticou e consultou três entregas.
- Senha anterior, recuperada da anotação de aplicação anterior do Secret, foi rejeitada
  explicitamente por falha de autenticação. Nenhum valor foi exibido ou salvo neste relato.
- Homologação: credencial própria autenticou e consultou três entregas, sem alteração pelo Codex.

Os testes finais foram de autenticação e leitura; não houve alteração de configuração
nessa verificação. O relato comprova funcionamento, não uma auditoria integral dos dados.

## 2026-11-09 — Fluxos de comunicação: validação funcional concluída

Testes executados pelo Codex a partir dos Deployments reais de Operações:

- Dev → Rastreamento dev: cinco respostas HTTP 200.
- Homolog → Rastreamento homolog: três respostas HTTP 200.
- Dev → Rastreamento homolog: timeout, conforme bloqueio esperado.
- Rastreamento dev: request `75Mi`, limit `110Mi`; três réplicas prontas,
  zero reinícios antes e depois das consultas.

Escopo: fluxos acima, pelo DNS interno dos Services. Não comprova isolamento de todos
os workloads, bloqueio por rotas externas ou estabilidade sob carga prolongada.
Histórico da investigação: `INCIDENTE-MEMORIA-DEV.md`.

## 2026-11-09 — Contenção de memória: aprovado

Aprovado pelo responsável pelo laboratório após apresentar evidências do teste.

- Aplicação: Rastreamento, namespace `project-rastreamento`.
- Pod observado: `rastreamento-649cc4c869-7jdwn`.
- Request de memória: `65Mi`; limit por container: `70Mi`.
- Teste executado: processo Python via `oc exec` tentando alocar 80 MiB adicionais.
- O comando terminou com código 137.
- O estado anterior do container apresentou `Reason: OOMKilled` e `Exit Code: 137`.
- O container reiniciou no mesmo pod e retornou a `Running` e `Ready`.

Conclusão aprovada: demonstradas a aplicação do limite de memória e a recuperação
automática do container após OOM. A recuperação observada não dependeu de probes.

Limites da evidência: havia três reinícios no momento da consulta; não foi estabelecida
a causa individual de todos eles. Não foram comprovadas nesta etapa a disponibilidade
durante a falha, a ausência de impacto nas outras réplicas ou a proteção entre times.
Este registro não representa aprovação integral do tópico de recursos nem da PoC.

## Encerramento declarado pelo autor

O autor confirmou ter concluído a execução dos requisitos da PoC. Os registros acima
preservam o método de validação de cada etapa. A revisão do snapshot ainda aponta
refinamentos de RBAC e da separação por time em homologação; não há evidências detalhadas
anexadas de rollback e onboarding. Essas diferenças são apresentadas no README para
que o leitor consiga distinguir relato de execução, configuração observada e evidência disponível.
