// Screenshot every moodboard frame in frames.html to m<nn>.jpg.
//   node docs/moodboard/shoot.mjs
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = ['--allow-file-access-from-files', ...(process.getuid?.() === 0 ? ['--no-sandbox'] : [])];
const browser = await puppeteer.launch({ headless: true, args });
const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080 });
await page.goto(pathToFileURL(path.join(here, 'frames.html')).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.waitForFunction(() => !document.getElementById('sw') || document.body.dataset.swarm === 'ready');
const ids = await page.$$eval('.frame', (els) => els.map((e) => e.id));
for (const id of ids) {
  await (await page.$('#' + id)).screenshot({ path: path.join(here, `${id}.jpg`), type: 'jpeg', quality: 88 });
  console.log(`${id}.jpg`);
}
await browser.close();
