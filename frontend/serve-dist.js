/**
 * Lightweight static server for the Expo web export (./dist).
 * - Serves precompressed .gz when the client accepts gzip
 * - Adds `Cache-Control: public, max-age=31536000, immutable` to hashed assets
 * - Adds `Cache-Control: no-cache` to HTML
 * - SPA fallback to index.html for client-side routing
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const ROOT = path.join(__dirname, 'dist');
const PORT = parseInt(process.env.PORT || '3000', 10);
const HOST = process.env.HOST || '0.0.0.0';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.mjs':  'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map':  'application/json; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif':  'image/gif',
  '.ico':  'image/x-icon',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
  '.otf':  'font/otf',
  '.txt':  'text/plain; charset=utf-8',
  '.wasm': 'application/wasm',
};

// MIME types that benefit from gzip
const COMPRESSIBLE = new Set([
  '.html', '.js', '.mjs', '.css', '.json', '.map', '.svg', '.txt', '.wasm'
]);

// ── One-time precompression of all compressible assets at startup ──
// Removes per-request gzip CPU cost; serve-dist just streams the .gz file.
function precompress(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { precompress(p); continue; }
    const ext = path.extname(e.name).toLowerCase();
    if (!COMPRESSIBLE.has(ext)) continue;
    if (e.name.endsWith('.gz')) continue;
    const gzPath = p + '.gz';
    try {
      // Skip if gz is fresh
      const src = fs.statSync(p);
      const gz = fs.existsSync(gzPath) ? fs.statSync(gzPath) : null;
      if (gz && gz.mtimeMs >= src.mtimeMs) continue;
      const buf = fs.readFileSync(p);
      const compressed = zlib.gzipSync(buf, { level: 9 });
      // Only keep the .gz if it's actually smaller
      if (compressed.length < buf.length * 0.95) {
        fs.writeFileSync(gzPath, compressed);
      }
    } catch {}
  }
}

if (fs.existsSync(ROOT)) {
  console.log('[serve-dist] precompressing static assets...');
  const t0 = Date.now();
  precompress(ROOT);
  console.log(`[serve-dist] precompression done in ${Date.now() - t0}ms`);
}

function safeJoin(root, urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0].split('#')[0]);
  const p = path.normalize(path.join(root, decoded));
  if (!p.startsWith(root)) return null;
  return p;
}

function send(res, status, body, headers = {}) {
  res.writeHead(status, {
    'Access-Control-Allow-Origin': '*',
    'Cache-Control': 'no-cache',
    ...headers,
  });
  res.end(body);
}

// Hashed asset paths get year-long immutable caching
const HASHED_RE = /-[a-f0-9]{16,}\.(js|css|map|woff2?|ttf|otf)$/i;
const isHashed = (p) => HASHED_RE.test(p);

function streamFile(res, file, acceptsGzip) {
  const ext = path.extname(file).toLowerCase();
  const type = MIME[ext] || 'application/octet-stream';

  // Prefer precompressed .gz if available + accepted
  const gzPath = file + '.gz';
  const useGz = acceptsGzip && COMPRESSIBLE.has(ext) && fs.existsSync(gzPath);
  const actualFile = useGz ? gzPath : file;

  fs.stat(actualFile, (err, st) => {
    if (err || !st.isFile()) return fallback(res);

    const cacheControl = ext === '.html'
      ? 'no-cache'
      : isHashed(file)
        ? 'public, max-age=31536000, immutable'
        : 'public, max-age=3600';

    const headers = {
      'Content-Type': type,
      'Content-Length': st.size,
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': cacheControl,
      'Vary': 'Accept-Encoding',
    };
    if (useGz) headers['Content-Encoding'] = 'gzip';

    res.writeHead(200, headers);
    fs.createReadStream(actualFile).pipe(res);
  });
}

function fallback(res) {
  const idx = path.join(ROOT, 'index.html');
  fs.readFile(idx, (err, buf) => {
    if (err) return send(res, 500, 'index.html missing');
    send(res, 200, buf, { 'Content-Type': MIME['.html'] });
  });
}

const server = http.createServer((req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return send(res, 405, 'method not allowed');
  }
  const acceptsGzip = /\bgzip\b/.test(req.headers['accept-encoding'] || '');

  let urlPath = req.url || '/';
  if (urlPath === '/' || urlPath === '') return streamFile(res, path.join(ROOT, 'index.html'), acceptsGzip);

  const file = safeJoin(ROOT, urlPath);
  if (!file) return send(res, 400, 'bad path');

  fs.stat(file, (err, st) => {
    if (!err && st.isFile()) return streamFile(res, file, acceptsGzip);
    // Try with .html appended (Expo router static)
    const withHtml = file + '.html';
    fs.stat(withHtml, (e2, s2) => {
      if (!e2 && s2.isFile()) return streamFile(res, withHtml, acceptsGzip);
      // SPA fallback
      return fallback(res);
    });
  });
});

server.listen(PORT, HOST, () => {
  console.log(`[serve-dist] serving ${ROOT} on http://${HOST}:${PORT}`);
});
