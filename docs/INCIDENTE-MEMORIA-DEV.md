# Parecia rede, mas era memória

## O que aconteceu

Eu estava configurando o bloqueio de Operações dev para Rastreamento homolog quando percebi que a comunicação dentro de desenvolvimento também falhava.

Operações dev precisava continuar consultando Rastreamento dev. Como eu tinha acabado de mexer nas políticas de rede, essa foi minha primeira suspeita.

A requisição retornava:

```text
RemoteDisconnected: Remote end closed connection without response
```

Em outras tentativas, apareceu `Connection refused`.

## Como chegamos à causa

Na investigação com apoio do Codex, conferimos o Service de Rastreamento. Ele selecionava as três réplicas e encaminhava as conexões para TCP/8080.

Em seguida, as consultas foram feitas a partir do pod de Operações dev, tanto pelo Service quanto pelos IPs das réplicas. As conexões fecharam sem resposta e os containers registraram `OOMKilled`, código 137, no mesmo horário dos testes: 15:48:01 UTC de 09/11/2026.

Os pods estavam com request de `65Mi` e limite de `70Mi`. Eram os valores que eu havia usado no exercício anterior para demonstrar contenção de memória. O controle funcionava, mas o limite estava baixo para a execução normal da aplicação.

## Comandos usados na investigação

A consulta partiu do container de Operações dev, que é a origem real do fluxo:

```bash
oc exec -n project-developer deployment/operacoes -- \
  python -c 'from urllib.request import urlopen; print(urlopen("http://rastreamento.project-rastreamento.svc:8080/entregas", timeout=5).status)'
```

Para conferir para onde o Service encaminhava o tráfego e revisar a regra de bloqueio:

```bash
oc get service rastreamento -n project-rastreamento
oc get endpointslice -n project-rastreamento \
  -l kubernetes.io/service-name=rastreamento
oc get adminnetworkpolicy op-dev-ras-homo-deny -o yaml
```

O ping não respondia à pergunta principal: a API conseguia atender uma consulta? Por isso a verificação passou a usar HTTP. O erro apareceu mesmo acessando diretamente as réplicas, sem depender do Service.

## O ajuste

Alterei o request para `75Mi` e o limite para `110Mi`. Depois repetimos os testes:

- Operações dev → Rastreamento dev: cinco respostas HTTP 200.
- Operações homolog → Rastreamento homolog: três respostas HTTP 200.
- Operações dev → Rastreamento homolog: timeout, como esperado.
- As três réplicas de Rastreamento dev permaneceram prontas e sem reinícios durante a verificação.

## O que levo desse teste

Eu não teria começado investigando memória. A pista foi correlacionar a requisição com o aumento dos reinícios, em vez de olhar apenas para a comunicação.

Para uma próxima ocorrência, acompanharia os pods enquanto reproduzo o erro:

```bash
oc get pods -n project-rastreamento -l app=rastreamento -w
```

Se os reinícios aumentarem, consultaria o estado anterior e os logs da execução que morreu:

```bash
oc describe pod NOME_DO_POD -n project-rastreamento
oc logs NOME_DO_POD -n project-rastreamento --previous
```

O log atual pode mostrar apenas o processo iniciando de novo. Neste caso, a informação decisiva estava no estado do container: `OOMKilled`.
