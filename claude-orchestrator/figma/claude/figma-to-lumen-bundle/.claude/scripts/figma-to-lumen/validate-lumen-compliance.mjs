#!/usr/bin/env node
/**
 * validate-lumen-compliance.mjs
 * Deterministic compliance gate for generated React/Storybook files.
 * Dependency-free (regex + a small scanner), so it runs in any repo without installs.
 *
 * What it enforces (configurable via lumen-compliance.config.json):
 *   - imports only from allowed prefixes (Lumen, React, Next, Storybook, relative/alias)
 *   - every Lumen import and every JSX prop on a Lumen component appears in the
 *     MCP-derived evidence file (lumen-resolution.json)   [always_verify_lumen_props]
 *   - Lumen import path equals the verified path in the evidence file
 *   - no inline style, hex/rgb/hsl colours, raw px values, `any`, raw interactive elements
 *
 * Limits: this is a lexical checker, not a TypeScript compiler. It complements tsc/eslint,
 * it does not replace them.
 *
 * CLI: node validate-lumen-compliance.mjs --config <cfg.json> --evidence <resolution.json> [--strict] <files...>
 * Exit: 0 = no violations, 1 = violations (or warnings with --strict), 2 = usage/config error
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const GLOBAL_PROPS = new Set(['key', 'ref', 'children', 'className', 'id', 'role', 'tabIndex']);

/** Blank out comments (keeping offsets/newlines) and collect ignore directives. */
function stripComments(src) {
  const out = src.split('');
  const ignores = new Map(); // line number -> Set(rules)
  let i = 0, line = 1, state = 'code', quote = '';
  const recordIgnore = (text, atLine) => {
    const m = text.match(/lumen-compliance-ignore-next-line\s+([\w-]+)(?:\s*--\s*(.+))?/);
    if (m) {
      const set = ignores.get(atLine + 1) ?? new Map();
      set.set(m[1], (m[2] ?? '').trim());
      ignores.set(atLine + 1, set);
    }
  };
  while (i < src.length) {
    const c = src[i], n = src[i + 1];
    if (c === '\n') {
      line++;
      // ' and " strings cannot span lines; this recovers from apostrophes in JSX text ("Don't")
      if (state === 'str' && quote !== '`') state = 'code';
    }
    if (state === 'code') {
      if (c === '/' && n === '/') {
        let j = i; while (j < src.length && src[j] !== '\n') j++;
        recordIgnore(src.slice(i, j), line);
        for (let k = i; k < j; k++) out[k] = ' ';
        i = j; continue;
      }
      if (c === '/' && n === '*') {
        let j = src.indexOf('*/', i + 2); j = j === -1 ? src.length : j + 2;
        recordIgnore(src.slice(i, j), line);
        for (let k = i; k < j; k++) if (src[k] !== '\n') out[k] = ' ';
        line += (src.slice(i, j).match(/\n/g) ?? []).length;
        i = j; continue;
      }
      if (c === '"' || c === "'" || c === '`') { state = 'str'; quote = c; }
    } else if (state === 'str') {
      if (c === '\\') { i += 2; continue; }
      if (c === quote) state = 'code';
    }
    i++;
  }
  return { code: out.join(''), ignores };
}

const lineOf = (src, idx) => src.slice(0, idx).split('\n').length;

/** Skip a balanced {...} starting at src[i] === '{'. Returns index after the closing brace. */
function skipBraces(src, i) {
  let depth = 0;
  while (i < src.length) {
    const c = src[i];
    if (c === '"' || c === "'" || c === '`') {
      const q = c; i++;
      while (i < src.length && src[i] !== q) { if (src[i] === '\\') i++; i++; }
    } else if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return i + 1; }
    i++;
  }
  return i;
}

/** Parse attribute names of a JSX opening tag that starts right after the tag name. */
function parseJsxAttrs(src, i) {
  const attrs = []; let spread = false;
  while (i < src.length) {
    while (/\s/.test(src[i] ?? '')) i++;
    if (src[i] === '>' || (src[i] === '/' && src[i + 1] === '>')) break;
    if (src[i] === '{') { spread = true; i = skipBraces(src, i); continue; }
    const m = /^[A-Za-z_$][\w$:.-]*/.exec(src.slice(i, i + 80));
    if (!m) { i++; continue; }
    attrs.push(m[0]); i += m[0].length;
    while (/\s/.test(src[i] ?? '')) i++;
    if (src[i] === '=') {
      i++; while (/\s/.test(src[i] ?? '')) i++;
      if (src[i] === '{') i = skipBraces(src, i);
      else if (src[i] === '"' || src[i] === "'") { const q = src[i++]; while (i < src.length && src[i] !== q) i++; i++; }
    }
  }
  return { attrs, spread };
}

