# Quando uma falha HTTP parecia um bloqueio de rede

## Contexto

Durante os testes de isolamento entre desenvolvimento e homologação, a comunicação
Operações dev → Rastreamento dev também falhou. Esse fluxo deveria continuar permitido.
O contexto de alteração de políticas de rede tornou um bloqueio de tráfego uma hipótese inicial.

## Sintoma

A consulta HTTP retornava `RemoteDisconnected: Remote end closed connection without response`.
Em testes subsequentes também houve `Connection refused`.
Esses erros, isoladamente, não identificam a causa.

## Investigação e evidências — 09/11/2026

1. O Service Rastreamento selecionava as três réplicas e encaminhava para TCP/8080.
2. As consultas partiram do pod real de Operações dev, pelo Service e diretamente
   pelos IPs das três réplicas de Rastreamento dev.
3. As conexões foram encerradas sem resposta HTTP; consultas seguintes tiveram conexão recusada.
4. Os três containers registraram `OOMKilled`, código 137, às 15:48:01 UTC,
   no momento da reprodução. Os contadores de reinícios aumentaram.
5. Cada container tinha request de `65Mi` e limit de `70Mi`, valores usados no exercício de contenção.

Diagnóstico: o limite de memória era insuficiente para a execução observada;
as requisições chegavam ao destino, mas os containers eram encerrados por OOM.
O limite demonstrava contenção, porém não oferecia um dimensionamento adequado para operação normal.

## Resolução e estado da validação

O responsável pelo laboratório ajustou o request para `75Mi` e o limit para `110Mi`.
Na verificação posterior pelo Codex em 09/11/2026:

- Operações dev → Rastreamento dev: cinco consultas consecutivas com HTTP 200.
- Operações homolog → Rastreamento homolog: três consultas consecutivas com HTTP 200.
- Operações dev → Rastreamento homolog: timeout, coerente com a regra de bloqueio inspecionada.
- As três réplicas de Rastreamento dev permaneceram prontas, com zero reinícios antes e depois.

A correção passou nessa verificação funcional curta. Não foi realizado teste de carga
ou observação prolongada para determinar o dimensionamento definitivo.

## Aprendizado para o portfólio

- Correlacionar a reprodução da falha com os reinícios e horários de término dos containers.
- Consultar `State`, `Last State`, `Reason` e `Limits` no `oc describe pod`.
- Usar `oc logs --previous` para consultar a execução anterior; o log pode terminar sem
  mensagem explicativa quando o processo é encerrado por OOM.
- Distinguir timeout, conexão recusada e conexão encerrada, tratando-os como pistas.
- Separar sucesso do teste de contenção de recursos de adequação do dimensionamento.

Na apresentação pública, contar este episódio como uma descoberta do laboratório,
com hipóteses e evidências. A correlação decisiva foi identificada com apoio do Codex,
que consultou o cluster e reproduziu as requisições; não atribuir essa etapa a uma
investigação independente do autor.
