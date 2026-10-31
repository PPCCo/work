#!/usr/bin/env node
/**
 * selftest.mjs: proves the deterministic parts of the pipeline work.
 * Run:  node .claude/scripts/figma-to-lumen/selftest.mjs
 * Exit: 0 all pass, 1 any failure
 * Uses only fixtures (no MCP, no network).
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseFigmaUrl } from './parse-figma-url.mjs';
import { validateSource, validateFile } from './validate-lumen-compliance.mjs';
import { verifyManifest } from './verify-manifest.mjs';
import { preflight } from './preflight.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = path.join(here, '__fixtures__');
const readJson = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const config = readJson(path.join(fx, 'lumen-compliance.config.json'));
const evidence = readJson(path.join(fx, 'lumen-resolution.json'));
const repo = path.join(fx, 'repo');

let pass = 0, fail = 0;
const test = (name, fn) => {
  try { fn(); pass++; console.log(`PASS  ${name}`); }
  catch (e) { fail++; console.log(`FAIL  ${name}\n      ${e.message}`); }
};
const eq = (a, b, m = '') => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m} expected ${JSON.stringify(b)} got ${JSON.stringify(a)}`); };
const ok = (c, m) => { if (!c) throw new Error(m); };
const rules = (r) => new Set(r.violations.map((v) => v.rule));

// ---- URL parser
test('url: /design with dashed node-id', () => {
  const r = parseFigmaUrl('https://www.figma.com/design/AbC123xyz9/My-App?node-id=12-34&m=dev');
  ok(r.ok); eq(r.fileKey, 'AbC123xyz9'); eq(r.nodeId, '12:34'); eq(r.nodeIdUrl, '12-34'); eq(r.devMode, true); eq(r.scope, 'node');
});
test('url: legacy /file with encoded colon', () => {
  const r = parseFigmaUrl('https://figma.com/file/AbC123xyz9/Name?node-id=1%3A2');
  ok(r.ok); eq(r.nodeId, '1:2');
});
test('url: no node-id => file scope', () => {
  const r = parseFigmaUrl('https://www.figma.com/design/AbC123xyz9/Name');
  ok(r.ok); eq(r.nodeId, null); eq(r.scope, 'file');
});
test('url: branch uses branch key', () => {
  const r = parseFigmaUrl('https://www.figma.com/design/ParentKey99/branch/BranchKey88/Name?node-id=3-4');
  ok(r.ok); eq(r.fileKey, 'BranchKey88'); eq(r.parentFileKey, 'ParentKey99');
});
test('url: instance node id', () => {
  const r = parseFigmaUrl('https://www.figma.com/design/AbC123xyz9/N?node-id=I5666-180910%3B1-10515');
  ok(r.ok); eq(r.nodeId, 'I5666:180910;1:10515');
});
test('url: rejects FigJam, foreign host, junk, malformed node', () => {
  ok(!parseFigmaUrl('https://www.figma.com/board/AbC123xyz9/Jam').ok, 'board');
  ok(!parseFigmaUrl('https://evil.example.com/design/AbC123xyz9/N').ok, 'host');
  ok(!parseFigmaUrl('not a url').ok, 'junk');
  ok(!parseFigmaUrl('https://www.figma.com/design/AbC123xyz9/N?node-id=abc').ok, 'node');
  ok(!parseFigmaUrl('').ok, 'empty');
});

// ---- validator: good fixtures
test('validator: good component passes with zero violations', () => {
  const r = validateFile(path.join(repo, 'src/components/Demo/Demo.tsx'), { config, evidence });
  eq(r.violations, [], 'violations');
});
test('validator: good story passes with zero violations', () => {
  const r = validateFile(path.join(repo, 'src/components/Demo/Demo.stories.tsx'), { config, evidence });
  eq(r.violations, [], 'violations');
});

// ---- validator: bad fixture must trip every intended rule
test('validator: bad fixture trips all intended rules', () => {
  const r = validateFile(path.join(fx, 'bad/Bad.tsx'), { config, evidence });
  const got = rules(r);
  for (const want of ['missing-generated-header', 'disallowed-import', 'no-namespace-lumen-import', 'unverified-lumen-import',
    'no-any', 'no-inline-style', 'no-hex-color', 'no-hardcoded-px', 'unverified-lumen-prop', 'no-raw-interactive-element']) {
    ok(got.has(want), `expected rule ${want}; got ${[...got].join(', ')}`);
  }
});
test('validator: wrong Lumen import path is caught', () => {
  const src = `/** @generated-by figma-to-react-lumen */\nimport { Button } from '@fixture/lumen/elsewhere';\nexport const A = () => <Button variant="primary">x</Button>;\n`;
  ok(rules(validateSource(src, { config, evidence })).has('wrong-lumen-import-path'));
});
test('validator: aliased Lumen import still has its props checked', () => {
  const src = `/** @generated-by figma-to-react-lumen */\nimport { Button as B } from '@fixture/lumen';\nexport const A = () => <B sparkle>x</B>;\n`;
  ok(rules(validateSource(src, { config, evidence })).has('unverified-lumen-prop'));
});
test('validator: props inside multi-line, nested-brace attributes parse correctly', () => {
  const src = `/** @generated-by figma-to-react-lumen */\nimport { Button } from '@fixture/lumen';\nexport const A = () => (\n  <Button\n    onClick={() => { const o = { a: 1 }; return o; }}\n    variant="primary"\n    shiny\n  >x</Button>\n);\n`;
  const r = validateSource(src, { config, evidence });
  const props = r.violations.filter((v) => v.rule === 'unverified-lumen-prop');
  eq(props.length, 1, 'prop violations'); ok(props[0].message.includes('"shiny"'), props[0].message);
});
test('validator: colours in comments and generics are not false positives', () => {
  const src = `/** @generated-by figma-to-react-lumen */\n// brand was #ff0000 once\nimport { Text } from '@fixture/lumen';\nconst xs: Array<Record<string, number>> = [];\nexport const A = () => <Text variant="body">hi</Text>;\n`;
  eq(validateSource(src, { config, evidence }).violations, []);
});
test('validator: apostrophe in JSX text does not break comment stripping', () => {
  const src = `/** @generated-by figma-to-react-lumen */\nimport { Text } from '@fixture/lumen';\nexport const A = () => <Text variant="body">Don't panic</Text>;\n// old: #00ff00\n`;
  eq(validateSource(src, { config, evidence }).violations, []);
});
test('validator: waiver comment suppresses exactly one rule on the next line and is reported', () => {
  const src = `/** @generated-by figma-to-react-lumen */\nimport { Text } from '@fixture/lumen';\n// lumen-compliance-ignore-next-line no-hex-color -- brand gradient not in Lumen, ticket ABC-1\nconst c = '#123456';\nexport const A = () => <Text variant="body">{c}</Text>;\n`;
  const r = validateSource(src, { config, evidence });
  eq(r.violations, []); eq(r.waivers.length, 1); ok(r.waivers[0].reason.includes('ABC-1'));
});

