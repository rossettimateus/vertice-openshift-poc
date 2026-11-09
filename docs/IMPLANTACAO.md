# Implantação inicial — 08/11/2026

Aplicações no cluster para os exercícios administrativos:

| Projeto | Componentes |
|---|---|
| `project-developer` | Operações, Service e Route HTTPS |
| `project-rastreamento` | Rastreamento, Service e Route HTTPS; PostgreSQL com Service interno e PVC de 1 GiB |

Os dois aplicativos desta implantação inicial reportam `APP_ENV=dev`.
Operações consulta `http://rastreamento.project-rastreamento.svc:8080`.
O banco utiliza dados sintéticos e suas credenciais ficam no Secret `rastreamento-db`.
Nenhum valor de senha está salvo neste diretório. A aplicação lê as credenciais por variáveis de ambiente.

As imagens são construídas por BuildConfigs binárias, usando `Containerfile`, e armazenadas
nos ImageStreams dos respectivos projetos. Os Deployments usam o registry interno, com imagens
fixadas pelo digest do build concluído.
`deploy/apps.json` registra os recursos iniciais, sem o Secret e sem os recursos de build.
Reaplicá-lo depois de realizar os exercícios pode sobrescrever suas alterações nesses recursos.

O banco é inicializado explicitamente com `python init_db.py` no container de Rastreamento.
O comando pode ser repetido sem apagar os dados.

RBAC existente foi preservado. Quotas, LimitRanges, NetworkPolicies e probes não foram adicionados.
O PVC permite iniciar o exercício de persistência; sua política de armazenamento será avaliada por você.
Não há autenticação na aplicação: use apenas dados fictícios.

Para reconstruir uma aplicação, envie novamente seu diretório com `oc start-build --from-dir`.
Após a conclusão, os Deployments precisam usar a imagem desejada e iniciar novos pods;
não há promoção ou recuperação automática configurada neste pacote.

## Homologação — 09/11/2026

Implantada separadamente no projeto existente `project-homologacao`, conforme solicitado.
Manifesto: `deploy/homologacao.json`.

- Operações e Rastreamento reportam `APP_ENV=homolog`.
- Operações usa `http://rastreamento:8080`, no próprio namespace.
- PostgreSQL tem PVC exclusivo de 1 GiB, banco e usuário `vertice_homolog`.
- Secret `rastreamento-db` exclusivo do namespace, com senha gerada separadamente.
- Os fontes das aplicações são construídos nos ImageStreams de homologação,
  sem conceder permissões de pull nos projetos de desenvolvimento.
- Os dados iniciais são sintéticos. Dados inseridos em desenvolvimento não são copiados.
- Routes HTTPS independentes para Operações e Rastreamento; banco somente com Service interno.
- A implantação não acrescenta RBAC, NetworkPolicies, quotas ou probes.
  O isolamento de rede entre desenvolvimento e homologação fica para o exercício administrativo.
