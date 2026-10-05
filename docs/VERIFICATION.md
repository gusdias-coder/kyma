# Verificação e estado da entrega

## Implementado

- Loja KYMA separada, páginas responsivas, logo da referência em janela visual e hero com entrada/zoom finitos, redução de movimento e interação desktop discreta.
- Catálogo, coleções, busca, filtros, variantes, cadastro de fotos e componentes comerciais editáveis.
- Banco relacional local com migrations; carrinho persistente em sessão de servidor.
- Cadastro, ativação por e-mail, login, recuperação, perfil, endereços e pedidos isolados por cliente.
- Compra de visitante com acesso por sessão e link assinado de acompanhamento.
- Gestão Django com TOTP obrigatório, funções de catálogo/atendimento/administração e auditoria.
- Checkout com totais no servidor, cupons, frete por tabela e reserva de estoque.
- Simulação local de pagamento claramente identificada; integração Stripe Checkout, assinatura de webhooks, reconciliação, idempotência e reembolso integral.
- Novidades com confirmação e cancelamento; análise interna opcional.
- Proteções de sessão, CSRF, CSP, arquivos públicos, validação de uploads e limites de tentativa.

## Verificado neste computador

41 testes automatizados passaram com encerramento normal do processo. Cobertura: contas, recuperação, TOTP administrativo, autorização, isolamento de pedidos/endereços, CSRF com origem correta e incorreta, preço no servidor, reserva concorrente da última unidade, notificações repetidas/divergentes, estados de pagamento, reembolso integral, cadastro de novidades, uploads, arquivos privados e integração da vitrine com estoque/carrinho.

Verificações do Django e consistência das migrations passaram. Auditoria das dependências não encontrou vulnerabilidades conhecidas no momento da execução; isso não comprova ausência de falhas. Auditoria dos assets não encontrou valores privados do ambiente ou marcadores de credenciais.

Navegador: home e página de produto, escolha de tamanho, carrinho, checkout com total calculado, aprovação demonstrativa e limpeza do carrinho foram conferidos. Menu móvel abriu corretamente; não houve imagens quebradas nem rolagem horizontal na verificação a 390 px. Capturas em `docs/screenshots/`.

Um conflito entre a política de referência da página e a validação de formulário foi encontrado no navegador e corrigido mantendo proteção CSRF e política `same-origin`. Uma concorrência no encerramento da base de testes do Windows também foi corrigida. As imagens de demonstração são pequenas (hero aproximadamente 86 KB e versão móvel 27 KB); não foi medida a experiência real de usuários.

## Revisão de código

Revisão local aplicada com foco em autorização, segredos, concorrência e consistência. Foram corrigidos sobrescrita potencial de reserva durante edição administrativa, sobrescrita de situação de pagamento ao editar rastreamento, tratamento de submissões repetidas, remoção de produto inativo do carrinho e liberação do checkout para nova tentativa após falha.

## Não validado externamente

- Stripe: nenhum pagamento foi enviado ao serviço. Credenciais e conta habilitada não foram fornecidas. Testes locais validam contratos e fluxo, não uma integração executada no sandbox oficial.
- SMTP: e-mails locais foram gravados em arquivos privados; entrega externa não foi executada.
- PostgreSQL: não há serviço local configurado. A tentativa de carregar o driver nativo para verificar a configuração de produção foi bloqueada pelo Controle de Aplicativo do Windows. Nenhuma proteção do Windows foi desativada. Validar em ambiente de hospedagem compatível antes de publicar.
- `check --deploy`: não pôde completar nesta máquina por esse bloqueio do driver; a configuração de produção não foi certificada.
- HTTPS, domínio, proxy, storage, backups, restauração e monitoramento exigem ambiente real.
- Não houve auditoria independente de segurança, avaliação completa de acessibilidade nem medição de Core Web Vitals de campo.

## Dependências para vender

Conta e credenciais do pagamento; SMTP verificado; PostgreSQL; domínio/hospedagem; catálogo, fotos e logo vetorial originais; dados da empresa; regras reais de frete e políticas revisadas; administradores provisionados com TOTP; execução das verificações de homologação e autorização de publicação.

A aplicação local está disponível para revisão. Ela não deve ser apresentada como loja já autorizada para vendas reais ou como sistema invulnerável.

## Atualização de fotografias reais — 04/10/2026

- Nove fotografias reais do Pexels empacotadas, incluindo oito fotografias distintas no catálogo e assets editoriais reutilizados; origem e licença em ASSETS.md.
- Hero gerado e ilustrações de roupas substituídos em todas as áreas renderizadas.
- Verificação HTTP de 10 páginas (home, loja e oito produtos) e 18 URLs de imagem: todas responderam com sucesso e conteúdo; nenhuma ilustração de roupa renderizada.
- Navegador: home em 1366 × 900 e 390 × 844, sem rolagem horizontal; hero e todas as fotos carregados após visitar as seções com carregamento gradual.
- Produto estampado: tamanho e cor selecionados, adição ao carrinho confirmada e foto real carregada. Apenas a peça acrescentada para essa verificação foi removida depois.
- Verificação de configuração Django e auditoria de credenciais em arquivos públicos aprovadas.
- Capturas atuais: screenshots/streetwear-desktop.jpg, streetwear-mobile.jpg, streetwear-hero.jpg e streetwear-cart.jpg. Capturas anteriores representam a versão visual anterior.