// ---- manifest verifier
const snapshot = readJson(path.join(repo, 'design-sync/abc123/source-snapshot.json'));
const manifest = readJson(path.join(repo, 'design-sync/abc123/manifest.json'));
const clone = (o) => JSON.parse(JSON.stringify(o));

test('manifest: good fixture passes', () => {
  const r = verifyManifest({ snapshot, manifest, repo }); eq(r.errors, []); ok(r.ok);
});
test('manifest: uncovered inventory item fails', () => {
  const m = clone(manifest); m.gaps = [];
  const r = verifyManifest({ snapshot, manifest: m, repo });
  ok(!r.ok && r.errors.some((e) => e.includes('2:1')), r.errors.join('; '));
});
test('manifest: gap without reason fails', () => {
  const m = clone(manifest); delete m.gaps[0].reason;
  ok(!verifyManifest({ snapshot, manifest: m, repo }).ok);
});
test('manifest: missing generated file fails', () => {
  const m = clone(manifest); m.entries[0].files.component = 'src/components/Demo/Nope.tsx';
  const r = verifyManifest({ snapshot, manifest: m, repo }); ok(!r.ok && r.errors.some((e) => e.includes('file not found')));
});
test('manifest: more Figma variants than stories fails', () => {
  const m = clone(manifest); m.entries[0].variants = ['Default', 'Loading', 'Disabled'];
  const r = verifyManifest({ snapshot, manifest: m, repo }); ok(!r.ok && r.errors.some((e) => e.includes('variants')));
});
test('manifest: ignored inventory item needs a reason', () => {
  const s = clone(snapshot); delete s.inventory[1].ignoreReason;
  ok(!verifyManifest({ snapshot: s, manifest, repo }).ok);
});

// ---- preflight
test('preflight: empty dir reports blockers instead of crashing', () => {
  const r = preflight({ repo: path.join(fx, 'bad') });
  ok(!r.ok && r.blockers.length > 0);
});

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
