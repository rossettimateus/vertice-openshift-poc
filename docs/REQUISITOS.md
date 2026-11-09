# Cenário recebido e escopo da PoC

## O cenário apresentado

A empresa mantém dois sistemas internos: Rastreamento, responsável pelas consultas de entregas, e Operações, usado pelos funcionários para consultar e registrar ocorrências.

No cenário, as aplicações rodam em máquinas virtuais. Os desenvolvedores dependem da infraestrutura para publicar versões, configurar acessos e investigar falhas. A empresa quer avaliar OpenShift antes de ampliar a adoção.

O pedido que usei como base para o trabalho foi:

> Permitir que os dois times publiquem e investiguem suas aplicações com acessos delimitados, proteger o ambiente contra consumo excessivo de recursos e ter procedimentos claros para recuperar o serviço. A equipe precisa conseguir entender e repetir o processo.

## Restrições

- Um cluster com a capacidade disponível no laboratório.
- Desenvolvimento e homologação; produção fora desta etapa.
- Aplicações demonstrativas e dados sintéticos.
- Equipe de plataforma pequena, com necessidade de procedimentos reproduzíveis.
- Alta disponibilidade da infraestrutura fora do escopo da demonstração.

## Requisito, decisão e entrega

| O que foi pedido | Como tratei na arquitetura | Entrega no repositório |
|---|---|---|
| Delimitar permissões de desenvolvimento, suporte e plataforma | Identidade via HTPasswd, grupos e RBAC por projeto | Bindings exportados e procedimento de identidade e acesso |
| Separar desenvolvimento de homologação | Projetos de desenvolvimento por aplicação e um projeto próprio de homologação | Deployments, bancos, credenciais e volumes independentes por ambiente |
| Manter Operações consultando Rastreamento no mesmo ambiente | Comunicação HTTP pelo Service; credenciais do banco somente em Rastreamento | Fluxos internos validados com HTTP 200 |
| Impedir Operações dev de acessar Rastreamento homolog | AdminNetworkPolicy com seletores de namespace e pod | Regra exportada e teste HTTP com timeout |
| Conter consumo de recursos | Requests e limits de memória em Rastreamento dev | Teste de OOM, recuperação e ajuste de dimensionamento |
| Substituir uma credencial | Coordenar alteração no PostgreSQL, atualização do Secret e rollout da API | Senha nova aceita, antiga rejeitada e outro ambiente preservado |
| Recuperar uma versão defeituosa | Preparar versões com falha de readiness e de negócio e um procedimento de retorno | Aplicações, Containerfiles e roteiro de recuperação |
| Preservar dados após substituir um pod | PostgreSQL monta armazenamento persistente por PVC | Ocorrência consultada após substituição do pod do banco |
| Receber um terceiro time | Reutilizar o provedor de identidade e documentar usuários, grupos, projetos e permissões | Procedimento de onboarding |

O detalhamento dos testes está em [RESULTADOS.md](RESULTADOS.md). Os manifests exportados registram as configurações disponíveis, incluindo os bindings de leitura. Permissões adicionais para autonomia completa de publicação devem seguir a matriz de acesso do ambiente.

## Adaptações no laboratório

A rotação de credenciais foi executada em desenvolvimento. Homologação compartilha um namespace entre as duas aplicações, mantendo banco e credenciais separados de desenvolvimento. A regra de rede demonstra um fluxo específico de bloqueio; sua ampliação para todos os workloads e para acessos externos fica como evolução da arquitetura.
