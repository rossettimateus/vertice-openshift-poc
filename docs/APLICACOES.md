# Vértice Logística — aplicações para laboratório OpenShift

Duas aplicações demonstrativas com dados sintéticos. Você configura integralmente o OpenShift.
Os fontes das aplicações estão separados das configurações administrativas do laboratório.
A implantação inicial solicitada está registrada em `../deploy/apps.json` e `IMPLANTACAO.md`.

## Comece aqui

1. Construa as imagens com os Containerfiles abaixo e publique no seu registry.
2. Disponibilize um PostgreSQL com banco e credenciais para cada ambiente.
3. Execute `python init_db.py` usando a imagem de Rastreamento e suas variáveis `DB_*`.
4. Execute Rastreamento e Operações com as variáveis documentadas.
5. Abra a página de Operações; consulte `ENT-001` e registre uma ocorrência.
6. Faça os testes em `VALIDACAO.md` e pratique publicação/recuperação.

O inicializador é uma ação explícita, separada da inicialização HTTP: você decide como executá-lo
na plataforma. É idempotente, não apaga dados e pode ser repetido. Execute em cada banco de ambiente.
O usuário de inicialização precisa criar tabelas; para simplificar o laboratório, usa as mesmas
credenciais da API. A API não cria nem migra tabelas ao iniciar.

## Componentes

| Componente | Porta do container | Função |
|---|---|---|
| rastreamento | 8080/TCP HTTP | Consulta entregas e grava ocorrências no PostgreSQL |
| operacoes | 8080/TCP HTTP | Página web; backend chama Rastreamento |
| PostgreSQL (fornecido por você) | 5432/TCP por padrão | Persistência de entregas e ocorrências |

Fluxo: navegador → Operações → Rastreamento → PostgreSQL.
A API também pode ser consultada diretamente pela URL externa que você criar.
Operações não acessa o banco diretamente. Seu navegador não precisa resolver o DNS interno da API.
As imagens de aplicação não precisam de PVC. Precisam de `/tmp` gravável para o Gunicorn.
Containerfiles usam usuário 1001 por padrão, porta não privilegiada, código legível por qualquer UID
 e não gravam em `/app`; preparados para UID arbitrário. Valide a execução com suas SCCs no cluster.

## Construção das imagens

Na raiz deste pacote, com Podman (ou substitua `podman` por `docker`):

```bash
podman build -f rastreamento/Containerfile -t vertice-rastreamento:1.0.0 rastreamento
podman build -f operacoes/Containerfile -t vertice-operacoes:1.0.0 operacoes
```

As imagens são locais: faça tag/push para o registry escolhido. Não há imagens publicadas por este pacote.
A base é `python:3.12-slim`; dependências diretas estão fixadas nos requirements.
A base e dependências transitivas não estão fixadas por digest/hash. Guarde os digests das imagens
construídas para repetir as implantações. Não contém segredos nas imagens.

## Configuração de Rastreamento

| Variável | Obrigatória | Padrão | Finalidade |
|---|---|---|---|
| `DB_HOST` | Sim | — | Host do PostgreSQL |
| `DB_PORT` | Não | `5432` | Porta do PostgreSQL |
| `DB_NAME` | Sim | — | Nome do banco |
| `DB_USER` | Sim | — | Usuário |
| `DB_PASSWORD` | Sim | — | Senha |
| `APP_ENV` | Não | `local` | Identificação visual/lógica, ex. dev ou homolog |
| `APP_VERSION` | Não | `1.0.0` no build | Versão reportada |
| `FAIL_MODE` | Não | `none` | `none`, `readiness` ou `business` |

As variáveis `DB_*` também são utilizadas por `python init_db.py`. O PostgreSQL precisa existir
antes desse comando. Banco ausente/esquema não inicializado: readiness e consultas retornam 503.
Conexão limitada a 3 s e SQL limitado a 3 s por comando. As conexões são abertas por requisição
 e fechadas ao final; não há pool. Limite inicial: dois workers e quatro threads por worker.

## Configuração de Operações

| Variável | Obrigatória | Padrão | Finalidade |
|---|---|---|---|
| `TRACKING_API_URL` | Sim | — | URL base de Rastreamento no mesmo ambiente, sem `/entregas` |
| `APP_ENV` | Não | `local` | Identificação exibida na página |
| `APP_VERSION` | Não | `1.0.0` no build | Versão exibida |

