import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '..');
const port = Number(process.env.PORT || 4321);
const types = { '.html':'text/html; charset=utf-8', '.txt':'text/plain; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'application/javascript; charset=utf-8', '.jpg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml', '.woff2':'font/woff2', '.mp4':'video/mp4', '.webm':'video/webm', '.json':'application/json; charset=utf-8' };
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, `http://localhost:${port}`);
    let requested = decodeURIComponent(url.pathname);
    if (requested.startsWith('/kyma-test/')) requested = requested.slice('/kyma-test'.length);
    const filename = path.resolve(root, `.${requested.endsWith('/') ? requested + 'index.html' : requested}`);
    if (!filename.startsWith(root + path.sep)) { response.writeHead(403).end(); return; }
    const stat = await fs.stat(filename);
    if (!stat.isFile()) { response.writeHead(404).end(); return; }
    response.writeHead(200, { 'Content-Type':types[path.extname(filename)] || 'application/octet-stream', 'Cache-Control':'no-store' });
    response.end(await fs.readFile(filename));
  } catch { response.writeHead(404, { 'Content-Type':'text/plain; charset=utf-8' }).end('Not found'); }
});
server.listen(port,'127.0.0.1', () => console.log(`KYMA preview: http://127.0.0.1:${port}/ — project-path test: http://127.0.0.1:${port}/kyma-test/`));
