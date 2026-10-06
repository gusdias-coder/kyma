/* Buildless storefront concept. All links/assets are relative for project Pages. */
(() => {
  'use strict';
  const { products, categories, collections, copy, settings } = window.KYMA_DATA;
  const domain = window.KYMA_DOMAIN;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const escape = (value) => String(value).replace(/[&<>"']/g, (character) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[character]));
  const money = domain.money;
  const imagePath = (name) => `./assets/images/${name}.jpg`;
  const productLink = (product) => `./produto.html?id=${encodeURIComponent(product.id)}`;
  const categoryLink = (category) => `./catalogo.html?categoria=${encodeURIComponent(category.id)}`;
  const collectionLink = (collection) => `./catalogo.html?colecao=${encodeURIComponent(collection.id)}`;
  const paths = {
    arrow: '<path d="M4 12h15M13 5l7 7-7 7"/>', search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    bag: '<path d="M5 8h14l1 13H4L5 8Z"/><path d="M8 8V6a4 4 0 0 1 8 0v2"/>', heart: '<path d="M20.5 4.6a5.4 5.4 0 0 0-7.7 0L12 5.5l-.8-.9a5.4 5.4 0 0 0-7.7 7.7L12 21l8.5-8.7a5.4 5.4 0 0 0 0-7.7Z"/>',
    user: '<circle cx="12" cy="7" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>', menu: '<path d="M3 8h18M3 16h18"/>', close: '<path d="m5 5 14 14M19 5 5 19"/>',
    plus: '<path d="M12 5v14M5 12h14"/>', minus: '<path d="M5 12h14"/>', pause: '<path d="M8 5v14M16 5v14"/>', play: '<path d="m8 5 11 7-11 7V5Z"/>',
    check: '<path d="m5 12 4 4L19 6"/>', chevron: '<path d="m6 9 6 6 6-6"/>', filter: '<path d="M4 7h16M7 12h10M10 17h4"/>', mail: '<rect x="3" y="5" width="18" height="14" rx="0"/><path d="m3 6 9 7 9-7"/>',
  };
  const icon = (name, className = '') => `<svg class="icon ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.arrow}</svg>`;
  const logo = (className = '') => `<img class="wordmark ${className}" src="./assets/brand/kyma-logo.svg" alt="KYMA" width="238" height="50">`;
  const storageKey = 'kyma-preview-v1';
  let storageAvailable = true;
  let state;
  try { state = domain.sanitizeState(JSON.parse(localStorage.getItem(storageKey) || '{}'), products, settings.maxQuantity); }
  catch { state = domain.sanitizeState({}, products); storageAvailable = false; }
  let toastTimer;
  let selection = { size: '', color: '', qty: 1 };
  let currentProduct;
  let checkoutShipping = 0;
  let limit = 12;
  let dialogTrigger;
  const page = document.body.dataset.page || 'home';
  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify(state)); }
    catch { if (storageAvailable) { storageAvailable = false; toast(copy.storageUnavailable); } }
    updateCounters();
  }
  function toast(message) {
    const element = $('#toast'); element.textContent = message; element.classList.add('visible');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => element.classList.remove('visible'), 3600);
  }
  function updateCounters() {
    const count = state.cart.reduce((sum, item) => sum + item.qty, 0);
    $$('[data-bag-count]').forEach((element) => { element.textContent = count; });
    $$('.bag-trigger').forEach((element) => element.setAttribute('aria-label', `Abrir sacola, ${count} ${count === 1 ? 'peça' : 'peças'}`));
    $$('[data-favorite-count]').forEach((element) => { element.textContent = state.favorites.length; });
    $$('[data-favorite]').forEach((button) => {
      const liked = state.favorites.includes(button.dataset.favorite);
      button.setAttribute('aria-pressed', String(liked)); button.classList.toggle('selected', liked);
      button.setAttribute('aria-label', `${liked ? 'Remover dos' : 'Adicionar aos'} favoritos: ${products.find((product) => product.id === button.dataset.favorite)?.name || 'peça'}`);
    });
  }
  function openDialog(id, trigger) {
    const dialog = $(`#${id}`); if (!dialog) return;
    $$('dialog[open]').forEach((element) => element.close());
    dialogTrigger = trigger || document.activeElement;
    dialog.showModal(); document.body.classList.add('dialog-open');
    if (id === 'search-dialog') setTimeout(() => $('#search-query').focus(), 0);
    if (id === 'bag-dialog') renderBagDrawer();
  }
  function renderChrome() {
    $('#site-header').innerHTML = `
      <div class="announcement">KYMA · PRÉVIA DE CONCEITO · SEM VENDAS REAIS</div>
      <header class="header" id="header">
        <div class="header-main container">
          <button class="menu-trigger plain" data-dialog="menu-dialog" aria-label="Abrir menu">${icon('menu')}<span>MENU</span></button>
          <a class="logo-link" href="./index.html" aria-label="KYMA, início">${logo()}</a>
          <div class="header-actions">
            <button class="icon-button" data-dialog="search-dialog" aria-label="Buscar peças">${icon('search')}</button>
            <a class="icon-button account-link" href="./conta.html" aria-label="Minha conta">${icon('user')}</a>
            <button class="bag-trigger plain" data-dialog="bag-dialog" aria-label="Abrir sacola">${icon('bag')}<span class="bag-word">SACOLA</span><span data-bag-count class="count">0</span></button>
          </div>
        </div>
        <nav class="secondary-nav" aria-label="Navegação principal">
          <a href="./catalogo.html?novidades=1">NOVIDADES</a>
          <button class="plain" data-dialog="clothes-dialog" aria-haspopup="dialog">ROUPAS ${icon('chevron')}</button>
          <button class="plain" data-dialog="collections-dialog" aria-haspopup="dialog">COLEÇÕES ${icon('chevron')}</button>
          <a href="./universo-kyma.html">UNIVERSO KYMA</a>
        </nav>
      </header>`;
    $('#site-footer').innerHTML = `
      <section class="invitation container"><div><p class="eyebrow">ALÉM DO QUE VOCÊ VESTE</p><h2>Faça parte do universo.</h2><p>Ideias, referências e novas formas de se expressar.</p></div><a class="button button-dark" href="./universo-kyma.html">CONHECER A KYMA ${icon('arrow')}</a></section>
      <footer class="footer"><div class="footer-grid container"><div class="footer-brand">${logo()}<p>${copy.tagline}</p><p class="footer-caption">Marca independente. Expressão livre.</p></div><div><h3>EXPLORE</h3><a href="./catalogo.html">Todas as peças</a><a href="./colecoes.html">Coleções</a><a href="./favoritos.html">Seus favoritos</a><a href="./universo-kyma.html">Universo KYMA</a></div><div><h3>PODEMOS AJUDAR</h3><a href="./ajuda.html#tamanhos">Guia de tamanhos</a><a href="./ajuda.html#entregas">Entregas</a><a href="./ajuda.html#trocas">Trocas e devoluções</a><a href="./ajuda.html">Dúvidas frequentes</a></div><div><h3>TRANSPARÊNCIA</h3><a href="./privacidade.html">Privacidade</a><a href="./termos.html">Termos desta prévia</a><p>Cadastros e atendimento comercial serão disponibilizados no lançamento.</p></div></div><div class="footer-bottom container"><span>© ${new Date().getFullYear()} KYMA</span><span>${copy.preview}</span><button class="plain" data-clear-storage>Limpar dados deste navegador</button></div></footer>`;
    $('#overlays').innerHTML = `
      <dialog id="menu-dialog" class="menu-dialog" aria-labelledby="menu-title"><div class="dialog-head">${logo()}<button class="icon-button" data-close aria-label="Fechar menu">${icon('close')}</button></div><h2 id="menu-title" class="sr-only">Menu KYMA</h2><nav class="large-menu" aria-label="Menu completo"><a href="./catalogo.html?novidades=1">Novidades ${icon('arrow')}</a><a href="./catalogo.html">Todas as peças ${icon('arrow')}</a><a href="./colecoes.html">Coleções ${icon('arrow')}</a><a href="./universo-kyma.html">Universo KYMA ${icon('arrow')}</a></nav><div class="menu-category-list">${categories.map((category) => `<a href="${categoryLink(category)}">${category.name}</a>`).join('')}</div><div class="menu-extra"><a href="./favoritos.html">Favoritos <span data-favorite-count>0</span></a><a href="./ajuda.html">Ajuda</a><a href="./conta.html">Conta</a></div><p class="preview-note">${copy.preview}</p></dialog>
      ${megaMenu('clothes-dialog', 'Encontre o seu jeito.', categories, 'tailoring', 'ROUPAS')}
      ${megaMenu('collections-dialog', 'Uma coleção. Infinitas formas.', collections, 'hoodie-detail', 'COLEÇÕES')}
      <dialog id="search-dialog" class="search-dialog" aria-labelledby="search-title"><div class="dialog-head"><p class="eyebrow">ENCONTRE A SUA PRÓXIMA PEÇA</p><button class="icon-button" data-close aria-label="Fechar busca">${icon('close')}</button></div><h2 id="search-title">O que você procura?</h2><form action="./catalogo.html" method="get" class="search-form"><label for="search-query" class="sr-only">Nome, categoria ou coleção</label><input id="search-query" name="q" type="search" placeholder="Camiseta, moletom, alfaiataria..." maxlength="100" autocomplete="off" required><button class="icon-button" aria-label="Buscar">${icon('arrow')}</button></form><p class="eyebrow popular-label">EXPLORE TAMBÉM</p><div class="search-suggestions">${categories.slice(0,4).map((category) => `<a href="${categoryLink(category)}">${category.name} ${icon('arrow')}</a>`).join('')}</div></dialog>
      <dialog id="bag-dialog" class="bag-dialog" aria-labelledby="bag-title"><div class="dialog-head"><h2 id="bag-title">Sua sacola <span data-bag-count>0</span></h2><button class="icon-button" data-close aria-label="Fechar sacola">${icon('close')}</button></div><div id="bag-drawer-content"></div></dialog>
      <dialog id="size-dialog" class="standard-dialog" aria-labelledby="size-title"><div class="dialog-head"><h2 id="size-title">Guia de tamanhos</h2><button class="icon-button" data-close aria-label="Fechar guia de tamanhos">${icon('close')}</button></div><p>Medidas ilustrativas em centímetros. Compare com uma peça que você já usa.</p>${sizeTable()}<p class="preview-note">As medidas reais serão informadas para cada produto no lançamento.</p></dialog>
      <dialog id="info-dialog" class="standard-dialog" aria-labelledby="info-title"><div class="dialog-head"><h2 id="info-title">Sobre esta prévia</h2><button class="icon-button" data-close aria-label="Fechar informação">${icon('close')}</button></div><p>Você está explorando um conceito do KYMA. As peças, imagens e valores são referências para revisar o site. Não há vendas, pagamentos, contas ou envio de dados pessoais.</p><p>Seus favoritos e sua sacola ficam apenas neste navegador. Use “Limpar dados deste navegador” no rodapé para removê-los.</p><a class="text-link" href="./termos.html">Entender esta demonstração ${icon('arrow')}</a></dialog>
      <div id="toast" class="toast" role="status" aria-live="polite"></div>`;
    $$('dialog').forEach((dialog) => {
      dialog.addEventListener('close', () => { document.body.classList.remove('dialog-open'); if (dialogTrigger?.isConnected) dialogTrigger.focus(); });
      dialog.addEventListener('click', (event) => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } });
    });
    updateCounters();
  }
  function megaMenu(id, title, items, image, label) {
    return `<dialog id="${id}" class="mega-dialog" aria-labelledby="${id}-title"><div class="dialog-head"><span class="eyebrow">${label}</span><button class="icon-button" data-close aria-label="Fechar ${label.toLowerCase()}">${icon('close')}</button></div><div class="mega-grid"><div><h2 id="${id}-title">${title}</h2><nav class="mega-links" aria-label="${label}">${items.map((item) => `<a href="${id === 'clothes-dialog' ? categoryLink(item) : collectionLink(item)}">${item.name} ${icon('arrow')}</a>`).join('')}</nav></div><figure><img src="${imagePath(image)}" width="900" height="1200" alt="Referência editorial de moda" loading="lazy"><figcaption>LIBERDADE É A NOSSA FORMA.</figcaption></figure></div></dialog>`;
  }
  function favoriteButton(product, className = '') {
    return `<button class="favorite-button ${className}" data-favorite="${product.id}" aria-pressed="${state.favorites.includes(product.id)}" aria-label="Adicionar aos favoritos: ${escape(product.name)}">${icon('heart')}</button>`;
  }
  function productCard(product) {
    const category = categories.find((item) => item.id === product.category);
    return `<article class="product-card"><div class="product-image"><a href="${productLink(product)}" aria-label="Ver ${escape(product.name)}"><img src="${imagePath(product.images[0])}" alt="Referência visual para ${escape(product.name)}" width="900" height="1200" loading="lazy" decoding="async"><img class="second-image" src="${imagePath(product.images[1])}" alt="" width="900" height="1200" loading="lazy" decoding="async"></a>${favoriteButton(product)}<span class="product-badge">CONCEITO</span><a class="product-hover" href="${productLink(product)}">EXPLORAR PEÇA ${icon('arrow')}</a></div><div class="product-meta"><p class="product-category">${category.name}</p><h3><a href="${productLink(product)}">${product.name}</a></h3><div class="product-bottom"><span>${money(product.price)}</span><span class="card-swatches" role="img" aria-label="Cores ilustrativas: ${escape(product.colors.join(', '))}">${product.colors.map((color) => `<i class="swatch ${color === 'Preto' ? 'black' : 'white'}"></i>`).join('')}</span></div></div></article>`;
  }
  function collectionCard(collection, index) {
    return `<a class="collection-card" href="${collectionLink(collection)}"><img src="${imagePath(collection.image)}" alt="Referência editorial da coleção ${collection.name}" width="900" height="1200" loading="lazy"><div class="collection-overlay"><span class="eyebrow">COLEÇÃO ${String(index+1).padStart(2,'0')}</span><h3>${collection.name}</h3><p>${collection.note}</p><span class="collection-arrow">${icon('arrow')}</span></div></a>`;
  }
  function home() {
    const highlights = [products[12], products[24], products[8], products[4]];
    $('#main').innerHTML = `
      <section class="hero" aria-labelledby="hero-title"><picture><source media="(max-width: 600px)" srcset="./assets/images/hero-mobile.webp"><img class="hero-photo" src="./assets/images/hero.webp" alt="Cena ilustrativa: pessoa com moletom preto em passagem urbana ao anoitecer" width="1536" height="1024" fetchpriority="high"></picture><div class="hero-shade"></div><div class="hero-content container"><p class="eyebrow hero-eyebrow"><span class="little-line"></span> INDEPENDENTE POR NATUREZA</p><h1 id="hero-title">SEU ESTILO.<br><span>SUA PRESENÇA.</span></h1><p class="hero-description">${copy.tagline}</p><a class="button button-light" href="./catalogo.html">EXPLORAR A COLEÇÃO ${icon('arrow')}</a></div><div class="hero-bottom container"><span>KYMA — EXPRESSÃO LIVRE</span><a href="#novidades" class="scroll-indicator">EXPLORE ${icon('arrow')}</a><button class="plain motion-toggle" id="motion-toggle" aria-pressed="false" aria-label="Pausar movimento">${icon('pause')} <span>MOVIMENTO</span></button></div></section>
      <div class="value-strip"><div class="container value-grid"><span>ESTILO SEM RÓTULOS</span><span>FORMAS DE SE EXPRESSAR</span><span>SEU JEITO, SUA KYMA</span></div></div>
      <section id="novidades" class="section container"><div class="section-heading"><div><p class="eyebrow">O SEU PRÓXIMO CAPÍTULO</p><h2>Novas presenças.</h2></div><a class="text-link" href="./catalogo.html?novidades=1">EXPLORAR NOVIDADES ${icon('arrow')}</a></div><div class="product-grid home-products">${highlights.map(productCard).join('')}</div><p class="catalog-disclaimer">Catálogo de conceito. Fotos e valores ilustrativos.</p></section>
      <section class="category-section section container"><div class="section-heading"><div><p class="eyebrow">DIFERENTES FORMAS. A MESMA LIBERDADE.</p><h2>Vista o seu jeito.</h2></div><a class="text-link" href="./catalogo.html">TODAS AS PEÇAS ${icon('arrow')}</a></div><div class="category-grid">${[categories[0],categories[3],categories[6]].map((category,index) => `<a href="${categoryLink(category)}" class="category-tile"><img src="${imagePath(category.image)}" alt="Referência editorial de ${category.name.toLowerCase()}" width="900" height="1200" loading="lazy"><div><span class="eyebrow">0${index+1} / SUA FORMA</span><h3>${category.name}</h3>${icon('arrow')}</div></a>`).join('')}</div><nav class="category-chips" aria-label="Mais categorias">${categories.filter((category) => !['camisetas','moletons','alfaiataria'].includes(category.id)).map((category) => `<a href="${categoryLink(category)}">${category.name} ${icon('arrow')}</a>`).join('')}</nav></section>
      <section class="editorial"><div class="editorial-image"><img src="${imagePath('tailoring')}" alt="Referência de alfaiataria em cenário urbano" width="900" height="1200" loading="lazy"></div><div class="editorial-copy"><p class="eyebrow">ALFAIATARIA LIVRE</p><h2>O clássico.<br>Do seu jeito.</h2><p>Linhas que encontram a cidade.<br>Proporções que abrem espaço para você.</p><a href="./catalogo.html?colecao=alfaiataria-livre" class="button button-light">DESCOBRIR A COLEÇÃO ${icon('arrow')}</a><span class="editorial-footnote">KYMA / NOVAS PERSPECTIVAS</span></div></section>
      <div class="marquee" aria-hidden="true"><div>LIBERDADE PARA SER. &nbsp; KYMA. &nbsp; LIBERDADE PARA VESTIR. &nbsp; KYMA. &nbsp; LIBERDADE PARA SER. &nbsp; KYMA. &nbsp;</div></div>
      <section class="section collection-section"><div class="section-heading container"><div><p class="eyebrow">UM UNIVERSO DE POSSIBILIDADES</p><h2>Encontre a sua coleção.</h2></div><div class="collection-controls"><button class="icon-button" data-scroll-collections="-1" aria-label="Coleções anteriores">${icon('arrow','arrow-back')}</button><button class="icon-button" data-scroll-collections="1" aria-label="Próximas coleções">${icon('arrow')}</button></div></div><div class="collection-rail" id="collection-rail" tabindex="0" aria-label="Coleções, role horizontalmente">${collections.slice(0,5).map(collectionCard).join('')}</div><div class="container rail-note"><span>DESLIZE PARA DESCOBRIR</span><a class="text-link" href="./colecoes.html">VER AS 8 COLEÇÕES ${icon('arrow')}</a></div></section>
      <section class="universe-teaser container section"><div><p class="eyebrow">UNIVERSO KYMA</p><h2>Mais do que roupa.<br>Um jeito de estar.</h2></div><div><p>Seu estilo não precisa caber em uma definição. A KYMA nasce do encontro entre diferentes formas de vestir e a liberdade de ser você.</p><a class="text-link" href="./universo-kyma.html">CONHECER A NOSSA ESSÊNCIA ${icon('arrow')}</a></div></section>`;
    setupMotion();
  }
  function filtersFromUrl() {
    const params = new URLSearchParams(location.search);
    return { q: params.get('q') || '', category: params.get('categoria') || '', collection: params.get('colecao') || '', size: params.get('tamanho') || '', color: params.get('cor') || '', price: params.get('preco') || '', sort: params.get('ordenar') || '' };
  }
  function catalog() {
    const filters = filtersFromUrl();
    const category = categories.find((item) => item.id === filters.category);
    const collection = collections.find((item) => item.id === filters.collection);
    const title = filters.q ? 'Sua busca.' : collection?.name || category?.name || (new URLSearchParams(location.search).has('novidades') ? 'Novidades.' : 'Todas as formas.');
    $('#main').innerHTML = `<section class="catalog-intro container"><p class="eyebrow">${filters.q ? `RESULTADOS PARA “${escape(filters.q)}”` : 'EXPLORE A KYMA'}</p><h1>${title}</h1><p>${collection?.note || 'Encontre a peça que conversa com o seu jeito de ser.'}</p><p class="catalog-disclaimer">${copy.preview}. Imagens e valores ilustrativos.</p></section><section class="catalog container"><div class="catalog-toolbar"><button class="plain filter-toggle" id="filter-toggle" aria-expanded="false" aria-controls="catalog-filters">${icon('filter')} FILTROS</button><span id="result-count" role="status"></span><label class="sort-label" for="sort">ORDENAR <select id="sort" data-filter="ordenar"><option value="">Destaques</option><option value="menor-preco">Menor preço</option><option value="maior-preco">Maior preço</option><option value="nome">Nome A–Z</option></select></label></div><div class="catalog-layout"><form id="catalog-filters" class="catalog-filters"><label for="category-filter">CATEGORIA</label><select id="category-filter" data-filter="categoria"><option value="">Todas as peças</option>${categories.map((item) => `<option value="${item.id}">${item.name}</option>`).join('')}</select><label for="collection-filter">COLEÇÃO</label><select id="collection-filter" data-filter="colecao"><option value="">Todas as coleções</option>${collections.map((item) => `<option value="${item.id}">${item.name}</option>`).join('')}</select><label for="size-filter">TAMANHO</label><select id="size-filter" data-filter="tamanho"><option value="">Todos os tamanhos</option>${['PP','P','M','G','GG','36','38','40','42','44'].map((size) => `<option>${size}</option>`).join('')}</select><label for="color-filter">COR</label><select id="color-filter" data-filter="cor"><option value="">Todas as cores</option><option>Preto</option><option>Off-white</option></select><label for="price-filter">PREÇO ILUSTRATIVO</label><select id="price-filter" data-filter="preco"><option value="">Todos os valores</option><option value="15000">Até R$150</option><option value="25000">Até R$250</option><option value="35000">Até R$350</option></select><button type="button" class="text-link clear-filters" data-clear-filters>LIMPAR FILTROS ${icon('close')}</button><p>As variações servem para testar o catálogo. Não representam estoque real.</p></form><div><div id="catalog-grid" class="product-grid catalog-products"></div><div class="load-more-wrap"><button id="load-more" class="button button-outline">EXPLORAR MAIS PEÇAS ${icon('plus')}</button></div></div></div></section>`;
    const map = { categoria: filters.category, colecao: filters.collection, tamanho: filters.size, cor: filters.color, preco: filters.price, ordenar: filters.sort };
    $$('[data-filter]').forEach((element) => { element.value = map[element.dataset.filter]; });
    renderCatalogProducts();
  }
  function renderCatalogProducts() {
    const result = domain.filterProducts(products, filtersFromUrl());
    $('#result-count').textContent = `${result.length} ${result.length === 1 ? 'peça' : 'peças'}`;
    $('#catalog-grid').innerHTML = result.length ? result.slice(0,limit).map(productCard).join('') : `<div class="empty-state"><h2>Nenhuma peça por aqui.</h2><p>Esses filtros não encontraram resultados. Experimente outras combinações.</p><button class="button button-dark" data-clear-filters>LIMPAR FILTROS ${icon('arrow')}</button></div>`;
    $('#load-more').hidden = result.length <= limit; updateCounters();
  }
  function productPage() {
    currentProduct = products.find((product) => product.id === new URLSearchParams(location.search).get('id'));
    if (!currentProduct) return notFound();
    selection = { size: '', color: currentProduct.colors[0], qty: 1 };
    const category = categories.find((item) => item.id === currentProduct.category);
    document.title = `${currentProduct.name} — KYMA`;
    $('#main').innerHTML = `<div class="container breadcrumb"><a href="./index.html">Início</a><span>/</span><a href="${categoryLink(category)}">${category.name}</a><span>/</span><span>${currentProduct.name}</span></div><section class="pdp container"><div class="gallery"><div class="gallery-track" id="gallery-track">${currentProduct.images.map((name,index) => `<button class="gallery-image" data-zoom="${index}" aria-label="Ampliar referência ${index+1}"><img src="${imagePath(name)}" alt="Referência editorial ${index+1} para ${escape(currentProduct.name)}" width="900" height="1200" ${index ? 'loading="lazy"' : 'fetchpriority="high"'}></button>`).join('')}</div><div class="gallery-thumbs">${currentProduct.images.map((name,index) => `<button class="thumb ${index ? '' : 'active'}" data-gallery="${index}" aria-label="Ver referência ${index+1}" aria-pressed="${!index}"><img src="${imagePath(name)}" alt="" width="72" height="90"></button>`).join('')}<span>TOQUE NA FOTO PARA AMPLIAR</span></div></div><div class="product-details"><p class="eyebrow">${collections.find((item) => item.id === currentProduct.collection).name}</p><h1>${currentProduct.name}</h1><p class="pdp-price">${money(currentProduct.price)}</p><p class="product-description">${currentProduct.description}</p><p class="preview-note">${copy.illustration}</p><div class="selection-head"><span>COR: <strong id="selected-color">${selection.color}</strong></span></div><div class="color-buttons" role="group" aria-label="Selecionar cor">${currentProduct.colors.map((color,index) => `<button class="color-option ${index ? '' : 'active'}" data-color="${color}" aria-label="${color}" aria-pressed="${!index}"><span class="swatch ${color === 'Preto' ? 'black' : 'white'}"></span></button>`).join('')}</div><div class="selection-head"><span>TAMANHO: <strong id="selected-size">ESCOLHA O SEU</strong></span><button class="plain guide-link" data-dialog="size-dialog">Guia de tamanhos</button></div><div class="size-buttons" role="group" aria-label="Selecionar tamanho">${currentProduct.sizes.map((size) => `<button data-size="${size}" aria-pressed="false">${size}</button>`).join('')}</div><p id="size-error" class="field-error" role="alert" hidden>Escolha um tamanho para adicionar a peça.</p><div class="add-actions"><button class="button button-dark" data-add-product>ADICIONAR À SACOLA ${icon('plus')}</button>${favoriteButton(currentProduct,'pdp-favorite')}</div><div class="product-accordions"><details open><summary>DETALHES DA PEÇA ${icon('plus')}</summary><p>Composição ilustrativa: ${currentProduct.composition}. As fotos são referências editoriais e podem diferir do produto proposto.</p></details><details><summary>CUIDADOS ${icon('plus')}</summary><p>Referência de cuidado: lavar com cores semelhantes, evitar alvejante e secar à sombra. Consulte sempre a etiqueta de uma peça real.</p></details><details><summary>ENTREGAS E TROCAS ${icon('plus')}</summary><p>Esta demonstração não realiza entregas. Preços, prazos e políticas reais serão disponibilizados antes do lançamento.</p><a href="./ajuda.html">Entender esta prévia</a></details></div><div class="shipping-calculator"><label for="product-shipping">SIMULAR FRETE POR ESTADO</label><div class="shipping-row"><select id="product-shipping"><option value="">Selecione seu estado</option>${stateOptions()}</select><button class="icon-button" data-product-shipping aria-label="Calcular frete ilustrativo">${icon('arrow')}</button></div><p id="product-shipping-result" role="status">Valores de exemplo, sem consulta externa.</p></div></div></section><section class="section container"><div class="section-heading"><div><p class="eyebrow">CONTINUE EXPLORANDO</p><h2>Outras formas de ser.</h2></div></div><div class="product-grid">${products.filter((product) => product.id !== currentProduct.id && product.collection === currentProduct.collection).slice(0,4).map(productCard).join('')}</div></section><div class="mobile-add"><span>${money(currentProduct.price)}<small>VALOR ILUSTRATIVO</small></span><button class="button button-dark" data-add-product>ADICIONAR ${icon('plus')}</button></div><dialog id="zoom-dialog" class="zoom-dialog" aria-label="Referência ampliada"><button class="icon-button zoom-close" data-close aria-label="Fechar imagem ampliada">${icon('close')}</button><img id="zoom-image" src="${imagePath(currentProduct.images[0])}" alt="Referência ampliada de ${escape(currentProduct.name)}"></dialog>`;
    const zoomDialog = $('#zoom-dialog'); zoomDialog.addEventListener('close', () => { document.body.classList.remove('dialog-open'); if (dialogTrigger?.isConnected) dialogTrigger.focus(); });
    $('#gallery-track').addEventListener('scroll', () => { const track = $('#gallery-track'); const index = Math.round(track.scrollLeft / track.clientWidth); $$('[data-gallery]').forEach((button) => { const active = Number(button.dataset.gallery) === index; button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active)); }); }, { passive: true });
  }
  function stateOptions() {
    return ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'].map((uf) => `<option value="${uf}">${uf}</option>`).join('');
  }
  function bagItems() {
    return state.cart.map((item) => {
      const product = products.find((entry) => entry.id === item.id); const key = escape(domain.key(item));
      return `<article class="bag-item"><a href="${productLink(product)}"><img src="${imagePath(product.images[0])}" alt="Referência de ${escape(product.name)}" width="120" height="150"></a><div><p class="product-category">${categories.find((entry) => entry.id === product.category).name}</p><h3><a href="${productLink(product)}">${product.name}</a></h3><p class="bag-variant">${item.color} / ${item.size}</p><div class="bag-item-bottom"><div class="quantity-stepper" role="group" aria-label="Quantidade de ${escape(product.name)}"><button data-quantity="-1" data-key="${key}" aria-label="Diminuir quantidade de ${escape(product.name)}">${icon('minus')}</button><span>${item.qty}</span><button data-quantity="1" data-key="${key}" aria-label="Aumentar quantidade de ${escape(product.name)}">${icon('plus')}</button></div><span>${money(product.price * item.qty)}</span></div><button class="remove-item" data-remove="${key}">Remover</button></div></article>`;
    }).join('');
  }
  function emptyBag() { return `<div class="empty-state">${icon('bag')}<h2>Espaço para o seu estilo.</h2><p>Sua sacola está vazia. Explore as peças e encontre a sua próxima presença.</p><a class="button button-dark" href="./catalogo.html">EXPLORAR PEÇAS ${icon('arrow')}</a></div>`; }
  function renderBagDrawer() {
    $('#bag-drawer-content').innerHTML = state.cart.length ? `<p class="preview-note">SACOLA DE DEMONSTRAÇÃO · SEM VENDAS REAIS</p><div class="drawer-items">${bagItems()}</div><div class="drawer-total"><span>Subtotal ilustrativo</span><strong>${money(domain.totals(state,products).subtotal)}</strong></div><a class="button button-dark full-width" href="./sacola.html">VER MINHA SACOLA ${icon('arrow')}</a><button class="plain continue-shopping" data-close>Continuar explorando</button>` : emptyBag();
    updateCounters();
  }
  function summary(shipping = 0) {
    const totals = domain.totals(state,products,shipping);
    return `<div class="summary-line"><span>Subtotal</span><span>${money(totals.subtotal)}</span></div>${totals.discount ? `<div class="summary-line"><span>Cupom de teste KYMA10</span><span>− ${money(totals.discount)}</span></div>` : ''}<div class="summary-line"><span>Frete ilustrativo</span><span>${shipping ? money(shipping) : 'Calcular na simulação'}</span></div><div class="summary-line total"><span>Total${shipping ? '' : ' sem frete'}</span><strong>${money(totals.total)}</strong></div>`;
  }
  function bagPage() {
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">AS SUAS ESCOLHAS</p><h1>Sua sacola.</h1><p>${copy.preview}. Nada será cobrado.</p></section>${state.cart.length ? `<section class="bag-layout container section-topless"><div id="bag-page-items">${bagItems()}</div><aside class="order-summary"><h2>Resumo da sacola</h2>${summary()}<form class="coupon-form" id="coupon-form"><label for="coupon">CUPOM DE DEMONSTRAÇÃO</label><div class="shipping-row"><input id="coupon" name="coupon" placeholder="Use KYMA10 para testar" maxlength="20" value="${state.coupon}"><button class="plain" type="submit">APLICAR</button></div><p id="coupon-message" role="status">${state.coupon ? 'Cupom de teste aplicado: 10% de desconto.' : 'O cupom serve apenas para testar a interface.'}</p></form><a href="./checkout.html" class="button button-dark full-width">SIMULAR CHECKOUT ${icon('arrow')}</a><a class="text-link" href="./catalogo.html">CONTINUAR EXPLORANDO ${icon('arrow')}</a><p class="preview-note">Sem pagamentos, reserva de estoque ou pedidos reais.</p></aside></section>` : `<section class="container section-topless">${emptyBag()}</section>`}`;
  }
  function checkoutPage() {
    if (!state.cart.length) { $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">CHECKOUT DE DEMONSTRAÇÃO</p><h1>Uma escolha de cada vez.</h1></section><div class="container">${emptyBag()}</div>`; return; }
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">SOMENTE PARA EXPLORAR A EXPERIÊNCIA</p><h1>Seu próximo passo.</h1><p>Simulação de checkout. Nenhum dado pessoal ou pagamento é solicitado.</p></section><section class="checkout-layout container section-topless"><div class="checkout-steps"><details open><summary><span>01</span> CONTATO ${icon('chevron')}</summary><div class="checkout-step"><h2>Você está testando o KYMA.</h2><p>O checkout real solicitará contato e endereço em uma hospedagem preparada para comércio. Aqui, você pode conhecer o fluxo sem se cadastrar.</p></div></details><details open><summary><span>02</span> ENTREGA ${icon('chevron')}</summary><div class="checkout-step"><label for="checkout-state">ESTADO PARA SIMULAR FRETE</label><select id="checkout-state"><option value="">Selecione um estado</option>${stateOptions()}</select><p id="checkout-shipping-note" role="status">Escolha um estado para ver um valor de exemplo.</p></div></details><details open><summary><span>03</span> PAGAMENTO ${icon('chevron')}</summary><div class="checkout-step"><fieldset class="payment-options"><legend>Escolha uma experiência para simular</legend><label><input type="radio" name="payment-demo" value="pix" checked><span><strong>Pix</strong><small>Prévia da confirmação. Sem QR Code ou cobrança.</small></span></label><label><input type="radio" name="payment-demo" value="card"><span><strong>Cartão</strong><small>Sem solicitar número do cartão.</small></span></label></fieldset><button class="button button-dark" id="simulate-checkout">CONCLUIR DEMONSTRAÇÃO ${icon('arrow')}</button><p id="checkout-error" class="field-error" role="alert" hidden>Selecione um estado para concluir a simulação.</p></div></details></div><aside class="order-summary"><h2>Suas escolhas</h2><div class="checkout-mini-items">${state.cart.map((item) => { const product = products.find((entry) => entry.id === item.id); return `<div><img src="${imagePath(product.images[0])}" alt="" width="60" height="75"><span>${product.name}<small>${item.color} / ${item.size} / ${item.qty} un.</small></span></div>`; }).join('')}</div><div id="checkout-summary">${summary()}</div><p class="preview-note">Valores ilustrativos. A demonstração não cria pedido, não envia dados e não realiza cobrança.</p><a class="text-link" href="./sacola.html">EDITAR SACOLA ${icon('arrow')}</a></aside></section>`;
  }
  function favoritesPage() {
    const favorites = products.filter((product) => state.favorites.includes(product.id));
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">GUARDE O QUE COMBINA COM VOCÊ</p><h1>Suas referências.</h1><p>Favoritos salvos apenas neste navegador.</p></section><section class="container section-topless">${favorites.length ? `<div class="product-grid">${favorites.map(productCard).join('')}</div>` : `<div class="empty-state">${icon('heart')}<h2>O começo de uma nova combinação.</h2><p>Toque no coração de uma peça para encontrá-la aqui depois.</p><a class="button button-dark" href="./catalogo.html">EXPLORAR PEÇAS ${icon('arrow')}</a></div>`}</section>`;
  }
  function collectionsPage() {
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">UM UNIVERSO. OITO PERSPECTIVAS.</p><h1>Coleções.</h1><p>Referências que encontram o seu jeito de vestir.</p></section><section class="container section-topless collections-grid">${collections.map(collectionCard).join('')}</section>`;
  }
  function universePage() {
    $('#main').innerHTML = `<section class="story-hero"><img src="./assets/images/hero.webp" alt="Cena urbana ilustrativa criada para o conceito KYMA" width="1536" height="1024"><div class="container"><p class="eyebrow">UNIVERSO KYMA</p><h1>Liberdade<br>é presença.</h1></div></section><section class="story-intro container section"><p class="eyebrow">A NOSSA ESSÊNCIA</p><h2>Você não precisa caber<br>em uma única definição.</h2><p>Às vezes, sua expressão é urbana. Em outras, é leve, clássica ou impossível de rotular. A KYMA é uma proposta de marca independente que parte dessa liberdade: vestir diferentes versões de quem você é.</p></section><section class="story-grid container section"><img src="${imagePath('jacket')}" alt="Referência editorial com jaqueta preta" width="900" height="1200" loading="lazy"><div><p class="eyebrow">SEM RÓTULOS. COM INTENÇÃO.</p><h2>A forma é sua.</h2><p>Uma silhueta pode dizer muito. Mas nenhuma peça precisa dizer tudo. Nosso universo reúne linhas urbanas, alfaiataria e camadas para criar combinações que tenham a sua presença.</p><a class="text-link" href="./colecoes.html">EXPLORAR AS COLEÇÕES ${icon('arrow')}</a></div></section><section class="manifesto"><div class="container"><p class="eyebrow">MANIFESTO KYMA</p><h2>Diferentes formas<br>de vestir.<br><span>A mesma liberdade<br>de ser você.</span></h2><a class="button button-light" href="./catalogo.html">ENCONTRAR O MEU ESTILO ${icon('arrow')}</a></div></section><section class="container section story-footnote"><p>Esta é uma apresentação de conceito. As fotografias são referências editoriais, sem vínculo comercial ou endosso das pessoas retratadas.</p></section>`;
  }
  function sizeTable() {
    return `<div class="table-scroll"><table><caption>Referência de camisetas e moletons</caption><thead><tr><th scope="col">Tamanho</th><th scope="col">Largura</th><th scope="col">Comprimento</th></tr></thead><tbody>${[['PP',48,66],['P',51,69],['M',54,72],['G',57,75],['GG',60,78]].map((row) => `<tr>${row.map((cell,index) => `<${index ? 'td' : 'th scope="row"'}>${cell}</${index ? 'td' : 'th'}>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function helpPage() {
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">PODEMOS AJUDAR</p><h1>Clareza em cada passo.</h1><p>Informações sobre esta apresentação do KYMA.</p></section><section class="help-layout container section-topless"><nav aria-label="Nesta página"><a href="#previa">Sobre a prévia</a><a href="#tamanhos">Tamanhos</a><a href="#entregas">Entregas</a><a href="#trocas">Trocas</a><a href="#pagamentos">Pagamentos</a></nav><div><details id="previa" open><summary>POSSO COMPRAR NESTE SITE? ${icon('plus')}</summary><p>Ainda não. Este site é uma apresentação navegável para testar o visual, o catálogo, a sacola e o fluxo de checkout. Nenhum pedido ou pagamento real é realizado.</p></details><details id="tamanhos"><summary>COMO ESCOLHER UM TAMANHO? ${icon('plus')}</summary><p>Use o guia ilustrativo para explorar a seleção de tamanho. As medidas definitivas serão publicadas por produto quando houver peças reais.</p>${sizeTable()}</details><details id="entregas"><summary>COMO FUNCIONA O FRETE? ${icon('plus')}</summary><p>O simulador usa uma tabela de exemplo por estado. Não consulta transportadoras, não cria etiquetas e não promete entrega.</p></details><details id="trocas"><summary>COMO FUNCIONAM TROCAS E DEVOLUÇÕES? ${icon('plus')}</summary><p>Não há compras nesta prévia. Antes da operação comercial, a marca deverá publicar políticas reais, com dados do negócio e revisão profissional no Brasil.</p></details><details id="pagamentos"><summary>HÁ PIX OU CARTÃO NESTA PRÉVIA? ${icon('plus')}</summary><p>Há uma demonstração visual da escolha de pagamento. Ela não gera Pix, não solicita dados de cartão e não processa dinheiro.</p></details><details><summary>ONDE FICAM MINHA SACOLA E MEUS FAVORITOS? ${icon('plus')}</summary><p>No armazenamento deste navegador. Não são enviados a um servidor, não sincronizam entre dispositivos e podem ser apagados no rodapé.</p></details></div></section>`;
    if (location.hash) { const target = document.getElementById(location.hash.slice(1)); if (target instanceof HTMLDetailsElement) target.open = true; }
  }
  function accountPage() {
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">SEU ESPAÇO NA KYMA</p><h1>Uma conta. Mais possibilidades.</h1></section><section class="account-preview container section-topless"><div>${icon('user')}<h2>Estamos preparando esse encontro.</h2><p>Contas, endereços e histórico de pedidos estarão disponíveis quando a loja real for lançada. Esta prévia não solicita cadastro, senha ou informações pessoais.</p><a class="button button-dark" href="./favoritos.html">VER MEUS FAVORITOS ${icon('heart')}</a><a class="text-link" href="./catalogo.html">EXPLORAR A KYMA ${icon('arrow')}</a></div><img src="${imagePath('tailoring-detail')}" alt="Referência editorial de alfaiataria" width="900" height="1200" loading="lazy"></section>`;
  }
  function legalPage() {
    const privacy = page === 'privacy';
    $('#main').innerHTML = `<section class="page-intro container"><p class="eyebrow">TRANSPARÊNCIA</p><h1>${privacy ? 'Privacidade nesta prévia.' : 'Termos da demonstração.'}</h1></section><article class="legal-copy container section-topless">${privacy ? `<h2>O que esta versão guarda</h2><p>Esta aplicação guarda apenas escolhas de produtos, variações, quantidades, favoritos e cupom de teste no armazenamento local do navegador. Não solicita CPF, endereço, e-mail ou dados de cartão.</p><h2>Envio de dados e hospedagem</h2><p>A aplicação não inclui formulários de coleta, ferramentas de análise de visitas ou chamadas a serviços de pagamento. Arquivos, fontes e mídias estão incluídos na própria hospedagem. O serviço que hospedar o site poderá tratar dados técnicos de acesso conforme sua própria política.</p><h2>Como apagar suas escolhas</h2><p>Use o botão “Limpar dados deste navegador” no rodapé. Você também pode limpar os dados do site nas configurações do navegador.</p><h2>Antes do lançamento comercial</h2><p>A loja real precisará de uma política específica para suas operações e fornecedores. Este texto descreve somente a demonstração e não substitui essa política.</p>` : `<h2>Finalidade desta versão</h2><p>KYMA é um conceito original de marca e de experiência de moda. Esta versão serve para apresentação, aprendizado e avaliação da navegação. Não constitui oferta comercial.</p><h2>Produtos e valores</h2><p>Nomes, preços, composição, tamanhos, cores, prazos e fretes são dados ilustrativos. As fotografias são referências editoriais licenciadas e uma imagem gerada para o conceito; não representam um inventário real ou endosso das pessoas retratadas.</p><h2>Simulação de checkout</h2><p>A simulação não cria pedido comercial, não reserva estoque, não processa pagamentos e não envia confirmação por e-mail. Não insira informações pessoais ou financeiras para testar este site.</p><h2>GitHub Pages</h2><p>O pacote foi preparado como uma apresentação estática. Para operar comércio eletrônico, é necessário escolher uma hospedagem que permita esse uso e implementar as integrações seguras de servidor.</p><h2>Créditos e limites</h2><p>Os créditos e fontes das mídias estão documentados no pacote. A marca e o código deste conceito são originais; nenhuma outra loja foi copiada.</p>`}<p class="preview-note">Informações desta prévia, atualizadas em 05/10/2026.</p></article>`;
  }
  function notFound() {
    $('#main').innerHTML = `<section class="not-found container"><p class="eyebrow">404 / UM NOVO CAMINHO</p><h1>Essa peça<br>mudou de lugar.</h1><p>A página não está disponível. Continue explorando o universo KYMA.</p><a class="button button-dark" href="./catalogo.html">ENCONTRAR OUTRAS FORMAS ${icon('arrow')}</a></section>`;
  }
  function addProduct(trigger) {
    if (!currentProduct) return;
    if (!selection.size) { $('#size-error').hidden = false; const firstSize = $('[data-size]'); firstSize.scrollIntoView({ block:'center', behavior: reducedMotion() ? 'instant' : 'smooth' }); firstSize.focus(); return; }
    const item = { id:currentProduct.id, size:selection.size, color:selection.color, qty:1 };
    const existing = state.cart.find((entry) => domain.key(entry) === domain.key(item));
    if (existing?.qty >= settings.maxQuantity) return toast(copy.maxQuantity);
    if (existing) existing.qty += 1; else state.cart.push(item);
    save(); toast(copy.cartAdded); openDialog('bag-dialog',trigger);
  }
  function refreshCartViews() {
    const focused = document.activeElement;
    const focusKey = focused?.dataset?.key;
    const focusQuantity = focused?.dataset?.quantity;
    save(); if ($('#bag-dialog').open) renderBagDrawer();
    if (page === 'bag') bagPage();
    if (page === 'checkout') { checkoutShipping = 0; checkoutPage(); }
    if (focusKey && focusQuantity) $$('[data-quantity]').find((button) => button.dataset.key === focusKey && button.dataset.quantity === focusQuantity)?.focus();
  }
  function reducedMotion() { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; }
  function setupMotion() {
    const hero = $('.hero'); const toggle = $('#motion-toggle');
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    let pausedByUser = false; let inView = true; let hasStarted = false;
    let video;
    function allowed() { return !reducedMotion() && !connection?.saveData && !['slow-2g','2g','3g'].includes(connection?.effectiveType); }
    function sync() {
      const active = !pausedByUser && !document.hidden && inView && allowed();
      hero.classList.toggle('motion-enabled', active);
      toggle.setAttribute('aria-pressed', String(pausedByUser));
      toggle.setAttribute('aria-label', pausedByUser ? 'Retomar movimento' : 'Pausar movimento');
      toggle.innerHTML = `${icon(pausedByUser ? 'play' : 'pause')} <span>${pausedByUser ? 'RETOMAR' : 'MOVIMENTO'}</span>`;
      if (video) { if (active) video.play().catch(() => { video.style.opacity = '0'; }); else video.pause(); }
    }
    function startVideo() {
      if (hasStarted || !allowed()) return; hasStarted = true;
      const panel = document.createElement('div'); panel.className = 'hero-film';
      panel.innerHTML = `<video muted loop playsinline preload="metadata" aria-label="Clipe editorial ilustrativo de moda"><source src="./assets/video/${window.innerWidth <= 600 ? 'fashion-mobile' : 'fashion-desktop'}.webm" type="video/webm"><source src="./assets/video/${window.innerWidth <= 600 ? 'fashion-mobile' : 'fashion-desktop'}.mp4" type="video/mp4"></video><span class="film-label">MODA EM MOVIMENTO / 01</span>`;
      hero.append(panel); video = $('video',panel); video.muted = true;
      video.addEventListener('playing', () => panel.classList.add('ready'));
      video.addEventListener('error', () => panel.remove()); sync();
    }
    toggle.addEventListener('click', () => { pausedByUser = !pausedByUser; sync(); });
    document.addEventListener('visibilitychange', sync);
    const observer = new IntersectionObserver((entries) => { inView = entries[0].isIntersecting; sync(); }, { threshold:0.1 }); observer.observe(hero);
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', sync);
    sync(); if ('requestIdleCallback' in window) window.requestIdleCallback(startVideo,{timeout:1800}); else setTimeout(startVideo,1200);
  }
  function finishSimulation() {
    if (!$('#checkout-state').value) { $('#checkout-error').hidden = false; $('#checkout-state').focus(); return; }
    const method = $('input[name="payment-demo"]:checked').value === 'pix' ? 'Pix' : 'Cartão';
    $('#main').innerHTML = `<section class="simulation-done container"><span class="done-icon">${icon('check')}</span><p class="eyebrow">DEMONSTRAÇÃO CONCLUÍDA</p><h1>Experiência explorada.</h1><p>Você testou o fluxo com ${method} e um total ilustrativo de <strong>${money(domain.totals(state,products,checkoutShipping).total)}</strong>.</p><div class="simulation-warning"><strong>Nenhum pedido foi criado. Nenhum pagamento foi realizado.</strong><p>Sua sacola continua salva para você testar outras combinações.</p></div><a class="button button-dark" href="./catalogo.html">CONTINUAR EXPLORANDO ${icon('arrow')}</a><a class="text-link" href="./sacola.html">VOLTAR À SACOLA ${icon('arrow')}</a></section>`;
    window.scrollTo({top:0,behavior:'instant'}); $('#main').focus();
  }
  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('button, a'); if (!trigger) return;
    if (trigger.dataset.dialog) openDialog(trigger.dataset.dialog,trigger);
    if (trigger.hasAttribute('data-close')) trigger.closest('dialog')?.close();
    if (trigger.dataset.favorite) {
      const id = trigger.dataset.favorite; state.favorites = state.favorites.includes(id) ? state.favorites.filter((entry) => entry !== id) : [...state.favorites,id]; save();
      toast(state.favorites.includes(id) ? 'Referência salva nos favoritos.' : 'Referência removida dos favoritos.'); if (page === 'favorites') { favoritesPage(); ($('#main [data-favorite]') || $('#main .button'))?.focus(); } updateCounters();
    }
    if (trigger.dataset.size) { selection.size = trigger.dataset.size; $('#selected-size').textContent = selection.size; $('#size-error').hidden = true; $$('[data-size]').forEach((button) => { const selected = button === trigger; button.classList.toggle('active',selected); button.setAttribute('aria-pressed',String(selected)); }); }
    if (trigger.dataset.color) { selection.color = trigger.dataset.color; $('#selected-color').textContent = selection.color; $$('[data-color]').forEach((button) => { const selected = button === trigger; button.classList.toggle('active',selected); button.setAttribute('aria-pressed',String(selected)); }); }
    if (trigger.hasAttribute('data-add-product')) addProduct(trigger);
    if (trigger.dataset.quantity) { const item = state.cart.find((entry) => domain.key(entry) === trigger.dataset.key); if (item) { if (item.qty + Number(trigger.dataset.quantity) > settings.maxQuantity) return toast(copy.maxQuantity); item.qty += Number(trigger.dataset.quantity); state.cart = state.cart.filter((entry) => entry.qty > 0); refreshCartViews(); } }
    if (trigger.dataset.remove) { state.cart = state.cart.filter((entry) => domain.key(entry) !== trigger.dataset.remove); refreshCartViews(); toast('Peça removida da sacola.'); }
    if (trigger.hasAttribute('data-clear-storage')) { state = domain.sanitizeState({},products); save(); refreshCartViews(); if (page === 'favorites') favoritesPage(); toast('Suas escolhas neste navegador foram apagadas.'); }
    if (trigger.hasAttribute('data-clear-filters')) { history.replaceState({},'',location.pathname); limit = 12; catalog(); }
    if (trigger.id === 'filter-toggle') { const open = trigger.getAttribute('aria-expanded') !== 'true'; trigger.setAttribute('aria-expanded',String(open)); $('#catalog-filters').classList.toggle('filters-open',open); }
    if (trigger.id === 'load-more') { limit += 12; renderCatalogProducts(); }
    if (trigger.dataset.gallery) { $('#gallery-track').scrollTo({left:Number(trigger.dataset.gallery) * $('#gallery-track').clientWidth,behavior:reducedMotion() ? 'instant' : 'smooth'}); }
    if (trigger.hasAttribute('data-zoom')) { $('#zoom-image').src = imagePath(currentProduct.images[Number(trigger.dataset.zoom)]); openDialog('zoom-dialog',trigger); }
    if (trigger.hasAttribute('data-product-shipping')) { const quote = domain.shippingByState($('#product-shipping').value); $('#product-shipping-result').textContent = quote ? `Exemplo: ${money(quote.price)} · ${quote.days}. Sem entrega real.` : 'Selecione um estado para simular o frete.'; }
    if (trigger.dataset.scrollCollections) $('#collection-rail').scrollBy({left: Number(trigger.dataset.scrollCollections) * 420,behavior:reducedMotion() ? 'instant' : 'smooth'});
    if (trigger.id === 'simulate-checkout') finishSimulation();
  });
  document.addEventListener('change', (event) => {
    const target = event.target;
    if (target.dataset.filter) { const params = new URLSearchParams(location.search); if (target.value) params.set(target.dataset.filter,target.value); else params.delete(target.dataset.filter); const query = params.toString(); history.replaceState({},'',`${location.pathname}${query ? `?${query}` : ''}`); limit = 12; renderCatalogProducts(); }
    if (target.id === 'checkout-state') { const quote = domain.shippingByState(target.value); checkoutShipping = quote?.price || 0; $('#checkout-summary').innerHTML = summary(checkoutShipping); $('#checkout-shipping-note').textContent = quote ? `Exemplo de entrega: ${quote.days}. Frete ${money(quote.price)}.` : 'Selecione um estado para ver um valor de exemplo.'; $('#checkout-error').hidden = true; }
  });
  document.addEventListener('submit', (event) => {
    if (event.target.id === 'coupon-form') { event.preventDefault(); const coupon = $('#coupon').value.trim().toUpperCase(); if (coupon && coupon !== 'KYMA10') { $('#coupon-message').textContent = 'Cupom não reconhecido. Use KYMA10 para testar o desconto.'; return; } state.coupon = coupon; save(); bagPage(); $('#coupon')?.focus(); }
    if (event.target.id === 'catalog-filters') event.preventDefault();
  });
  window.addEventListener('storage', (event) => { if (event.key !== storageKey) return; try { state = domain.sanitizeState(JSON.parse(event.newValue || '{}'),products); } catch { state = domain.sanitizeState({},products); } updateCounters(); if ($('#bag-dialog').open) renderBagDrawer(); if (page === 'bag') bagPage(); if (page === 'favorites') favoritesPage(); if (page === 'checkout') checkoutPage(); });
  renderChrome();
  const renderers = { home, catalog, product:productPage, bag:bagPage, checkout:checkoutPage, favorites:favoritesPage, collections:collectionsPage, universe:universePage, help:helpPage, account:accountPage, privacy:legalPage, terms:legalPage, '404':notFound };
  (renderers[page] || notFound)(); updateCounters();
  const sentinel = document.createElement('div'); sentinel.className = 'scroll-sentinel'; document.body.prepend(sentinel);
  new IntersectionObserver((entries) => $('#header').classList.toggle('compact',!entries[0].isIntersecting)).observe(sentinel);
  if (!storageAvailable) toast(copy.storageUnavailable);
})();
