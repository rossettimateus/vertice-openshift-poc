# Reprodução do laboratório

Este repositório registra uma PoC e seus exercícios, não um instalador completo de plataforma.

## Pré-requisitos

- Cluster OpenShift com suporte à API AdminNetworkPolicy utilizada; confirme a disponibilidade na sua versão.
- Permissões para criar projetos, recursos de aplicação e políticas administrativas.
- Registry interno operacional, builds Docker habilitados e acesso às imagens base.
- StorageClass padrão com provisionamento dinâmico, capacidade de ao menos dois PVCs de 1 GiB.
- CLI `oc`, Python 3 e ferramentas de build quando construir imagens fora do cluster.

O laboratório original usou OpenShift, OVN-Kubernetes e armazenamento EBS CSI. Execução em OKD ou outro storage não foi validada neste projeto.

## Escolha dos manifests

`deploy/apps.json` e `deploy/homologacao.json` são os manifests iniciais usados para disponibilizar as aplicações. Eles não contêm os refinamentos administrativos feitos durante os exercícios. Os digests nesses arquivos pertencem ao registry original: construa e substitua as referências no seu ambiente.

`deploy/observado.json` contém recursos sanitizados da revisão: Deployments, Services, Routes, PVCs, BuildConfigs, ImageStreams e controles observados. Routes recebem hosts do novo cluster, PVCs usam sua StorageClass padrão e aplicações referenciam tags `1.0.0` no registry interno. Não aplique este snapshot por cima de um ambiente existente sem revisão.

## Ordem de preparação

1. Crie `project-developer`, `project-rastreamento` e `project-homologacao`.
2. Configure sua autenticação e grupos. Secrets de identidade não estão no repositório.
3. Em cada namespace com PostgreSQL, crie um Secret `rastreamento-db` com `DB_HOST=postgresql`, `DB_PORT=5432`, `DB_NAME`, `DB_USER` e `DB_PASSWORD`. Use valores independentes por ambiente. Não versione os arquivos resultantes.
4. Prepare PVCs, Services, ImageStreams e BuildConfigs a partir do manifesto escolhido.
5. Execute builds binários dos diretórios `rastreamento/` e `operacoes/`, usando `Containerfile`. Em dev, cada app fica no projeto correspondente; em homolog, os dois ficam em `project-homologacao`.
6. Confirme a tag de saída do build e a referência dos Deployments. Para o snapshot observado, a saída é `1.0.0`.
7. Aguarde o banco e as imagens; disponibilize os Deployments e execute `python init_db.py` no container de Rastreamento em cada ambiente.
8. Valide o funcionamento antes de aplicar políticas de isolamento. Depois repita os testes permitidos e negados.

Variáveis e comandos de build: [APLICACOES.md](APLICACOES.md). Critérios: [VALIDACAO.md](VALIDACAO.md).

## Credenciais e persistência

Atualizar o Secret não altera a senha em um banco inicializado. Coordene a alteração PostgreSQL com a atualização do Secret e a recriação dos containers que leem variáveis de ambiente. As variáveis de inicialização da imagem do banco não equivalem a uma rotina de rotação.

Para demonstrar persistência, grave uma ocorrência, substitua somente o pod PostgreSQL e consulte novamente. Não exclua o PVC. Esta validação não é um teste de backup.
