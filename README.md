# Vértice Logística — PoC com OpenShift

[![Testes das aplicações](https://github.com/rossettimateus/vertice-openshift-poc/actions/workflows/tests.yml/badge.svg)](https://github.com/rossettimateus/vertice-openshift-poc/actions/workflows/tests.yml)

Parti de um cluster OpenShift já disponível e de um cenário de cliente fictício: a Vértice Logística precisava organizar dois sistemas, Operações e Rastreamento, em desenvolvimento e homologação.

A partir desse pedido, defini a distribuição dos projetos, configurei os acessos e as regras de comunicação e testei os fluxos das aplicações. Usei aplicações modelo para validar o comportamento da plataforma.

## O pedido recebido

Os desenvolvedores dependiam da infraestrutura para publicar aplicações e investigar problemas. Havia acessos excessivos, configurações manuais e preocupação com uma aplicação consumir recursos a ponto de afetar as demais.

A partir desse cenário, organizei os testes em torno destes pontos:

- Acessos organizados por time e função, com suporte consultando diagnóstico sem alterar as aplicações.
- Desenvolvimento e homologação com dados e credenciais separados.
- Comunicação entre Operações e Rastreamento no mesmo ambiente.
- Bloqueio de Operações dev para Rastreamento homolog.
- Controle de memória e recuperação após falhas.
- Troca de credenciais e preservação de dados quando o pod do banco fosse substituído.
- Um procedimento para receber novos usuários e times.

[Cenário e matriz de requisitos](docs/REQUISITOS.md) · [Arquitetura e implantação](docs/IMPLANTACAO.md) · [Resultados](docs/RESULTADOS.md)

## O ambiente que montei

Trabalhei em um cluster com OVN-Kubernetes e armazenamento EBS CSI. Separei os aplicativos de desenvolvimento em dois projetos. Para homologação, usei um terceiro projeto com uma cópia dos dois aplicativos e um banco próprio.

| Projeto | Componentes |
|---|---|
| `project-developer` | Operações dev |
| `project-rastreamento` | Rastreamento dev, PostgreSQL e PVC |
| `project-homologacao` | Operações homolog, Rastreamento homolog, PostgreSQL e PVC próprios |

```mermaid
flowchart LR
  subgraph DEV[Desenvolvimento]
    subgraph OP[project-developer]
      O[Operações]
    end
    subgraph RA[project-rastreamento]
      R[Rastreamento]
      D[(PostgreSQL + PVC)]
      R --> D
    end
    O -->|HTTP permitido| R
  end
  subgraph HOM[project-homologacao]
    OH[Operações homolog] --> RH[Rastreamento homolog]
    RH --> DH[(PostgreSQL + PVC próprio)]
  end
  O -. HTTP bloqueado .-> RH
```

Operações envia as consultas e os registros de ocorrências para a API de Rastreamento. A API faz o acesso ao PostgreSQL; Operações não recebe as credenciais do banco.

Usei o provedor HTPasswd já configurado no ambiente para os usuários. Organizei as permissões com grupos e bindings de RBAC. Para a comunicação entre ambientes, configurei uma AdminNetworkPolicy selecionando a origem e o destino pelos namespaces e labels dos pods.

O RBAC de desenvolvimento ficou com `edit` para cada grupo no próprio projeto e `view` no projeto do outro time. O suporte recebe leitura de diagnóstico, sem alteração de Deployments nem leitura de Secrets.

Homologação reúne os dois aplicativos e é operada pelo acesso administrativo do laboratório. Os grupos de desenvolvimento e suporte não receberam acesso a esse projeto nesta entrega. A separação de homologação por time fica para uma ampliação da estrutura.

## Validação da entrega

| Necessidade | Teste realizado | Resultado |
|---|---|---|
| Acessos dos desenvolvedores | Consultar pods e logs, verificar criação/alteração de Deployments e leitura de Secrets nos dois projetos | Edição no próprio projeto; leitura no outro, sem alteração nem acesso aos Secrets |
| Acesso de suporte | Consultar pods, eventos e logs; verificar permissões de alteração e leitura de Secrets | Leitura de diagnóstico permitida; ações verificadas de alteração e leitura de Secrets negadas |
| Comunicação em desenvolvimento | Consultar Rastreamento a partir de Operações dev | HTTP 200 em cinco consultas consecutivas |
| Comunicação em homologação | Consultar Rastreamento a partir de Operações homolog | HTTP 200 em três consultas consecutivas |
| Bloqueio entre ambientes | Consultar Rastreamento homolog a partir de Operações dev | Timeout, com a regra de bloqueio aplicada |
| Limite de memória | Tentar alocar memória acima do limite do container | OOMKilled e reinício do container |
| Troca de senha do banco | Atualizar a credencial e testar a senha nova e a antiga | Nova autenticou; antiga foi rejeitada; homologação continuou acessível |
| Persistência | Registrar uma ocorrência e substituir o pod PostgreSQL | A ocorrência permaneceu disponível |

A troca de credenciais foi feita em desenvolvimento. Na parte de recuperação de versão, as aplicações incluem imagens com falhas controladas de readiness e de negócio. Deixei o roteiro de execução e o procedimento de entrada de um novo time na documentação.

[Testes e resultados](docs/RESULTADOS.md) · [Roteiro do laboratório](docs/VALIDACAO.md) · [Entrada de novos times](docs/ONBOARDING.md)

## O problema que mais me ensinou

Enquanto configurava o isolamento, Operações dev parou de consultar Rastreamento dev. Minha primeira suspeita foi a rede, porque era justamente a configuração em que eu estava trabalhando.

A investigação mostrou que as requisições chegavam aos pods, mas os containers morriam por falta de memória. O limite de 70 MiB usado no exercício de contenção era baixo demais para o funcionamento da aplicação.

Ajustei o request para 75 MiB e o limite para 110 MiB. Repetimos as consultas: desenvolvimento voltou a responder, homologação continuou funcionando e o acesso indevido entre os ambientes permaneceu bloqueado. As três réplicas de Rastreamento dev ficaram prontas, sem reinícios durante essa verificação.

Eu estava procurando um problema de rede e não tinha pensado em memória. Acompanhar os reinícios junto da requisição foi o que ajudou a entender a falha.

[Relato e comandos usados na investigação](docs/INCIDENTE-MEMORIA-DEV.md).

## O que está no repositório

- `rastreamento/` e `operacoes/`: aplicações modelo, preparadas com apoio do Codex.
- `deploy/apps.json` e `deploy/homologacao.json`: implantação inicial das aplicações.
- `deploy/observado.json`: configurações exportadas do laboratório, sem Secrets e com referências ajustadas para reprodução.
- `docs/`: requisitos do cliente, decisões de arquitetura, implantação e resultados dos testes.
- `tests/`: testes unitários e smoke integrado.

[Como reproduzir](docs/REPRODUCAO.md) · [Configuração das aplicações](docs/APLICACOES.md)

## Escopo da entrega

Esta entrega reúne a estrutura dos ambientes, os controles aplicados e os testes funcionais descritos acima. O laboratório usa dados fictícios; alta disponibilidade do banco, testes de carga e backup/restauração ficaram fora desta etapa.


## Testes locais

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r rastreamento/requirements.txt
python -m unittest discover -s tests -v
```

O smoke integrado insere uma ocorrência sintética. Execute `python tests/smoke.py --help` para informar as URLs.
