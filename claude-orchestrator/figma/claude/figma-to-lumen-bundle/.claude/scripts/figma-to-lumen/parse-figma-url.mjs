#!/usr/bin/env node
/**
 * parse-figma-url.mjs
 * Deterministically parse a Figma URL into { fileKey, nodeId, ... }.
 * No network access, no dependencies.
 *
 * CLI:  node parse-figma-url.mjs "<figma-url>"   -> prints JSON, exit 1 on invalid input
 * API:  import { parseFigmaUrl } from './parse-figma-url.mjs'
 *
 * URL shapes handled:
 *   https://www.figma.com/design/<fileKey>/<name>?node-id=1-2
 *   https://www.figma.com/file/<fileKey>/<name>?node-id=1%3A2          (legacy)
 *   https://www.figma.com/design/<fileKey>/branch/<branchKey>/<name>   (branch: branchKey is the file key)
 *   https://www.figma.com/proto/<fileKey>/<name>?node-id=1-2           (prototype)
 *   https://www.figma.com/board/<fileKey>/<name>                       (FigJam: unsupported)
 *   https://www.figma.com/make/<fileKey>/<name>                        (Figma Make: unsupported)
 */

const ALLOWED_HOSTS = new Set(['figma.com', 'www.figma.com']);
const SUPPORTED_KINDS = new Set(['design', 'file', 'proto']);
const UNSUPPORTED_KINDS = new Set(['board', 'make', 'slides', 'buzz']);
const NODE_ID_RE = /^I?\d+:\d+(;\d+:\d+)*$/;
const FILE_KEY_RE = /^[A-Za-z0-9]{6,64}$/;

/** Convert "1-2", "1:2", "1%3A2", "I5666-180910;1-10515" -> API form "1:2". */
export function normalizeNodeId(raw) {
  if (raw == null || raw === '') return null;
  let v = raw;
  try { v = decodeURIComponent(raw); } catch { /* keep raw */ }
  v = v.trim().replace(/-/g, ':');
  return NODE_ID_RE.test(v) ? v : undefined; // undefined = present but malformed
}

export function parseFigmaUrl(input) {
  const result = { ok: false, error: null };
  if (typeof input !== 'string' || !input.trim()) {
    return { ...result, error: 'Empty or non-string URL' };
  }

  let url;
  try { url = new URL(input.trim()); } catch {
    return { ...result, error: 'Not a valid URL' };
  }
  if (url.protocol !== 'https:' && url.protocol !== 'http:') {
    return { ...result, error: `Unsupported protocol ${url.protocol}` };
  }
  if (!ALLOWED_HOSTS.has(url.hostname.toLowerCase())) {
    return { ...result, error: `Host "${url.hostname}" is not figma.com` };
  }

  const segs = url.pathname.split('/').filter(Boolean).map((s) => decodeURIComponent(s));
  const kind = segs[0];
  if (!kind) return { ...result, error: 'URL has no path' };
  if (UNSUPPORTED_KINDS.has(kind)) {
    return { ...result, kind, error: `Figma "${kind}" files are not supported; provide a /design/ URL with hi-fi screens` };
  }
  if (!SUPPORTED_KINDS.has(kind)) {
    return { ...result, kind, error: `Unrecognised Figma URL type "/${kind}/"` };
  }

  let fileKey = segs[1];
  let parentFileKey = null;
  let branchKey = null;
  let fileName = segs[2] ?? null;
  if (segs[2] === 'branch' && segs[3]) {
    // /design/<fileKey>/branch/<branchKey>/<name>: the branch key is the key to use for API calls
    parentFileKey = segs[1];
    branchKey = segs[3];
    fileKey = branchKey;
    fileName = segs[4] ?? null;
  }
  if (!fileKey || !FILE_KEY_RE.test(fileKey)) {
    return { ...result, kind, error: 'Missing or malformed file key' };
  }

  const rawNode = url.searchParams.get('node-id');
  const nodeId = normalizeNodeId(rawNode);
  if (rawNode && nodeId === undefined) {
    return { ...result, kind, fileKey, error: `Malformed node-id "${rawNode}"` };
  }

  return {
    ok: true,
    error: null,
    kind,
    fileKey,
    parentFileKey,
    branchKey,
    fileName,
    nodeId: nodeId ?? null,            // API form, e.g. "12:34"
    nodeIdUrl: nodeId ? nodeId.replace(/:/g, '-') : null, // URL form, e.g. "12-34"
    devMode: url.searchParams.get('m') === 'dev',
    scope: nodeId ? 'node' : 'file',   // "file" => enumerate pages / top-level frames
  };
}

// CLI
import { fileURLToPath } from 'node:url';
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const out = parseFigmaUrl(process.argv[2]);
  process.stdout.write(JSON.stringify(out, null, 2) + '\n');
  process.exit(out.ok ? 0 : 1);
}