Exemplo de formato: `http://HOST-QUE-VOCE-DEFINIR:PORTA`.
O endereço é usado apenas pelo backend. Timeout HTTP de 4 s; erros da dependência aparecem na interface.

`APP_ENV` é um rótulo, não uma barreira de isolamento. Separação de credenciais, dados e acessos
entre times/ambientes depende dos recursos que você configurar. A aplicação permite que você valide isso.

## Contrato HTTP

| Aplicação | Método e caminho | Resposta esperada |
|---|---|---|
| Ambas | `GET /healthz` | 200 enquanto processo HTTP responde; não verifica dependências |
| Rastreamento | `GET /readyz` | 200 se consulta tabela entregas; 503 se falha |
| Operações | `GET /readyz` | 200 se readiness de Rastreamento responde 200; caso contrário 503 |
| Ambas | `GET /version` | Serviço, versão e ambiente |
| Rastreamento | `GET /entregas` | Lista de entregas |
| Rastreamento | `GET /entregas/ENT-001` | Entrega com ocorrências |
| Rastreamento | `POST /entregas/ENT-001/ocorrencias` | 201 com id e descrição |
| Operações | `GET /` | Interface web |
| Operações | `/api/entregas...` | Encaminha os três endpoints de negócio à API |

POST aceita JSON `{"descricao":"Veículo chegou ao centro de distribuição"}`.
Descrição: 1–500 caracteres após remover espaços das pontas. Código: `ENT-` seguido de três dígitos.
Código inválido ou payload inválido: 400. Entrega inexistente: 404. Banco indisponível: 503.
Ocorrências têm timestamp UTC. A página converte para o fuso do navegador.
Logs HTTP e erros resumidos vão para stdout/stderr; senhas e corpos de requisição não são registrados.

```bash
# Defina a URL que você publicou; exemplo local:
API_URL=http://localhost:8081
curl -fsS "$API_URL/entregas/ENT-001"
curl -fsS -H 'Content-Type: application/json' \
  -d '{"descricao":"Chegada ao centro de distribuição"}' \
  "$API_URL/entregas/ENT-001/ocorrencias"
```

## Versões defeituosas para recuperação

```bash
podman build -f rastreamento/Containerfile \
  --build-arg APP_VERSION=1.1.0-falha-readiness --build-arg FAIL_MODE=readiness \
  -t vertice-rastreamento:1.1.0-falha-readiness rastreamento

podman build -f rastreamento/Containerfile \
  --build-arg APP_VERSION=1.2.0-falha-funcional --build-arg FAIL_MODE=business \
  -t vertice-rastreamento:1.2.0-falha-funcional rastreamento
```

`readiness`: `/readyz` falha com 503, `/healthz` continua 200.
`business`: endpoints `/entregas...` falham com 500; readiness continua 200 se o banco funciona.
Assim, você pode testar tanto detecção por probe quanto detecção por teste funcional.
Recupere usando a imagem funcional original. Essas versões não mudam o esquema nem destroem dados.
Não há rollback automático implementado na aplicação. Se definir `FAIL_MODE`/`APP_VERSION` no runtime,
isso sobrescreve o padrão da imagem: retire o override para exercitar a recuperação pela troca da imagem.

## Escopo do laboratório

Sem autenticação de usuário final: qualquer pessoa com acesso HTTP aos endpoints pode consultar
 e registrar dados sintéticos. Os perfis de plataforma/suporte/desenvolvedores são permissões administrativas
que você implementará no OpenShift; não são contas nesta interface. Exposição externa da API também
expõe o endpoint de escrita, salvo restrição que você configurar. Este pacote não é uma aplicação de produção.
Não há CORS aberto, URLs remotas informadas pelo navegador ou interpolação de SQL com dados do usuário.
A interface apresenta descrições como texto, não HTML.

PostgreSQL não está empacotado como imagem personalizada. Use uma imagem/distribuição apropriada
ao seu ambiente e siga suas próprias variáveis de inicialização; `DB_*` são variáveis da API,
não necessariamente as variáveis aceitas pela imagem do banco.

## Testes

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r rastreamento/requirements.txt
python -m unittest discover -s tests -v
python tests/smoke.py --tracking http://URL-DA-API --operations http://URL-DE-OPERACOES
```

Os testes unitários substituem o banco e parte das chamadas HTTP por mocks. O smoke usa os serviços reais,
insere uma ocorrência única e verifica sua leitura. Veja `VALIDACAO.md`.
