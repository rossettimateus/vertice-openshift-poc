# Testes e resultados

Executei os testes com os dois ambientes disponíveis no cluster. Abaixo estão os resultados que usei para avaliar a PoC.

## Comunicação entre aplicações

| Origem | Destino | Resultado |
|---|---|---|
| Operações dev | Rastreamento dev | Cinco consultas HTTP 200 |
| Operações homolog | Rastreamento homolog | Três consultas HTTP 200 |
| Operações dev | Rastreamento homolog | Timeout |

A primeira versão da AdminNetworkPolicy selecionava os pods `app=operacoes` de todos os namespaces. Isso também bloqueou Operações homolog. Corrigi o seletor de origem para `project-developer` e repeti os testes.

As consultas usaram HTTP pelo DNS dos Services. O ping ajudou em verificações pontuais, mas não substituiu o teste do protocolo usado pela aplicação.

## Contenção de memória

Configurei Rastreamento dev com request de `65Mi` e limit de `70Mi`. Dentro de um dos containers, executei um processo Python tentando alocar mais 80 MiB.

O comando terminou com código 137. No estado do container, apareceram `Reason: OOMKilled` e `Exit Code: 137`. O container reiniciou e voltou a ficar pronto no mesmo pod.

Depois, durante as consultas normais, descobrimos que esse limite também era insuficiente para a aplicação. Ajustei para request de `75Mi` e limit de `110Mi`. Na repetição dos testes, as três réplicas ficaram prontas, sem reinícios durante as consultas.

O teste demonstrou a contenção. O ajuste posterior permitiu continuar os testes funcionais; um dimensionamento para produção precisaria de medição sob carga.

[Investigação do problema](INCIDENTE-MEMORIA-DEV.md).

## Troca da credencial do PostgreSQL

Fiz a atualização do Secret `rastreamento-db` em `project-rastreamento` e reiniciei o rollout da API. A mudança foi coordenada com a alteração da senha do usuário no PostgreSQL.

Depois da troca:

- A nova senha autenticou e permitiu consultar as entregas.
- A senha antiga foi rejeitada por falha de autenticação.
- Operações conseguiu registrar uma ocorrência e Rastreamento conseguiu consultá-la.
- O banco de homologação continuou acessível com sua própria credencial.

O principal cuidado foi entender que atualizar o Secret não altera a senha dentro de um banco já inicializado. As duas mudanças precisam ser coordenadas.

## Persistência após substituição do pod

Registrei uma ocorrência pela interface de Operações, excluí somente o pod PostgreSQL de desenvolvimento e aguardei o substituto ficar disponível. Depois consultei a entrega novamente: a ocorrência continuava lá.

O novo pod montou o armazenamento pelo PVC existente. Não excluí o PVC nem o PV. O exercício demonstrou persistência após substituir o pod do banco; backup e restauração são uma próxima etapa.

## Procedimentos do laboratório

O [roteiro de validação](VALIDACAO.md) inclui publicação de versões com falha controlada e recuperação da aplicação. O [documento de onboarding](ONBOARDING.md) organiza a entrada de usuários e de um terceiro time.

As verificações de HTTP e autenticação foram feitas com apoio do Codex. O teste de persistência foi acompanhado pela interface da aplicação.

## Resumo dos critérios verificados

| Verificação | Evidência registrada |
|---|---|
| Diagnóstico de suporte | Permissões consultadas para pods, logs, eventos, alteração e Secrets |
| Fluxos HTTP no mesmo ambiente | Respostas HTTP 200 em dev e homolog |
| Fluxo dev → homolog | Timeout com origem e destino selecionados na política |
| Contenção de memória | Estado OOMKilled e código 137 |
| Funcionamento após ajuste de memória | Consultas HTTP 200 e ausência de novos reinícios durante o teste |
| Rotação de senha | Conexões ao banco com senha nova e antiga |
| Persistência do banco | Ocorrência consultada após substituir o pod PostgreSQL |

Para repetir os testes de comunicação, consulte [DIAGNOSTICO.md](DIAGNOSTICO.md). Para os demais cenários, consulte [VALIDACAO.md](VALIDACAO.md).
