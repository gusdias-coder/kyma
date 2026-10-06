import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root = path.resolve(import.meta.dirname, '..');
const pages = (await fs.readdir(root)).filter((name) => name.endsWith('.html'));
let assets = 0;
for (const name of pages) {
  const html = await fs.readFile(path.join(root,name),'utf8');
  assert.match(html, /<html lang="pt-BR">/);
  assert.match(html, /<meta name="viewport"/);
  assert.match(html, /id="main"/);
  for (const [,reference] of html.matchAll(/(?:src|href)="([^"#]+)"/g)) {
    if (/^(https?:|data:|mailto:)/.test(reference)) continue;
    assert.ok(!reference.startsWith('/'), `${name}: root-relative URL breaks project Pages: ${reference}`);
    const relative = reference.split(/[?#]/)[0];
    await fs.access(path.resolve(root,relative)); assets += 1;
  }
}
const css = await fs.readFile(path.join(root,'assets/css/styles.css'),'utf8');
for (const [,reference] of css.matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)) await fs.access(path.resolve(root,'assets/css',reference));
for (const name of ['data','domain','app']) new vm.Script(await fs.readFile(path.join(root,`assets/js/${name}.js`),'utf8'), {filename:`${name}.js`});
for (const name of ['inter-latin.woff2','oswald-latin.woff2']) {
  const bytes = await fs.readFile(path.join(root,'assets/fonts',name));
  assert.equal(bytes.subarray(0,4).toString(),'wOF2', `${name} must be a real WOFF2`);
}
const poster = await fs.stat(path.join(root,'assets/images/hero.webp'));
assert.ok(poster.size <= 150*1024, `Poster exceeds 150 KB (${poster.size})`);
const source = await fs.readFile(path.join(root,'assets/js/app.js'),'utf8');
assert.ok(!/fetch\(|https:\/\//.test(source), 'Preview app must not contact payment or personal-data endpoints.');
assert.equal(pages.length,13);
console.log(`PASS: ${pages.length} pages, ${assets} references, script syntax, real fonts, poster budget and offline preview boundary.`);
