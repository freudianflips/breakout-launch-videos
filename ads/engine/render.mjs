#!/usr/bin/env node
// Render ad creatives with headless Chrome. Called by ads.py; you rarely run it by hand.
//
//   node ads/engine/render.mjs jobs.json
//
// jobs.json is a list of:
//   { "out": "x.png", "template": "verdict", "size": [1200, 1200], "fields": {...} }   one image
//   { "out": "x.pdf", "size": [1080, 1080], "pages": [{ "template": ..., "fields": ... }] }   a document ad
//   { "out": "x.png", "url": "file:///.../sheet.html", "size": [1600, 900], "full_page": true }   any page
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const AD_HTML = pathToFileURL(path.join(ROOT, 'ads', 'designs', 'ad.html')).href;
const BRAND = JSON.parse(fs.readFileSync(path.join(ROOT, 'brand', 'brand.json'), 'utf8'));
const SANDBOX = process.getuid?.() === 0 ? ['--no-sandbox'] : [];

// Use the bundled Chrome when it was downloaded, else a system or preinstalled one.
function chrome() {
  const candidates = [process.env.PUPPETEER_EXECUTABLE_PATH, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'];
  for (const c of candidates) if (c && fs.existsSync(c)) return c;
  return undefined;
}

async function drawAd(page, job) {
  await page.setViewport({ width: job.size[0], height: job.size[1], deviceScaleFactor: 1 });
  await page.evaluateOnNewDocument((ad, brand) => { window.AD = ad; window.BRAND = brand; },
    { template: job.template, size: job.size, fields: job.fields || {} }, BRAND);
  await page.goto(AD_HTML, { waitUntil: 'load' });
  await page.waitForFunction('window.READY === true', { timeout: 20000 });
  const failed = await page.evaluate('window.FAILED || null');
  if (failed) throw new Error(failed);
}

async function main() {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await puppeteer.launch({ headless: true, executablePath: chrome(), args: ['--allow-file-access-from-files', '--font-render-hinting=none', ...SANDBOX] });
  let bad = 0;
  for (const job of jobs) {
    const page = await browser.newPage();
    try {
      fs.mkdirSync(path.dirname(job.out), { recursive: true });
      if (job.url) {
        await page.setViewport({ width: job.size[0], height: job.size[1], deviceScaleFactor: job.scale || 1 });
        await page.goto(job.url, { waitUntil: 'networkidle0' });
        await page.evaluate('document.fonts.ready');
        await page.screenshot({ path: job.out, fullPage: !!job.full_page });
      } else if (job.pages) {
        const pngs = [];
        for (const [i, p] of job.pages.entries()) {
          const pg = await browser.newPage();
          await drawAd(pg, { ...p, size: job.size });
          const png = job.out.replace(/\.pdf$/, `-p${i + 1}.png`);
          await pg.screenshot({ path: png });
          pngs.push(png);
          await pg.close();
        }
        const [w, h] = job.size;
        const html = job.out.replace(/\.pdf$/, '-pages.html');
        fs.writeFileSync(html, `<!doctype html><style>@page{size:${w}px ${h}px;margin:0}body{margin:0}img{display:block;width:${w}px;height:${h}px;page-break-after:always}</style>`
          + pngs.map((p) => `<img src="${pathToFileURL(p).href}">`).join(''));
        await page.goto(pathToFileURL(html).href, { waitUntil: 'load' });
        await page.pdf({ path: job.out, width: `${w}px`, height: `${h}px`, printBackground: true });
        fs.rmSync(html);
      } else {
        await drawAd(page, job);
        await page.screenshot({ path: job.out, type: job.out.endsWith('.jpg') ? 'jpeg' : 'png', ...(job.out.endsWith('.jpg') ? { quality: 92 } : {}) });
      }
      console.log(`ok   ${path.relative(ROOT, job.out)}`);
    } catch (e) {
      bad++;
      console.log(`FAIL ${path.relative(ROOT, job.out)}: ${e.message}`);
    }
    await page.close();
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
}

main();
