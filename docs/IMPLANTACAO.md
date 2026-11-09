# Implantação das aplicações

A PoC utiliza duas aplicações HTTP e PostgreSQL. Os fontes, Containerfiles e contratos de configuração estão em [APLICACOES.md](APLICACOES.md).

| Projeto | Componentes |
|---|---|
| `project-developer` | Operações dev, Service e Route HTTPS |
| `project-rastreamento` | Rastreamento dev, PostgreSQL, Services, Route HTTPS e PVC de 1 GiB |
| `project-homologacao` | Operações homolog, Rastreamento homolog, PostgreSQL, Services, Routes HTTPS e PVC próprio de 1 GiB |

## Configuração por ambiente

Em desenvolvimento, Operações usa `http://rastreamento.project-rastreamento.svc:8080`. Em homologação, usa `http://rastreamento:8080`, resolvido no próprio projeto.

As aplicações reportam `APP_ENV=dev` ou `APP_ENV=homolog`. Esse valor identifica o ambiente; a separação de dados depende dos bancos, credenciais e volumes configurados.

O Secret `rastreamento-db` existe nos dois projetos que hospedam o banco, com valores próprios de cada ambiente. Rastreamento recebe as variáveis de conexão por esse Secret. Operações acessa somente a API.

## Imagens e inicialização

BuildConfigs binárias constroem os diretórios das aplicações usando `Containerfile`. Cada projeto mantém seus ImageStreams no registry interno, inclusive homologação, sem depender de permissões de pull nos projetos de desenvolvimento.

O comando `python init_db.py`, executado no container de Rastreamento, inicializa as tabelas e os dados sintéticos. Ele pode ser repetido sem apagar os registros existentes.

## Manifests

- `deploy/apps.json`: implantação inicial de desenvolvimento.
- `deploy/homologacao.json`: implantação inicial de homologação.
- `deploy/observado.json`: exportação das configurações do laboratório, com metadados removidos e referências ajustadas para reprodução.

Os manifests iniciais precedem os ajustes administrativos. Reaplicá-los sobre o ambiente pode sobrescrever alterações dos Deployments. Para reproduzir o projeto em outro cluster, siga [REPRODUCAO.md](REPRODUCAO.md).
