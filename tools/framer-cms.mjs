#!/usr/bin/env node
// Read and update the Framer CMS of getbreakout.ai through Framer's Server API.
//
//   node tools/framer-cms.mjs info
//   node tools/framer-cms.mjs collections
//   node tools/framer-cms.mjs fields <collection>
//   node tools/framer-cms.mjs items <collection> [--json]
//   node tools/framer-cms.mjs upsert <collection> <items.json> [--yes]
//   node tools/framer-cms.mjs remove <collection> <slug> [<slug> ...] [--yes]
//   node tools/framer-cms.mjs publish                # a preview deployment, not live
//   node tools/framer-cms.mjs deploy <deploymentId> --yes   # promote it to the live domains
//
// <collection> is a collection's name or id. The project and the key come from the
// environment, never from the repo:
//
//   FRAMER_PROJECT_URL   e.g. https://framer.com/projects/Website--aabbccdd1122
//   FRAMER_API_KEY       Framer > project settings > API Keys
//
// items.json is an array of items keyed by slug, with fields by their display name:
//
//   [{ "slug": "launch-film", "draft": true,
//      "fields": { "Title": "Meet Breakout", "Date": "2026-10-28", "Video": "https://..." } }]
//
// An item whose slug exists is updated (only the fields given change); any other is created.
// Enum fields take the case name, image and file fields take a URL, reference fields take
// item ids. Writes only print the plan until --yes is given. Edits land in the project;
// nothing reaches the live site until `publish` and then `deploy`.

import fs from 'node:fs/promises';
import { connect } from 'framer-api';

const argv = process.argv.slice(2);
const flags = new Set(argv.filter(a => a.startsWith('--')));
const [cmd, ...args] = argv.filter(a => !a.startsWith('--'));

function die(msg) {
  console.error(msg);
  process.exit(1);
}

const USAGE = 'usage: node tools/framer-cms.mjs info|collections|fields|items|upsert|remove|publish|deploy ... (see the header of this file)';
if (!cmd) die(USAGE);

const projectUrl = process.env.FRAMER_PROJECT_URL;
const apiKey = process.env.FRAMER_API_KEY;
if (!projectUrl || !apiKey) die('set FRAMER_PROJECT_URL and FRAMER_API_KEY in the environment (docs/setup.md, "Framer CMS")');

async function findCollection(framer, nameOrId) {
  if (!nameOrId) die('name a collection (see `collections`)');
  const all = await framer.getCollections();
  const hit = all.find(c => c.id === nameOrId) ?? all.find(c => c.name.toLowerCase() === nameOrId.toLowerCase());
  if (!hit) die(`no collection "${nameOrId}"; there are: ${all.map(c => c.name).join(', ')}`);
  return hit;
}

// Plain value from a stored field entry, for printing.
function plain(entry) {
  if (!entry) return null;
  const v = entry.value;
  if (v && typeof v === 'object' && 'url' in v) return v.url;
  return v;
}

// A value from items.json to the entry addItems expects for that field.
function toEntry(field, value) {
  const type = field.type;
  if (value === null) return { type, value: null };
  switch (type) {
    case 'enum': {
      const c = field.cases.find(c => c.name === value || c.id === value);
      if (!c) die(`"${field.name}": no case "${value}"; cases are ${field.cases.map(c => c.name).join(', ')}`);
      return { type, value: c.id };
    }
    case 'number': return { type, value: Number(value) };
    case 'boolean': return { type, value: Boolean(value) };
    case 'date': return { type, value: new Date(value).toISOString() };
    case 'string': case 'formattedText': case 'link': case 'color':
    case 'image': case 'file': case 'collectionReference': case 'multiCollectionReference':
      return { type, value };
    default:
      die(`"${field.name}" is a ${type} field, which this tool does not write; edit it in Framer`);
  }
}

