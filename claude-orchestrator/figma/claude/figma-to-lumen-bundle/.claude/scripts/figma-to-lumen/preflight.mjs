#!/usr/bin/env node
/**
 * preflight.mjs
 * Checks the repo and framework are ready BEFORE the pipeline spends MCP calls.
 * It cannot test the MCP servers (those are only reachable from inside Claude Code);
 * the skill performs the MCP reachability check itself in Phase 0.
 *
 * CLI: node preflight.mjs [--repo .] [--config .claude/rules/lumen-compliance.config.json]
 * Exit: 0 ready (warnings allowed), 1 blocking problems
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export function preflight({ repo = '.', configPath }) {
  const blockers = [], warnings = [], info = {};
  const p = (...s) => path.join(repo, ...s);
  const readJson = (f) => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return null; } };

  const nodeMajor = Number(process.versions.node.split('.')[0]);
  info.node = process.versions.node;
  if (nodeMajor < 18) blockers.push(`Node ${process.versions.node} < 18`);

  const pkg = readJson(p('package.json'));
  if (!pkg) blockers.push('package.json not found/readable in repo root');
  const deps = { ...(pkg?.dependencies ?? {}), ...(pkg?.devDependencies ?? {}) };

  if (pkg) {
    if (!deps.next) blockers.push('"next" not found in package.json: expected an existing Next.js app');
    else info.next = deps.next;
    if (!deps.react) blockers.push('"react" not found in package.json');
    if (!deps.typescript) warnings.push('typescript not in package.json: pipeline assumes .tsx output');
    info.router = fs.existsSync(p('src', 'app')) || fs.existsSync(p('app')) ? 'app' : (fs.existsSync(p('src', 'pages')) || fs.existsSync(p('pages')) ? 'pages' : 'unknown');
    info.packageManager = fs.existsSync(p('pnpm-lock.yaml')) ? 'pnpm' : fs.existsSync(p('yarn.lock')) ? 'yarn' : fs.existsSync(p('package-lock.json')) ? 'npm' : 'unknown';

    const sb = deps.storybook ?? deps['@storybook/nextjs'] ?? deps['@storybook/react'];
    info.storybook = sb ?? null;
    if (!sb) warnings.push('Storybook not installed: Phase 0 must decide how to add it (v8 devDependencies only) and report it');
    else if (!/\b8\b|\^8|~8|8\./.test(sb)) warnings.push(`Storybook version "${sb}" is not v8 (config says v8): align or flag`);
    info.storybookConfigDir = fs.existsSync(p('.storybook'));
    if (sb && !info.storybookConfigDir) warnings.push('Storybook dependency present but .storybook/ is missing');
  }

  const cfg = configPath ? readJson(configPath) : null;
  if (configPath && !cfg) blockers.push(`compliance config unreadable: ${configPath}`);
  if (cfg) {
    const prefixes = cfg.lumenImportPrefixes ?? [];
    if (!prefixes.length) blockers.push('config.lumenImportPrefixes is empty: run Phase 0 MCP discovery to fill it in');
    for (const pref of prefixes) {
      const pkgName = pref.startsWith('@') ? pref.split('/').slice(0, 2).join('/') : pref.split('/')[0];
      const installed = fs.existsSync(p('node_modules', ...pkgName.split('/')));
      info[`installed:${pkgName}`] = installed;
      if (!installed) blockers.push(`Lumen package "${pkgName}" is not installed in node_modules (run the package manager install; may require the internal registry)`);
    }
  }

  for (const f of ['.claude/skills/figma-to-react-lumen/SKILL.md', '.claude/workflows/figma-to-lumen.md', '.claude/rules/lumen-compliance.config.json']) {
    if (!fs.existsSync(p(f))) warnings.push(`framework file missing: ${f}`);
  }

  return { ok: blockers.length === 0, blockers, warnings, info };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const a = process.argv.slice(2); let repo = '.', configPath;
  for (let i = 0; i < a.length; i++) { if (a[i] === '--repo') repo = a[++i]; else if (a[i] === '--config') configPath = a[++i]; }
  const r = preflight({ repo, configPath });
  console.log(JSON.stringify(r, null, 2));
  process.exit(r.ok ? 0 : 1);
}
