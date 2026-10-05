# Fotografias reais de referência — KYMA

A interface usa fotografias reais publicadas no Pexels no hero, nas quatro categorias, nos oito produtos de referência, nos três banners e na seção Universo KYMA.

Origem e licença conferidas em 4 de outubro de 2026: [Pexels License](https://www.pexels.com/license/). A plataforma permite uso em sites e e-commerce. Não se presume endosso das pessoas ou marcas fotografadas nem que as peças pertençam à KYMA. O catálogo permanece identificado como demonstração. Para vendas reais, cadastre as fotos da mercadoria efetivamente oferecida.

| Arquivo original otimizado | Fotógrafo | Página de origem |
| --- | --- | --- |
| `graphic-back.webp` | Ardit Mbrati | [Pexels 16831785](https://www.pexels.com/photo/back-view-of-a-young-man-wearing-a-graphic-t-shirt-16831785/) |
| `graphic-cartoon.webp` | Hanna Alves | [Pexels 29052570](https://www.pexels.com/photo/casual-streetwear-with-cartoon-graphic-t-shirt-29052570/) |
| `graphic-red.webp` | Ab Pixels | [Pexels 31959038](https://www.pexels.com/photo/stylish-man-in-vibrant-urban-streetwear-31959038/) |
| `graphic-jersey.webp` | Rules Effects | [Pexels 29613985](https://www.pexels.com/photo/young-man-in-urban-outfit-with-graphic-jersey-29613985/) |
| `graphic-blue.webp` | Fernando Ortiz P. | [Pexels 34421369](https://www.pexels.com/photo/man-wearing-blue-graphic-tee-in-urban-setting-34421369/) |
| `hoodie-black.webp` | Ali Pazani | [Pexels 3799378](https://www.pexels.com/photo/man-in-black-hoodie-3799378/) |
| `denim-jacket.webp` | Felix Young | [Pexels 19243412](https://www.pexels.com/photo/woman-wearing-denim-jacket-on-a-street-19243412/) |
| `cargo-street.webp` | John Ric Cabatuan | [Pexels 5366340](https://www.pexels.com/photo/model-in-cargo-pants-5366340/) |
| `denim-street.webp` | Luis Quintero | [Pexels 16069737](https://www.pexels.com/photo/a-man-wearing-black-t-shirt-and-jeans-16069737/) |

As fotos estão em `static/images/streetwear/`, com registro estruturado em `sources.json`. Conversão para WebP, correção de orientação EXIF, remoção de metadados e recorte de enquadramento: nenhuma estampa, roupa, pessoa ou marca foi gerada ou substituída.

Hero atual: `hoodie-black.webp`, fotografia de Ali Pazani, com recorte vertical específico para celular. A versão do moletom preto foi retomada a pedido do usuário. `graphic-red-product.webp` e `hoodie-black-product.webp` são recortes das respectivas fotos de origem. Categorias e banners reutilizam fotos da seleção. Arquivos de mídia instalados usam o prefixo `kyma-reference-`.

O comando local `python manage.py seed` instala as fotografias junto ao catálogo de referência, sem acesso à internet. `python manage.py streetwear_photos` atualiza uma instalação demonstrativa existente e preserva fotografias enviadas pelo proprietário, pedidos e quantidades de estoque. O comando é recusado em produção. `python scripts/assets.py` baixa novamente apenas a seleção documentada.

Logo: screenshot fornecida pelo usuário, exibida por recorte CSS em `logo-reference.jpeg`. As fotografias externas não compõem o logo.

## Experimento anterior com vídeos — desativado

O experimento usava oito MP4 fornecidos no prompt, de `https://pub-86dc5b5484314368ac5436a674b0d919.r2.dev/designs/`: `video-1.mp4`, `video-1-reverse.mp4`, `video-2.mp4`, `video-2-reverse.mp4`, `video-3.mp4`, `video-3-reverse.mp4`, `video-4.mp4` e `video-4-reverse.mp4`. Eles não são carregados pela home atual.

A permissão para esse host de mídia foi removida da CSP após a retomada do hero fotográfico. Não foi verificada uma licença comercial independente dos vídeos do experimento.

## Ampliação das coleções — 04/10/2026

Foram selecionadas 23 fotografias reais nas páginas públicas https://www.pexels.com/search/streetwear/ e https://www.pexels.com/search/fashion/ . Dessas, 16 fotografias distintas foram usadas nas novas peças. Os arquivos locais são WebP, com orientação corrigida e metadados removidos. Não houve geração nem substituição de roupas, pessoas ou estampas.

Registro por ID, fotógrafo/identificador da origem, URL de aquisição e licença: static/images/expanded/sources.json. Os mesmos IDs são definidos em scripts/expand_assets.py para aquisição reproduzível. A seleção visual ficou registrada em screenshots/expanded-photo-selection.jpg. Não foram usadas fotografias da Gucci.

As fotos representam estilos, com dados comerciais e tamanhos demonstrativos. Cadastre imagens próprias e dados reais antes de vender. A licença pública do Pexels foi consultada novamente em https://www.pexels.com/license/ .