function parseImports(code) {
  const imports = [];
  const re = /import\s+(type\s+)?([\s\S]*?)\s+from\s+['"]([^'"]+)['"]|import\s+['"]([^'"]+)['"]|(?:require|import)\(\s*['"]([^'"]+)['"]\s*\)/g;
  let m;
  while ((m = re.exec(code))) {
    const spec = m[3] ?? m[4] ?? m[5];
    const names = []; let namespace = null, def = null;
    const clause = m[2];
    if (clause) {
      const ns = clause.match(/\*\s+as\s+([\w$]+)/); if (ns) namespace = ns[1];
      const braces = clause.match(/\{([\s\S]*)\}/);
      if (braces) for (const part of braces[1].split(',')) {
        const p = part.trim().replace(/^type\s+/, ''); if (!p) continue;
        const [imported, local] = p.split(/\s+as\s+/).map((s) => s.trim());
        names.push({ imported, local: local ?? imported });
      }
      const d = clause.replace(/\{[\s\S]*\}/, '').replace(/\*\s+as\s+[\w$]+/, '').replace(/,/g, '').trim();
      if (d) def = d;
    }
    imports.push({ spec, names, namespace, def, typeOnly: !!m[1], line: lineOf(code, m.index) });
  }
  return imports;
}

export function validateSource(src, { kind = 'component', config, evidence, file = '<memory>' }) {
  const violations = [], warnings = [], waivers = [];
  const { code, ignores } = stripComments(src);

  const add = (list, rule, line, message) => {
    const w = ignores.get(line)?.get(rule);
    if (w !== undefined) { waivers.push({ rule, line, reason: w }); return; }
    list.push({ rule, line, message });
  };

  const lumenPrefixes = config.lumenImportPrefixes ?? [];
  const allowed = [...(config.allowedImportPrefixes ?? []), ...(kind === 'story' ? config.storyExtraImportPrefixes ?? [] : [])];
  const aliases = config.allowedAliasPrefixes ?? [];
  const isLumen = (s) => lumenPrefixes.some((p) => s === p || s.startsWith(p + '/'));
  const evComponents = evidence?.components ?? {};

  // --- imports
  const lumenLocals = new Map(); // local name -> imported name
  for (const imp of parseImports(code)) {
    const rel = imp.spec.startsWith('.') || aliases.some((a) => imp.spec.startsWith(a));
    const ok = rel || isLumen(imp.spec) || allowed.some((p) => imp.spec === p || imp.spec.startsWith(p));
    if (!ok) add(violations, 'disallowed-import', imp.line, `Import from "${imp.spec}" is not on the allow-list`);
    if (isLumen(imp.spec)) {
      if (imp.namespace) add(violations, 'no-namespace-lumen-import', imp.line, `Namespace import of "${imp.spec}"; import named components`);
      if (imp.def) add(warnings, 'lumen-default-import', imp.line, `Default import "${imp.def}" from "${imp.spec}"; confirm via MCP evidence`);
      for (const { imported, local } of imp.names) {
        lumenLocals.set(local, imported);
        const ev = evComponents[imported];
        if (!ev) add(violations, 'unverified-lumen-import', imp.line, `"${imported}" has no MCP evidence in lumen-resolution.json`);
        else if (ev.import && ev.import !== imp.spec) add(violations, 'wrong-lumen-import-path', imp.line, `"${imported}" must be imported from "${ev.import}", not "${imp.spec}"`);
      }
    }
  }

  // --- JSX props on Lumen components
  const jsx = /(?<![\w$)\]])<([A-Z][\w$]*)(?![\w$.])/g; let m;
  while ((m = jsx.exec(code))) {
    const imported = lumenLocals.get(m[1]);
    if (!imported) continue;
    const ev = evComponents[imported]; if (!ev) continue;
    const known = new Set([...(ev.props ?? []), ...GLOBAL_PROPS]);
    const { attrs, spread } = parseJsxAttrs(code, m.index + m[0].length);
    for (const a of attrs) {
      if (known.has(a) || a.startsWith('data-') || a.startsWith('aria-')) continue;
      add(violations, 'unverified-lumen-prop', lineOf(code, m.index), `<${imported}> prop "${a}" is not in MCP-verified props [${[...(ev.props ?? [])].join(', ')}]`);
    }
    if (spread) add(warnings, 'lumen-prop-spread', lineOf(code, m.index), `<${imported}> uses a spread; props cannot be verified statically`);
  }

  // --- raw design values
  const scan = (re, rule, msg, list = violations) => {
    let x; const r = new RegExp(re.source, re.flags.includes('g') ? re.flags : re.flags + 'g');
    while ((x = r.exec(code))) add(list, rule, lineOf(code, x.index), msg(x[0]));
  };
  if (config.forbidInlineStyle !== false) scan(/(?<![\w$])style\s*=\s*\{/, 'no-inline-style', () => 'Inline style prop; use Lumen props/tokens');
  if (config.forbidHexColors !== false) scan(/#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![\w-])/, 'no-hex-color', (t) => `Hardcoded colour ${t}`);
  scan(/\b(?:rgb|rgba|hsl|hsla)\s*\(/, 'no-color-function', (t) => `Colour function ${t}`);
  if (kind === 'component' && config.forbidRawPx !== false) scan(/\b\d+(?:\.\d+)?px\b/, 'no-hardcoded-px', (t) => `Hardcoded ${t}; use a Lumen spacing/size token`);
  if (config.forbidAny !== false) scan(/(?::\s*any\b|<any>|\bas\s+any\b)/, 'no-any', () => 'Use of `any`');
  const raw = (config.forbiddenRawElements ?? ['button', 'input', 'select', 'textarea']).join('|');
  if (raw) scan(new RegExp(`(?<![\\w$)\\]])<(${raw})(?![\\w-])`), 'no-raw-interactive-element', (t) => `Raw ${t}>; use the Lumen equivalent`);
  if (config.warnOnRawLayoutElements !== false) scan(/(?<![\w$)\]])<(div|span)(?![\w-])/, 'raw-layout-element', (t) => `Raw ${t}>; prefer Lumen layout primitives`, warnings);
  if (config.warnOnClassName !== false) scan(/\bclassName\s*=\s*["'`]/, 'literal-classname', () => 'Literal className; styling should come from Lumen', warnings);

  // --- provenance header
  if (config.requireGeneratedHeader !== false && !/@generated-by\s+figma-to-react-lumen/.test(src)) {
    add(violations, 'missing-generated-header', 1, 'Missing "@generated-by figma-to-react-lumen" header');
  }
  return { file, kind, violations, warnings, waivers };
}

export function kindOf(file) {
  return /\.(stories|story)\.[tj]sx?$/.test(file) ? 'story' : 'component';
}

export function validateFile(file, opts) {
  return validateSource(fs.readFileSync(file, 'utf8'), { ...opts, kind: kindOf(file), file });
}

// CLI
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const args = process.argv.slice(2); const files = []; let cfgPath, evPath, strict = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--config') cfgPath = args[++i];
    else if (args[i] === '--evidence') evPath = args[++i];
    else if (args[i] === '--strict') strict = true;
    else files.push(args[i]);
  }
  if (!cfgPath || !evPath || !files.length) {
    console.error('usage: validate-lumen-compliance.mjs --config <cfg.json> --evidence <lumen-resolution.json> [--strict] <files...>');
    process.exit(2);
  }
  let config, evidence;
  try { config = JSON.parse(fs.readFileSync(cfgPath, 'utf8')); evidence = JSON.parse(fs.readFileSync(evPath, 'utf8')); }
  catch (e) { console.error(`config/evidence error: ${e.message}`); process.exit(2); }

  let bad = 0; const results = [];
  for (const f of files) {
    const r = validateFile(f, { config, evidence }); results.push(r);
    const fail = r.violations.length > 0 || (strict && r.warnings.length > 0);
    if (fail) bad++;
    console.log(`${fail ? 'FAIL' : 'PASS'}  ${path.relative(process.cwd(), f)}  (${r.violations.length} violations, ${r.warnings.length} warnings, ${r.waivers.length} waivers)`);
    for (const v of r.violations) console.log(`   ✗ [${v.rule}] line ${v.line}: ${v.message}`);
    for (const w of r.warnings) console.log(`   ! [${w.rule}] line ${w.line}: ${w.message}`);
  }
  console.log(JSON.stringify({ summary: { files: files.length, failed: bad, waivers: results.flatMap((r) => r.waivers.map((w) => ({ file: r.file, ...w }))) } }));
  process.exit(bad ? 1 : 0);
}
