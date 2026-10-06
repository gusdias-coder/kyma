/* Pure preview rules. Real commerce must revalidate all values on a server. */
(() => {
  'use strict';
  const money = (cents) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);
  const normalize = (value) => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const key = (item) => `${item.id}|${item.size}|${item.color}`;
  function sanitizeState(value, products, limit = 10) {
    const source = value && typeof value === 'object' ? value : {};
    const validIds = new Set(products.map((product) => product.id));
    const cart = [];
    for (const raw of Array.isArray(source.cart) ? source.cart : []) {
      if (!raw || typeof raw !== 'object') continue;
      const product = products.find((item) => item.id === raw.id);
      if (!product || !product.sizes.includes(raw.size) || !product.colors.includes(raw.color) || !Number.isInteger(raw.qty) || raw.qty < 1) continue;
      const item = { id: product.id, size: raw.size, color: raw.color, qty: Math.min(raw.qty, limit) };
      const existing = cart.find((entry) => key(entry) === key(item));
      if (existing) existing.qty = Math.min(limit, existing.qty + item.qty);
      else cart.push(item);
    }
    return { cart, favorites: [...new Set((Array.isArray(source.favorites) ? source.favorites : []).filter((id) => validIds.has(id)))], coupon: source.coupon === 'KYMA10' ? 'KYMA10' : '' };
  }
  function totals(state, products, shipping = 0) {
    const subtotal = state.cart.reduce((sum, item) => sum + (products.find((product) => product.id === item.id)?.price || 0) * item.qty, 0);
    const discount = state.coupon === 'KYMA10' ? Math.floor(subtotal / 10) : 0;
    return { subtotal, discount, shipping, total: subtotal - discount + shipping };
  }
  function shippingByState(uf) {
    const groups = { sudeste: ['SP','RJ','MG','ES'], sul: ['PR','SC','RS'], centro: ['DF','GO','MT','MS'], nordeste: ['AL','BA','CE','MA','PB','PE','PI','RN','SE'], norte: ['AC','AP','AM','PA','RO','RR','TO'] };
    if (groups.sudeste.includes(uf)) return { price: 1990, days: '3 a 5 dias úteis' };
    if (groups.sul.includes(uf)) return { price: 2490, days: '4 a 7 dias úteis' };
    if (groups.centro.includes(uf)) return { price: 2990, days: '5 a 8 dias úteis' };
    if (groups.nordeste.includes(uf)) return { price: 3490, days: '6 a 10 dias úteis' };
    if (groups.norte.includes(uf)) return { price: 3990, days: '8 a 12 dias úteis' };
    return null;
  }
  function filterProducts(products, filters) {
    const words = normalize(filters.q || '').trim().split(/\s+/).filter(Boolean);
    const matches = products.filter((product) => {
      const haystack = normalize(`${product.name} ${product.description} ${product.category} ${product.collection}`);
      return (!filters.category || product.category === filters.category)
        && (!filters.collection || product.collection === filters.collection)
        && (!filters.size || product.sizes.includes(filters.size))
        && (!filters.color || product.colors.includes(filters.color))
        && (!filters.price || product.price <= Number(filters.price))
        && words.every((word) => haystack.includes(word));
    });
    if (filters.sort === 'menor-preco') return matches.sort((a,b) => a.price - b.price);
    if (filters.sort === 'maior-preco') return matches.sort((a,b) => b.price - a.price);
    if (filters.sort === 'nome') return matches.sort((a,b) => a.name.localeCompare(b.name, 'pt-BR'));
    return matches.sort((a,b) => a.sequence - b.sequence);
  }
  window.KYMA_DOMAIN = { money, normalize, key, sanitizeState, totals, shippingByState, filterProducts };
})();
