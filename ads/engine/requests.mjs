#!/usr/bin/env node
// Print every URL a page requests in its first seconds (scripts a tag manager injects included), one per line.
//   node ads/engine/requests.mjs https://example.com [ms]
import fs from 'node:fs';
import puppeteer from 'puppeteer';

const [url, ms = '8000'] = process.argv.slice(2);
const SANDBOX = process.getuid?.() === 0 ? ['--no-sandbox'] : [];
const exe = [process.env.PUPPETEER_EXECUTABLE_PATH, '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find((p) => p && fs.existsSync(p));
const browser = await puppeteer.launch({ headless: true, executablePath: exe, args: SANDBOX });
const page = await browser.newPage();
await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36');
const seen = new Set();
page.on('request', (r) => seen.add(r.url()));
try {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
  await new Promise((ok) => setTimeout(ok, Number(ms)));
  const globals = await page.evaluate(() => Object.keys(window).filter((k) => /qualified|drift|intercom/i.test(k)));
  globals.forEach((g) => seen.add(`global:${g}`));
} catch (e) {
  console.error(String(e.message || e));
}
console.log([...seen].join('\n'));
await browser.close();