const framer = await connect(projectUrl, apiKey);
try {
  if (cmd === 'info') {
    console.log(JSON.stringify(await framer.getProjectInfo(), null, 2));
  } else if (cmd === 'collections') {
    for (const c of await framer.getCollections()) {
      const n = (await c.getItems()).length;
      console.log(`${c.id}\t${c.name}\t${n} items${c.managedBy && c.managedBy !== 'user' ? `\tmanaged by ${c.managedBy}` : ''}`);
    }
  } else if (cmd === 'fields') {
    const c = await findCollection(framer, args[0]);
    for (const f of await c.getFields()) {
      const extra = f.type === 'enum' ? `\t[${f.cases.map(c => c.name).join(' | ')}]` : '';
      console.log(`${f.id}\t${f.type}\t${f.name ?? ''}${extra}`);
    }
  } else if (cmd === 'items') {
    const c = await findCollection(framer, args[0]);
    const fields = await c.getFields();
    const items = await c.getItems();
    const rows = items.map(it => ({
      id: it.id, slug: it.slug, draft: Boolean(it.draft),
      fields: Object.fromEntries(fields.filter(f => f.name).map(f => [f.name, plain(it.fieldData[f.id])])),
    }));
    if (flags.has('--json')) console.log(JSON.stringify(rows, null, 2));
    else for (const r of rows) console.log(`${r.slug}${r.draft ? ' (draft)' : ''}\t${r.id}`);
  } else if (cmd === 'upsert') {
    const c = await findCollection(framer, args[0]);
    if (!args[1]) die('give the items file: upsert <collection> <items.json>');
    const input = JSON.parse(await fs.readFile(args[1], 'utf8'));
    if (!Array.isArray(input)) die('items.json must be an array');
    const fields = await c.getFields();
    const byName = new Map(fields.filter(f => f.name).map(f => [f.name, f]));
    const existing = new Map((await c.getItems()).map(it => [it.slug, it]));
    const batch = input.map(row => {
      if (!row.slug) die('every item needs a slug');
      const fieldData = {};
      for (const [name, value] of Object.entries(row.fields ?? {})) {
        const f = byName.get(name);
        if (!f) die(`no field "${name}" in ${c.name}; fields are ${[...byName.keys()].join(', ')}`);
        fieldData[f.id] = toEntry(f, value);
      }
      const old = existing.get(row.slug);
      const item = { slug: row.slug, fieldData };
      if (row.draft !== undefined) item.draft = Boolean(row.draft);
      if (old) item.id = old.id;
      console.log(`${old ? 'update' : 'create'}\t${row.slug}\t${Object.keys(row.fields ?? {}).join(', ')}`);
      return item;
    });
    if (!flags.has('--yes')) console.log(`\n${batch.length} items planned; nothing written. Re-run with --yes to write.`);
    else { await c.addItems(batch); console.log(`\nwrote ${batch.length} items to ${c.name} (not live until publish + deploy)`); }
  } else if (cmd === 'remove') {
    const c = await findCollection(framer, args[0]);
    const slugs = args.slice(1);
    if (!slugs.length) die('name the slugs to remove');
    const items = await c.getItems();
    const ids = slugs.map(s => items.find(it => it.slug === s)?.id ?? die(`no item "${s}" in ${c.name}`));
    slugs.forEach(s => console.log(`remove\t${s}`));
    if (!flags.has('--yes')) console.log(`\n${ids.length} items planned; nothing removed. Re-run with --yes to remove.`);
    else { await c.removeItems(ids); console.log(`\nremoved ${ids.length} items from ${c.name}`); }
  } else if (cmd === 'publish') {
    const { deployment, hostnames } = await framer.publish();
    console.log(`deployment ${deployment.id}`);
    for (const h of hostnames) console.log(`  ${h.hostname} (${h.type})`);
    console.log(`\npreview only. To go live: node tools/framer-cms.mjs deploy ${deployment.id} --yes`);
  } else if (cmd === 'deploy') {
    if (!args[0]) die('give the deployment id from `publish`');
    if (!flags.has('--yes')) die(`this puts deployment ${args[0]} on the live site; re-run with --yes`);
    for (const h of await framer.deploy(args[0])) console.log(`live: ${h.hostname}`);
  } else {
    die(USAGE);
  }
} finally {
  await framer.disconnect();
}
