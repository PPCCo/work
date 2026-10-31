#!/usr/bin/env node
/**
 * hook-validate-on-write.mjs
 * Claude Code PostToolUse hook: validate generated React/story files right after they are written.
 *
 * Contract assumed (VERIFY against your installed Claude Code version; Phase 0 must confirm):
 *   - the hook receives a JSON event on stdin containing tool_name and tool_input.file_path
 *   - exit code 2 feeds stderr back to Claude as a blocking error; exit 0 is silent success
 *
 * Scope: only files that carry the "@generated-by figma-to-react-lumen" header, so it never
 * fires on hand-written code. New files that lack the header are caught by the pipeline's
 * full validation run in Phase 4 rather than here.
 *
 * Config discovery: <repo>/.claude/rules/lumen-compliance.config.json
 * Evidence discovery: newest <repo>/design-sync/*\/lumen-resolution.json
 */
import fs from 'node:fs';
import path from 'node:path';
import { validateFile } from './validate-lumen-compliance.mjs';

const chunks = [];
for await (const c of process.stdin) chunks.push(c);
let event = {};
try { event = JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}'); } catch { process.exit(0); }

const file = event?.tool_input?.file_path;
if (!file || !/\.(tsx|jsx)$/.test(file) || !fs.existsSync(file)) process.exit(0);
if (!/@generated-by\s+figma-to-react-lumen/.test(fs.readFileSync(file, 'utf8'))) process.exit(0);

const repo = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const cfgPath = path.join(repo, '.claude/rules/lumen-compliance.config.json');
const syncDir = path.join(repo, 'design-sync');
let evidencePath = null;
if (fs.existsSync(syncDir)) {
  const cands = fs.readdirSync(syncDir)
    .map((d) => path.join(syncDir, d, 'lumen-resolution.json'))
    .filter((f) => fs.existsSync(f))
    .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  evidencePath = cands[0] ?? null;
}
if (!fs.existsSync(cfgPath) || !evidencePath) {
  console.error('[figma-to-lumen hook] compliance config or lumen-resolution.json not found; skipping per-file validation (Phase 4 still runs it)');
  process.exit(0);
}

const r = validateFile(file, { config: JSON.parse(fs.readFileSync(cfgPath, 'utf8')), evidence: JSON.parse(fs.readFileSync(evidencePath, 'utf8')) });
if (r.violations.length) {
  console.error(`Lumen compliance violations in ${path.relative(repo, file)}:`);
  for (const v of r.violations) console.error(`  [${v.rule}] line ${v.line}: ${v.message}`);
  console.error('Fix these using MCP-verified Lumen components/props/tokens. Do not add waivers without a reason.');
  process.exit(2);
}
process.exit(0);