## Animações premium e hero cinematográfico — 04/10/2026

- JavaScript passou pela verificação de sintaxe; configuração Django e auditoria de assets públicos aprovadas.
- Navegador em 1366 × 900: entrada do título observada com opacidade 0 e deslocamento de 24 px; depois terminou em opacidade 1 e sem deslocamento. Categorias observadas entrando em sequência, sem mensagens de erro no console.
- Movimento contínuo do hero observado em amostras de matrizes de transformação diferentes ao longo do tempo, inclusive em viewport móvel.
- Navegador em 390 × 844: menu abriu com aria-expanded=true; painel sobreposto; Escape fechou, retornou ao botão, terminou hidden=true e inert presente; sem rolagem horizontal.
- Preferência por movimento reduzido e pausa fora da tela/em segundo plano revisadas no código; não foi alterada a preferência do sistema operacional do usuário para essa conferência.
- Especificação e limites em docs/MOTION.md.

## Correção da loja e integração do editorial — 04/10/2026

- A demonstração visual standalone foi integrada à home comercial da KYMA. A entrada antiga em `ltx-world-model/index.html` agora encaminha para a loja local na porta 3001.
- Hero com oito vídeos, quatro controles e respectivos retornos; CTA de compra local sempre disponível. Catálogo, contas, gestão e checkout permanecem no backend existente.
- Adição ao carrinho diretamente nas vitrines, com tamanho/cor obrigatório e somente variantes disponíveis. Preço e estoque continuam validados no servidor.
- 41 testes passaram em 28,713 segundos. Os três testes adicionados cobrem a integração dos vídeos/links/CSP, preço autoritativo na compra pela vitrine e ocultação da última unidade reservada.
- Sintaxe de cinematic.js e store.js, configuração Django, consistência das migrations e auditoria de assets públicos aprovadas.
- Navegador: busca por Cartoon, seleção M/Branco, adição ao carrinho, quantidade 2 e subtotal R$278, retorno para 1 e checkout R$139 + R$19 de entrega = R$158. Aprovação demonstrativa gerou confirmação e esvaziou o carrinho. Foram usados dados fictícios; nenhuma cobrança real.
- Desktop em 1366 × 900: todos os quatro pares de transição concluídos. Celular em 390 × 844: Look/Voltar funcionaram, CTA de compra permaneceu visível, menu abriu e fechou com Escape; sem rolagem horizontal.
- Capturas: screenshots/kyma-commerce-desktop.png, kyma-commerce-mobile.png e kyma-order-verified.png. As capturas anteriores representam versões anteriores do hero.
- Stripe, e-mail externo, PostgreSQL e publicação continuam dependentes das configurações descritas acima; esta atualização não os declara homologados.

## Base retomada, catálogo ampliado e navegação premium — 04/10/2026

- A pedido do usuário, o hero do moletom preto e cenário urbano escuro foi restaurado. Nenhum vídeo LTX é carregado; o movimento de câmera da fotografia foi preservado, com recorte móvel.
- Catálogo local: 24 peças, oito categorias, oito coleções, todas com produtos. Dezesseis novas fotografias reais foram usadas nas peças adicionais; não há foto de produto ausente nem página de produto com erro na verificação dos 24 registros.
- Cabeçalho com marca central, compactação ao rolar, mega menus por categoria/coleção, painel lateral e busca. Referência estrutural: site oficial da Gucci; inspeção visual bloqueada por Access Denied, portanto não se declara reprodução exata de seus efeitos.
- 43 testes passaram em 30,215 segundos. A ampliação é idempotente, preserva quantidades existentes e é recusada para loja real/produção. Auditoria de assets públicos, configuração Django e consistência das migrations aprovadas.
- Navegador: mega menus abrem por clique, links de coleção filtram o catálogo; busca encontrou Moletom Atlântico; painel lateral abriu e Escape fechou, devolvendo foco e liberando rolagem.
- Compra demonstrativa de Moletom Atlântico M/Branco: R$259 + R$19 = R$278. No celular, clique adicionou Blazer Arquitetura M/Branco: R$429 + R$19 = R$448. As peças usadas na verificação foram removidas do carrinho, sem gerar pedido ou cobrança.
- Foi corrigido um deslocamento de botões causado pelo cancelamento da entrada ao receber foco: cartões e botões comerciais agora aparecem por opacidade, sem mudar a posição durante o clique. A compactação do cabeçalho também mantém o espaço ocupado na página.
- Verificação visual em 1366 × 900 e 390 × 844: sem rolagem horizontal, logo e ícones separados, hero móvel carregado (700 px), menu móvel e links de coleções funcionais. As oito fotografias das coleções carregaram no navegador.
- Capturas atuais: screenshots/kyma-luxury-desktop.png, kyma-luxury-mobile.png, kyma-luxury-mega-menu.png e kyma-luxury-mobile-menu.png. As anteriores são históricas.
- Esta atualização não configura cobranças reais nem publicação. As dependências de produção listadas neste documento permanecem necessárias.
