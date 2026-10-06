/* Illustrative catalog for the GitHub Pages presentation. No real inventory. */
(() => {
  'use strict';
  const categories = [
    { id: 'camisetas', name: 'Camisetas', image: 'graphic', detail: 'shirt', composition: '100% algodão', base: 9900, names: ['Camiseta Essencial', 'Camiseta Forma', 'Camiseta Horizonte', 'Camiseta Movimento'] },
    { id: 'calcas', name: 'Calças', image: 'denim', detail: 'graphic', composition: '98% algodão, 2% elastano', base: 24900, names: ['Calça Denim Livre', 'Calça Reta Urbana', 'Calça Ampla', 'Calça Cargo Horizonte'] },
    { id: 'camisas', name: 'Camisas', image: 'shirt', detail: 'tailoring-detail', composition: '100% algodão', base: 18900, names: ['Camisa Linha Leve', 'Camisa Contorno', 'Camisa Textura', 'Camisa Essencial'] },
    { id: 'moletons', name: 'Moletons', image: 'hoodie', detail: 'hoodie-detail', composition: '80% algodão, 20% poliéster', base: 27900, names: ['Moletom Presença', 'Moletom Urbano', 'Moletom Amplitude', 'Moletom Horizonte'] },
    { id: 'estampas', name: 'Estampas', image: 'graphic', detail: 'shirt', composition: '100% algodão', base: 12900, names: ['Camiseta Arte Livre', 'Camiseta Manifesto', 'Camiseta Traço', 'Camiseta Frequência'] },
    { id: 'camadas', name: 'Camadas', image: 'jacket', detail: 'denim', composition: '100% algodão', base: 22900, names: ['Sobreposição Urbano', 'Colete Linha', 'Overshirt Estrutura', 'Camada Essencial'] },
    { id: 'alfaiataria', name: 'Alfaiataria', image: 'tailoring', detail: 'tailoring-detail', composition: '68% poliéster, 30% viscose, 2% elastano', base: 38900, names: ['Blazer Alfaiataria Livre', 'Blazer Contorno', 'Calça de Alfaiataria', 'Colete Estrutura'] },
    { id: 'jaquetas', name: 'Jaquetas', image: 'jacket', detail: 'denim', composition: '100% algodão', base: 34900, names: ['Jaqueta Denim Noite', 'Jaqueta Horizonte', 'Jaqueta Urbana', 'Jaqueta Textura'] },
  ];
  const collections = [
    { id: 'street-culture', name: 'Street Culture', note: 'A cidade como ponto de partida.', image: 'hoodie-detail' },
    { id: 'alfaiataria-livre', name: 'Alfaiataria Livre', note: 'Novas formas de ocupar o espaço.', image: 'tailoring' },
    { id: 'essenciais', name: 'Essenciais', note: 'Menos ruído. Mais você.', image: 'shirt' },
    { id: 'entre-formas', name: 'Entre Formas', note: 'Silhuetas que não seguem regras.', image: 'denim' },
    { id: 'noite-urbana', name: 'Noite Urbana', note: 'Presença mesmo depois do último raio.', image: 'jacket' },
    { id: 'arte-em-movimento', name: 'Arte em Movimento', note: 'Vista aquilo que você sente.', image: 'graphic' },
    { id: 'texturas', name: 'Texturas', note: 'Detalhes que mudam tudo.', image: 'tailoring-detail' },
    { id: 'novos-horizontes', name: 'Novos Horizontes', note: 'O próximo passo é seu.', image: 'hoodie' },
  ];
  const slugify = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const products = categories.flatMap((category, categoryIndex) => category.names.map((name, index) => ({
    id: slugify(name), name, category: category.id,
    collection: collections[(categoryIndex + index) % collections.length].id,
    price: category.base + index * 2000,
    sizes: category.id === 'calcas' ? ['36', '38', '40', '42', '44'] : ['PP', 'P', 'M', 'G', 'GG'],
    colors: index % 2 ? ['Off-white', 'Preto'] : ['Preto', 'Off-white'],
    images: [category.image, category.detail], composition: category.composition,
    description: 'Uma proposta de silhueta contemporânea, pensada para combinar com o seu jeito de vestir. Linhas simples, proporções livres e espaço para a sua personalidade.',
    demo: true, sequence: categoryIndex * 4 + index,
  })));
  const copy = {
    brand: 'KYMA', tagline: 'Diferentes formas de vestir. A mesma liberdade de ser você.',
    preview: 'Prévia de conceito · sem vendas reais',
    illustration: 'Fotos de referência e valores ilustrativos. Este item não está à venda.',
    cartAdded: 'Peça adicionada à sua sacola de demonstração.',
    storageUnavailable: 'Seu navegador bloqueou o armazenamento. As escolhas duram apenas nesta página.',
    maxQuantity: 'O limite desta demonstração é de 10 unidades por variação.',
  };
  window.KYMA_DATA = { categories, collections, products, copy, settings: { version: 1, maxQuantity: 10, currency: 'BRL', mode: 'preview' } };
})();
