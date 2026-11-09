# Entrada de um terceiro time

Organizei este procedimento para receber um novo time de desenvolvimento, por exemplo Integrações, usando o provedor de identidade existente. Cada equipe precisa dos seus usuários, grupo, ambientes e permissões.

## Identidade

1. Identifique o Secret referenciado pelo Identity Provider HTPasswd existente no OAuth. Não exporte nem publique seu conteúdo.
2. Em uma estação autorizada, obtenha uma cópia protegida do arquivo HTPasswd.
3. Adicione o novo usuário com `htpasswd -B ARQUIVO NOVO_USUARIO`, fornecendo a senha interativamente. Não use `-c` em um arquivo existente, pois ele recria o arquivo.
4. Atualize a chave `htpasswd` do mesmo Secret com o arquivo completo. Preserve os usuários existentes.
5. Valide o novo login. O objeto User surge no primeiro login bem-sucedido.
6. Adicione o usuário ao grupo do time. Não é necessário criar outro Identity Provider para cada equipe.

## Ambientes e autorizações

Defina os projetos de desenvolvimento e homologação do novo time; configure seus grupos e bindings conforme a matriz de acesso desejada. Aplique os padrões de recursos, armazenamento e rede escolhidos. Não copie credenciais de outro ambiente.

Use `deploy/observado.json` como referência das configurações do laboratório. Complete os bindings do novo time conforme as operações que ele precisa executar; os bindings de leitura não permitem publicar aplicações.

## Aceite

- Novo usuário autentica e consegue publicar e investigar a aplicação no escopo autorizado.
- Não altera recursos dos demais times.
- Suporte consulta diagnóstico sem modificar recursos nem obter credenciais.
- Fluxos internos necessários funcionam e acessos indevidos são bloqueados.
- Usuários anteriores continuam autenticando.
- Outro administrador consegue repetir o procedimento seguindo este documento.

Referências: [HTPasswd no OpenShift](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/authentication_and_authorization/configuring-identity-providers), [RBAC no Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/).
