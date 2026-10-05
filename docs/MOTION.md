# Animações atuais da KYMA

## Hero do moletom preto

A base visual foi retomada conforme solicitado: fotografia real de moletom preto, cenário urbano escuro e recorte específico para celular. A foto tem movimento de câmera suave, com zoom e deslocamento em trechos de 18 segundos, alternando a direção. A câmera pausa fora da tela e em segundo plano; a preferência por movimento reduzido a desativa. Não há vídeo nem painel de transformação da LTX na página atual.

Os textos entram com opacidade, máscara e deslocamento discretos, em 760 ms no desktop e 520 ms no celular. O botão comercial aparece somente por opacidade, mantendo sua posição estável durante um clique.

## Navegação inspirada na direção de luxo

- Marca central e cabeçalho que se compacta ao rolar: 460 ms.
- Mega menus com entrada de 360 ms e links em sequência de 24 ms.
- Painel lateral e busca: entrada de 460 ms e saída de 240 ms.
- Escape, fechamento pelo controle e retorno de foco usam o diálogo nativo. O usuário pode navegar pelo teclado sem esperar animações.
- A preferência por movimento reduzido elimina essas transições.

A referência pública foi o site oficial da Gucci. O site bloqueou a inspeção visual automática; os efeitos implementados são uma adaptação para a KYMA. Não foram copiados código, imagens ou identidade da Gucci. Detalhes e estados em NAVIGATION.md.

## Coleções e vitrines

Categorias, produtos, coleções e banners aparecem suavemente ao chegar à tela: 660 ms, intervalo de 70 ms entre colunas. Elementos interativos aparecem por opacidade, mantendo seus controles fixos. Essa escolha evita que um cancelamento da animação ao receber foco mova o botão antes do clique terminar.

As fotografias têm zoom discreto de 2,5% no hover; banners ampliam 4,5%. Links ganham sublinhado progressivo. A galeria troca fotos após carregar a próxima imagem, com transição de 320 ms. Hover é restrito a dispositivos com mouse. Os formulários comerciais continuam funcionais sem JavaScript.
