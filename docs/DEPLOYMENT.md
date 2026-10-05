# Publicação e continuidade

## Configuração necessária

1. Hospedagem Python/WSGI, PostgreSQL, armazenamento persistente de mídia e domínio.
2. Ambiente privado com `DEBUG=false`, `SECRET_KEY` aleatória longa, `DATABASE_URL`, `ALLOWED_HOSTS`, `SITE_URL=https://...` e `CSRF_TRUSTED_ORIGINS=https://...`.
3. Stripe habilitada para a empresa, métodos de pagamento, chave do ambiente escolhido e segredo do webhook. Chaves live só após autorização.
4. SMTP com remetente e domínio verificados; informações reais da empresa, catálogo e políticas.
5. Tabela real de frete, regras de prazo e responsáveis pela operação.

## Preparar a entrega

Instale `requirements.txt` num ambiente isolado. Execute `migrate`, `collectstatic --noinput` e `check --deploy`. Execute os testes com a configuração da base PostgreSQL em homologação, sem transações live. Provisione administradores com TOTP em terminal privado.

Servidor WSGI compatível com Windows/Linux:

```text
waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
```

Use um proxy HTTPS na frente. Configure limites de upload, timeout, hosts e cabeçalhos. O servidor deve receber o esquema HTTPS corretamente: habilite `SECURE_PROXY_SSL_HEADER` apenas para um proxy confiável que remova cabeçalhos de origem; essa opção não está ligada automaticamente. Sem essa configuração ou terminação HTTPS correta, `SECURE_SSL_REDIRECT` pode causar loop.

WhiteNoise serve somente `staticfiles/`. Mídia de produto é servida por uma rota vinculada ao cadastro e deve usar volume persistente. Para grande volume, adaptar a um storage de objetos com URLs apropriadas e políticas de acesso.

Nunca expor a raiz do projeto por um servidor estático. Bloquear dotfiles e backups no proxy. Não usar o servidor de desenvolvimento em produção.

Agende `process_orders` a cada minuto com execução monitorada e concorrência limitada. Configure alertas para falhas de reconciliação, e-mail, banco e pedidos pagos fora do fluxo esperado. Webhooks assinados são a principal confirmação; a reconciliação é recuperação adicional.

## Backup e restauração

Crie backups criptografados do PostgreSQL e do volume de mídia em armazenamento restrito e separado. Defina retenção, frequência e responsáveis conforme a operação. Não guardar dumps em `static/` nem em repositório.

Teste periodicamente a restauração em uma base isolada. Verifique usuários, variantes, reservas e pedidos. Depois de restauração, reconcilie pagamentos no provedor antes de retomar vendas; a base pode ter sido restaurada num ponto anterior a pagamentos já realizados.

## Antes de habilitar vendas

- Testar Pix/cartão no sandbox oficial e processamento dos webhooks assinados.
- Testar SMTP, confirmação de conta e recuperação de senha.
- Executar concorrência e isolamento na mesma versão/configuração do PostgreSQL de produção.
- Aprovar fotos, composição, medidas, preços, estoque, frete e políticas reais.
- Revisar administração, permissões, TOTP, backups e restauração.
- Medir acessibilidade e desempenho no domínio final; dados locais não comprovam Core Web Vitals de campo.
- Fazer revisão de segurança da infraestrutura e teste independente conforme o risco.
- Autorizar publicação e transações live separadamente.

## Limites atuais

Cotação de transportadora e etiquetas não estão integradas; o frete é uma tabela configurável. Reembolsos parciais, recuperação de segundo fator, alertas de reposição e campanhas automatizadas não têm fluxo automático. Conteúdo legal e comercial está em preparação. Essas limitações devem entrar na decisão de lançamento, sem anunciar recursos indisponíveis.

Referências oficiais: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [Django OTP](https://django-otp-official.readthedocs.io/en/stable/auth.html), [Stripe Pix](https://docs.stripe.com/payments/pix), [Stripe webhooks](https://docs.stripe.com/webhooks).
