import fs from 'node:fs/promises';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '..');
const output = path.join(root, 'site');
await fs.mkdir(output, { recursive: true });
const entries = await fs.readdir(root);
for (const name of entries.filter((entry) => entry.endsWith('.html') || entry === '.nojekyll' || entry === 'robots.txt')) {
  await fs.copyFile(path.join(root,name), path.join(output,name));
}
await fs.cp(path.join(root,'assets'), path.join(output,'assets'), { recursive:true });
console.log('Static site packaged in site/. No server runtime or credentials required.');
