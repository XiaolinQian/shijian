import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'verification');
await mkdir(out, { recursive: true });
const { chromium } = await import(
  process.env.PLAYWRIGHT_MODULE ||
    '/Users/qianxiaolin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs'
);
const failures = [];
const summary = { viewports: [], downloads: [], filePreview: false };
const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.zip': 'application/zip',
  '.dmg': 'application/x-apple-diskimage',
  '.txt': 'text/plain; charset=utf-8',
};
const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  const relative = decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname);
  const file = path.resolve(root, '.' + relative);
  if (!file.startsWith(root + path.sep)) {
    res.writeHead(403);
    res.end();
    return;
  }
  try {
    const data = await readFile(file);
    res.writeHead(200, {
      'Content-Type': types[path.extname(file)] || 'application/octet-stream',
      'Content-Length': data.length,
    });
    res.end(data);
  } catch {
    res.writeHead(404);
    res.end('Not found');
  }
});
await new Promise((resolve, reject) => {
  server.once('error', reject);
  server.listen(0, '127.0.0.1', resolve);
});
const base = `http://127.0.0.1:${server.address().port}`;
let browser;
try {
  browser = await chromium.launch({
    executablePath:
      process.env.PROMO_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    reducedMotion: 'reduce',
    acceptDownloads: true,
  });
  page.on('pageerror', (error) => failures.push(error.message));
  page.on('response', (r) => {
    if (r.status() >= 400) failures.push(`${r.status()} ${r.url()}`);
  });
  page.on('requestfailed', (r) => failures.push(`${r.failure()?.errorText} ${r.url()}`));
  await page.goto(base, { waitUntil: 'networkidle' });
  assert.equal(await page.title(), '时笺 · SHIJIAN｜今天，也要从容有序。');
  // Pin download checks to the verified build manifest, including the old link alias.
  const release = JSON.parse(await readFile(path.join(root, 'downloads/release.json'), 'utf8'));
  assert.equal(release.productName, '时笺');
  const expectedChecksum = release.sha256;
  for (const filename of [release.file, release.compatibilityFile]) {
    const response = await page.request.get(`${base}/downloads/${filename}`);
    assert.equal(response.status(), 200);
    const bytes = await response.body();
    assert.equal(bytes.length, release.bytes);
    assert.equal(createHash('sha256').update(bytes).digest('hex'), expectedChecksum);
  }
  const checksumFile = await readFile(path.join(root, 'downloads/SHA256SUMS.txt'), 'utf8');
  assert.ok(checksumFile.includes(`${expectedChecksum}  ${release.file}`));
  assert.ok(checksumFile.includes(`${expectedChecksum}  ${release.compatibilityFile}`));
  summary.release = {
    file: release.file,
    compatibilityFile: release.compatibilityFile,
    sha256: expectedChecksum,
  };

  const urls = await page
    .locator('a[href],img[src],link[href]')
    .evaluateAll((els) => [
      ...new Set(els.map((el) => el.getAttribute('href') || el.getAttribute('src'))),
    ]);
  for (const url of urls) {
    if (url.startsWith('#'))
      assert.equal(await page.locator(url).count(), 1, `Missing anchor ${url}`);
    else {
      const res = await page.request.get(new URL(url, base).href);
      assert.equal(res.status(), 200, `Broken URL: ${url}`);
    }
  }
  for (const width of [1440, 1024, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.evaluate(async () => {
      for (const img of document.images) {
        img.loading = 'eager';
        await img.decode();
      }
    });
    const check = await page.evaluate(() => ({
      width: innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      broken: [...document.images].filter((i) => !i.complete || !i.naturalWidth).map((i) => i.src),
    }));
    if (check.scrollWidth > width + 1) {
      console.log(
        await page.evaluate(() =>
          [...document.querySelectorAll('body *')]
            .map((e) => ({
              tag: e.tagName,
              cls: e.className,
              text: e.textContent.trim().slice(0, 25),
              left: e.getBoundingClientRect().left,
              right: e.getBoundingClientRect().right,
              width: e.getBoundingClientRect().width,
            }))
            .filter((r) => r.right > innerWidth || r.left < 0),
        ),
      );
      await page.screenshot({
        path: path.join(out, `overflow-${width}.jpg`),
        fullPage: true,
        type: 'jpeg',
      });
    }
    assert.ok(check.scrollWidth <= width + 1, `Horizontal overflow ${JSON.stringify(check)}`);
    assert.deepEqual(check.broken, []);
    summary.viewports.push(check);
    if ([1440, 390].includes(width)) {
      await page.screenshot({
        path: path.join(out, width === 1440 ? 'website-desktop.jpg' : 'website-mobile.jpg'),
        fullPage: true,
        type: 'jpeg',
        quality: 85,
      });
      await page.screenshot({
        path: path.join(
          out,
          width === 1440 ? 'website-desktop-first.jpg' : 'website-mobile-first.jpg',
        ),
        type: 'jpeg',
        quality: 90,
      });
    }
  }
  await page.setViewportSize({ width: 1440, height: 1000 });
  const question = page.getByText('自动报告使用 AI 吗？', { exact: true });
  await question.click();
  assert.equal(await question.evaluate((el) => el.parentElement.open), true);
  await page.keyboard.press('Enter');
  assert.equal(await question.evaluate((el) => el.parentElement.open), false);
  assert.equal(await page.getByRole('button', { name: 'Windows 版尚未发布' }).isDisabled(), true);
  for (const href of [
    'downloads/Shijian_0.1.0_x64.dmg',
    'downloads/TodoApp-press-kit.zip',
    'press/01-cover.png',
  ]) {
    const pending = page.waitForEvent('download');
    await page.locator(`a[href="${href}"]`).click();
    const download = await pending;
    assert.equal(await download.failure(), null);
    const data = await readFile(await download.path());
    const original = await readFile(path.join(root, href));
    const sha = (buffer) => createHash('sha256').update(buffer).digest('hex');
    assert.equal(sha(data), sha(original));
    summary.downloads.push({
      name: download.suggestedFilename(),
      bytes: data.length,
      sha256: sha(data),
    });
    await download.delete();
  }
  await page.goto(pathToFileURL(path.join(root, 'index.html')).href, { waitUntil: 'load' });
  await page.evaluate(async () => {
    for (const img of document.images) {
      img.loading = 'eager';
      await img.decode();
    }
  });
  assert.equal(await page.locator('h1').count(), 1);
  summary.filePreview = true;
  const reduced = await page.evaluate(
    () => getComputedStyle(document.documentElement).scrollBehavior,
  );
  assert.equal(reduced, 'auto');
  assert.deepEqual(failures, []);
  summary.status = 'passed';
  await writeFile(path.join(out, 'checks.json'), JSON.stringify(summary, null, 2) + '\n');
  console.log(JSON.stringify(summary, null, 2));
} finally {
  await browser?.close();
  await new Promise((resolve) => server.close(resolve));
}
