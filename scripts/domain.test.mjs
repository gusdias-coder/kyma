import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const root = path.resolve(import.meta.dirname,'..');
const context = vm.createContext({ window:{}, Intl });
for (const name of ['data','domain']) vm.runInContext(fs.readFileSync(path.join(root,`assets/js/${name}.js`),'utf8'),context);
const { products,categories,collections } = context.window.KYMA_DATA;
const rules = context.window.KYMA_DOMAIN;
const product = products[0];
const variation = { id:product.id, size:product.sizes[0], color:product.colors[0], qty:2 };
test('The concept covers 32 unique products, eight categories and eight collections', () => {
  assert.equal(products.length,32); assert.equal(new Set(products.map((item)=>item.id)).size,32);
  assert.equal(categories.length,8); assert.equal(collections.length,8);
  assert.ok(products.every((item)=>Number.isInteger(item.price)&&item.price>0&&item.demo));
  assert.ok(categories.every((category)=>products.filter((item)=>item.category===category.id).length===4));
  assert.ok(collections.every((collection)=>products.some((item)=>item.collection===collection.id)));
});
test('Corrupt local data cannot create unknown products, invalid variants or negative quantities', () => {
  const sanitized = rules.sanitizeState({ cart:[variation,{...variation,id:'missing'}, {...variation,size:'invalid'},{...variation,qty:-1},{...variation,qty:1.5}, {...variation,color:'invalid'}],favorites:[product.id,product.id,'missing'],coupon:'BAD' },products);
  assert.equal(sanitized.cart.length,1); assert.equal(sanitized.favorites.length,1); assert.equal(sanitized.coupon,'');
});
test('Repeated variants merge, enforce the preview limit and ignore stored prices', () => {
  const sanitized = rules.sanitizeState({cart:[{...variation,qty:9,price:1}, {...variation,qty:9}]},products);
  assert.equal(sanitized.cart.length,1); assert.equal(sanitized.cart[0].qty,10);
  assert.equal(rules.totals(sanitized,products).subtotal,product.price*10);
});
test('Discount and shipping are added in integer cents', () => {
  const result = rules.totals({cart:[variation],coupon:'KYMA10'},products,1990);
  assert.equal(result.total,product.price*2-Math.floor(product.price*2/10)+1990);
  assert.ok(Number.isInteger(result.total));
  assert.equal(rules.totals({cart:[],coupon:''},products).total,0);
});
test('Search tolerates accents and intersects category, size and price filters', () => {
  const matches = rules.filterProducts(products,{q:'calca',category:'calcas',size:'40',price:'30000',sort:'menor-preco'});
  assert.ok(matches.length>0); assert.ok(matches.every((item)=>item.category==='calcas'&&item.sizes.includes('40')&&item.price<=30000));
  assert.ok(matches.every((item,index)=>index===0||matches[index-1].price<=item.price));
  assert.equal(rules.filterProducts(products,{q:'<script>'}).length,0);
});
test('Illustrative shipping accepts all Brazilian UFs and rejects unknown regions', () => {
  for (const uf of ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']) assert.ok(rules.shippingByState(uf)?.price>0);
  assert.equal(rules.shippingByState('XX'),null);
});
