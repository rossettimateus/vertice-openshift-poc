# Entrada de um terceiro time

Procedimento proposto para um novo time de desenvolvimento, por exemplo Integrações. Homologação é um ambiente, não um terceiro time. Esta documentação não registra uma execução completa de onboarding.

## Identidade

1. Identifique o Secret referenciado pelo Identity Provider HTPasswd existente no OAuth. Não exporte nem publique seu conteúdo.
2. Em uma estação autorizada, obtenha uma cópia protegida do arquivo HTPasswd.
3. Adicione o novo usuário com `htpasswd -B ARQUIVO NOVO_USUARIO`, fornecendo a senha interativamente. Não use `-c` em um arquivo existente, pois ele recria o arquivo.
4. Atualize a chave `htpasswd` do mesmo Secret com o arquivo completo. Preserve os usuários existentes.
5. Valide o novo login. O objeto User surge no primeiro login bem-sucedido.
6. Adicione o usuário ao grupo do time. Não é necessário criar outro Identity Provider para cada equipe.

## Ambientes e autorizações

Defina os projetos de desenvolvimento e homologação do novo time; configure seus grupos e bindings conforme a matriz de acesso desejada. Aplique os padrões de recursos, armazenamento e rede escolhidos. Não copie credenciais de outro ambiente.

O snapshot `deploy/observado.json` mostra o que foi observado na PoC, não um template de onboarding completo. Revise o RBAC antes de reutilizá-lo: o snapshot de leitura não concede autonomia completa de publicação.

## Aceite

- Novo usuário autentica e consegue publicar e investigar a aplicação no escopo autorizado.
- Não altera recursos dos demais times.
- Suporte consulta diagnóstico sem modificar recursos nem obter credenciais.
- Fluxos internos necessários funcionam e acessos indevidos são bloqueados.
- Usuários anteriores continuam autenticando.
- Outro administrador consegue repetir o procedimento seguindo este documento.

Referências: [HTPasswd no OpenShift](https://docs.redhat.com/en/documentation/openshift_container_platform/4.20/html/authentication_and_authorization/configuring-identity-providers), [RBAC no Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/).
