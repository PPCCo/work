#!/usr/bin/env node
/**
 * verify-manifest.mjs
 * Proves the pipeline covered everything the designer produced.
 *
 * Reads <dir>/source-snapshot.json and <dir>/manifest.json (contracts in
 * .claude/patterns/figma-to-lumen-artifacts.md) and checks:
 *   1. every snapshot item with expected=true is mapped by an entry or listed as a gap with a reason
 *   2. every entry's generated files exist under <repo>
 *   3. every component/layout/screen entry has a story file with a default export and >=1 named story
 *   4. named-story count >= number of Figma variants/states recorded on the entry
 *   5. screen stories use a "Screens/" title; layout stories "Layouts/"
 *   6. status values are valid; skipped/gap items carry reasons
 *
 * CLI: node verify-manifest.mjs --dir design-sync/<fileKey> [--repo .]
 * Exit: 0 pass, 1 fail, 2 usage error
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const STATUSES = new Set(['generated', 'reused', 'skipped']);
const KINDS = new Set(['component', 'layout', 'screen']);

export function verifyManifest({ snapshot, manifest, repo }) {
  const errors = [];
  const err = (m) => errors.push(m);

  const entries = manifest.entries ?? [];
  const gaps = manifest.gaps ?? [];
  const covered = new Map(); // figma node id -> where

  entries.forEach((e, i) => {
    const tag = `entry[${i}] ${e.name ?? '<unnamed>'}`;
    if (!e.name) err(`${tag}: missing name`);
    if (!KINDS.has(e.kind)) err(`${tag}: invalid kind "${e.kind}"`);
    if (!STATUSES.has(e.status)) err(`${tag}: invalid status "${e.status}"`);
    if (!Array.isArray(e.figmaNodeIds) || !e.figmaNodeIds.length) err(`${tag}: figmaNodeIds is empty`);
    for (const id of e.figmaNodeIds ?? []) covered.set(id, tag);
    if (e.status === 'skipped' && !e.reason) err(`${tag}: skipped without reason`);

    if (e.status === 'generated') {
      for (const key of ['component', 'story']) {
        const rel = e.files?.[key];
        if (!rel) { err(`${tag}: files.${key} missing`); continue; }
        if (!fs.existsSync(path.join(repo, rel))) err(`${tag}: file not found: ${rel}`);
      }
      const storyRel = e.files?.story;
      const storyPath = storyRel && path.join(repo, storyRel);
      if (storyPath && fs.existsSync(storyPath)) {
        const s = fs.readFileSync(storyPath, 'utf8');
        if (!/export\s+default\b/.test(s)) err(`${tag}: story has no default export`);
        const named = (s.match(/^export\s+const\s+\w+/gm) ?? []).length;
        if (named < 1) err(`${tag}: story has no named stories`);
        const need = (e.variants ?? []).length;
        if (need && named < need) err(`${tag}: ${named} named stories but ${need} Figma variants/states recorded`);
        const title = s.match(/title\s*:\s*['"`]([^'"`]+)['"`]/)?.[1];
        if (e.kind === 'screen' && title && !title.startsWith('Screens/')) err(`${tag}: screen story title "${title}" must start with "Screens/"`);
        if (e.kind === 'layout' && title && !title.startsWith('Layouts/')) err(`${tag}: layout story title "${title}" must start with "Layouts/"`);
        if (e.kind === 'screen' && e.viewport == null) err(`${tag}: screen entry has no viewport (designer frame size)`);
      }
    }
    if (e.status === 'reused' && !e.reusedFrom) err(`${tag}: reused without reusedFrom`);
  });

  gaps.forEach((g, i) => {
    if (!g.figmaNodeId) err(`gap[${i}]: missing figmaNodeId`);
    if (!g.reason) err(`gap[${i}]: missing reason`);
    if (g.figmaNodeId) covered.set(g.figmaNodeId, `gap[${i}]`);
  });

  for (const item of snapshot.inventory ?? []) {
    if (item.expected === false || item.classification === 'ignored') {
      if (item.classification === 'ignored' && !item.ignoreReason) err(`inventory ${item.id} (${item.name}): ignored without ignoreReason`);
      continue;
    }
    if (!item.classification) err(`inventory ${item.id} (${item.name}): no classification`);
    else if (!covered.has(item.id)) err(`inventory ${item.id} (${item.name}): not covered by any entry or gap`);
  }

  return { ok: errors.length === 0, errors, stats: {
    inventory: (snapshot.inventory ?? []).length, entries: entries.length, gaps: gaps.length,
    generated: entries.filter((e) => e.status === 'generated').length,
    reused: entries.filter((e) => e.status === 'reused').length } };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const a = process.argv.slice(2); let dir, repo = '.';
  for (let i = 0; i < a.length; i++) { if (a[i] === '--dir') dir = a[++i]; else if (a[i] === '--repo') repo = a[++i]; }
  if (!dir) { console.error('usage: verify-manifest.mjs --dir design-sync/<fileKey> [--repo .]'); process.exit(2); }
  let snapshot, manifest;
  try {
    snapshot = JSON.parse(fs.readFileSync(path.join(dir, 'source-snapshot.json'), 'utf8'));
    manifest = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
  } catch (e) { console.error(`cannot read artifacts: ${e.message}`); process.exit(2); }
  const r = verifyManifest({ snapshot, manifest, repo });
  console.log(r.ok ? 'PASS manifest' : 'FAIL manifest');
  r.errors.forEach((e) => console.log(`   ✗ ${e}`));
  console.log(JSON.stringify(r.stats));
  process.exit(r.ok ? 0 : 1);
}
