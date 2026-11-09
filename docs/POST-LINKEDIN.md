# Rascunho para LinkedIn

Como demonstrar que uma plataforma OpenShift atende aos requisitos de um cliente?

Montei uma PoC para uma empresa fictícia de logística, com dois times de desenvolvimento e ambientes de desenvolvimento e homologação. Meu foco foi a plataforma: acessos por grupos, comunicação entre aplicações, limites de recursos, persistência e troca de credenciais.

Um dos aprendizados mais úteis apareceu durante os testes de rede. Operações dev não conseguia consultar Rastreamento dev. Como eu estava configurando isolamento, a suspeita inicial foi um bloqueio de tráfego.

A investigação mostrou outra causa: as requisições chegavam, mas os containers de Rastreamento eram encerrados por OOM. O limite usado no teste de contenção era insuficiente para a execução normal. Ajustei a memória e validei novamente os fluxos permitidos e bloqueados.

Também testei uma troca de senha do banco coordenada com o Secret e a atualização dos pods, e confirmei que uma ocorrência permanecia disponível após substituir o pod do PostgreSQL.

Documentei a arquitetura, os testes, o incidente e os limites da demonstração no GitHub. Usei aplicações modelo preparadas com apoio do Codex para concentrar o trabalho nas decisões e configurações do OpenShift.

Repositório: https://github.com/rossettimateus/vertice-openshift-poc

#OpenShift #Kubernetes #PlatformEngineering #RedHat
