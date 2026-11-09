# Diagnóstico dos fluxos HTTP

Comandos usados para distinguir uma falha de comunicação de uma aplicação que reinicia ao receber requisições. Todos os comandos abaixo são de consulta; execute-os com uma conta autorizada no laboratório.

## Reproduzir o fluxo

```bash
# Desenvolvimento → desenvolvimento: esperado HTTP 200
oc exec -n project-developer deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento.project-rastreamento.svc:8080/entregas", timeout=5).status)'

# Homologação → homologação: esperado HTTP 200
oc exec -n project-homologacao deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento:8080/entregas", timeout=5).status)'

# Desenvolvimento → homologação: esperado timeout com a regra de bloqueio aplicada
oc exec -n project-developer deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento.project-homologacao.svc:8080/entregas", timeout=5).status)'
```

Um timeout sozinho não prova que a política causou o bloqueio. Confirme que o destino responde a uma origem permitida e confira os seletores da política.

## Observar o destino durante a requisição

```bash
oc get pods -n project-rastreamento -l app=rastreamento -w
oc get service rastreamento -n project-rastreamento
oc get endpointslice -n project-rastreamento \
  -l kubernetes.io/service-name=rastreamento
oc get adminnetworkpolicy op-dev-ras-homo-deny -o yaml
```

Se o contador de reinícios aumentar junto da falha, consulte o motivo do encerramento. Substitua `NOME_DO_POD` pelo pod afetado:

```bash
oc describe pod NOME_DO_POD -n project-rastreamento
oc logs NOME_DO_POD -n project-rastreamento --previous
```

`OOMKilled` foi a evidência encontrada nesta PoC. O log da aplicação pode terminar sem explicar a morte do processo. Consulte o [incidente de memória](INCIDENTE-MEMORIA-DEV.md) para acompanhar a investigação.
