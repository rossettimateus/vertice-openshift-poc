# Comandos usados no troubleshooting

Durante os testes, Operações dev não conseguia consultar Rastreamento dev. Estes foram os comandos usados para verificar o caminho da requisição e acompanhar o que acontecia nos pods.

## Testar a API a partir de Operações

Em desenvolvimento:

```bash
oc exec -n project-developer deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento.project-rastreamento.svc:8080/entregas", timeout=5).status)'
```

Em homologação:

```bash
oc exec -n project-homologacao deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento:8080/entregas", timeout=5).status)'
```

Os dois acessos precisavam retornar `200`. O mesmo teste de desenvolvimento para homologação precisava falhar:

```bash
oc exec -n project-developer deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento.project-homologacao.svc:8080/entregas", timeout=5).status)'
```

## Conferir o destino

```bash
oc get service rastreamento -n project-rastreamento
oc get endpointslice -n project-rastreamento \
  -l kubernetes.io/service-name=rastreamento
oc get adminnetworkpolicy op-dev-ras-homo-deny -o yaml
```

O Service apontava para as três réplicas, na porta 8080. A regra bloqueava o acesso de Operações dev a Rastreamento homolog.

## Acompanhar os reinícios

Em outro terminal, enquanto a requisição era repetida:

```bash
oc get pods -n project-rastreamento -l app=rastreamento -w
```

O contador de reinícios aumentou junto com as falhas HTTP. Para ver o motivo, substitua `NOME_DO_POD` pelo pod afetado:

```bash
oc describe pod NOME_DO_POD -n project-rastreamento
oc logs NOME_DO_POD -n project-rastreamento --previous
```

O `describe` mostrou `OOMKilled`. Os logs atuais mostravam o Gunicorn iniciando novamente; por isso foi importante olhar o estado anterior do container.

O relato completo está em [Parecia rede, mas era memória](INCIDENTE-MEMORIA-DEV.md).
