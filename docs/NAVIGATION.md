# Componente: navegação premium KYMA

A navegação conecta o catálogo ampliado, as coleções e os serviços da loja. Referência consultada em 04/10/2026: https://www.gucci.com/us/en/ . A estrutura pública foi acessível; a inspeção visual pelo navegador recebeu Access Denied. O resultado é uma adaptação da direção de navegação de luxo, sem afirmar identidade exata com os efeitos atuais da Gucci e sem reutilizar seu logo, fotos ou código.

## Variantes e estados

| Estado | Visual | Comportamento |
| --- | --- | --- |
| Desktop inicial | Marca central, Menu à esquerda, serviços à direita e navegação secundária | Novidades, Roupas, Coleções e Universo KYMA |
| Desktop compacto | Marca menor e linha secundária recolhida | A rolagem compacta após 120 px; retorna ao início abaixo de 12 px |
| Mega menu | Fundo branco, links em duas colunas e duas fotos editoriais | Hover abre; clique fixa a abertura; novo clique ou Escape fecha |
| Painel lateral | Gaveta à esquerda com categorias, coleções e serviços | Dialog modal, com detalhes expansíveis |
| Busca | Painel superior, campo e sugestões de coleções | GET para a busca real da loja |
| Celular | Marca central menor, Menu e três ícones | Painel lateral substitui a navegação secundária |
| Sem JavaScript | Links comerciais adicionais | Loja, coleções, busca e conta acessíveis por links normais |

## Tokens e movimento

Branco #fff, texto #111, borda #e5e5e0. Curva cubic-bezier(.22,1,.36,1); cabeçalho 460 ms, entrada do menu 360 ms, painel 460 ms e saída 240 ms. A redução de altura do cabeçalho é compensada pela margem, mantendo o espaço ocupado e evitando deslocar a página durante um clique. As fotos ampliam apenas 2,5% no hover.

## Acessibilidade

Botões de abertura usam aria-controls e aria-expanded. O diálogo nativo mantém o foco dentro do painel; Escape fecha, devolve o foco ao acionador e libera a rolagem. O mega menu também responde a ArrowDown e Escape. Links da linha compactada ficam inertes. Controles têm áreas de toque apropriadas; existe preferência por movimento reduzido. Os controles comerciais não se deslocam durante a animação de entrada, inclusive quando ela é cancelada ao receber foco.

## Integração

Markup em templates/navigation.html; estilos e comportamento em static/navigation.css e static/navigation.js. Categorias e coleções vêm do banco. Todos os links comerciais permanecem dentro da KYMA. Não há API key, biblioteca remota ou script externo nesse componente.
