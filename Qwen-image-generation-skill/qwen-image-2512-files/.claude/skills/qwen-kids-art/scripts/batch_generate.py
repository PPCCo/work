#!/usr/bin/env python3
"""
batch_generate.py - run a plan from build_prompt.py against a local ComfyUI.

Use the ComfyUI MCP tools for one-off images and conversation-driven work. Use
this when you want twenty images, a seed sweep, or a written record of exactly
which prompt and seed produced which file. That record is what turns "sometimes
it's good" into a library of settings you can rely on.

  python batch_generate.py --plan plan.json \
      --workflow ~/ComfyUI/user/default/workflows/qwen_image_2512_t2i_api.json \
      --out ~/kids-art/run-2026-09-19

Requires: a ComfyUI workflow exported in **API format** (Workflow -> Export
(API)), built on the Qwen-Image-2512 Q8_0 loader stack (UNETLoaderGGUF +
CLIPLoader/CLIPLoaderGGUF + VAELoader - see references/comfyui-runtime.md).
Standard-format exports will not queue. Only the standard library is used, so
no pip install is needed.

Unlike the old Klein setup, the negative-prompt node this script detects is
now real: on a "full"-variant plan it is patched with the pack's negative
text; on "lightning" the plan's negative is already blank (CFG is 1.0 there
and the branch is inert - see qwen-prompt-standards.md #3), so the node is
still patched, just with nothing to exclude.

Dry run first - it prints every patch it intends to make:
  python batch_generate.py --plan plan.json --workflow wf.json --dry-run
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request

POS_HINTS = ("positive", "prompt", "text")
NEG_HINTS = ("negative",)


def http_json(url, payload=None, timeout=30):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def find_nodes(wf):
    """Locate the nodes we need to patch. Returns dict of role -> node id."""
    roles = {"positive": None, "negative": None, "latent": None, "sampler": None}
    for nid, node in wf.items():
        cls = node.get("class_type", "")
        ins = node.get("inputs", {})
        title = (node.get("_meta", {}).get("title", "") or "").lower()
        if "TextEncode" in cls or "TextEncodeFlux" in cls or "Qwen" in cls:
            if any(h in title for h in NEG_HINTS):
                roles["negative"] = nid
            elif roles["positive"] is None or any(h in title for h in POS_HINTS):
                roles["positive"] = roles["positive"] or nid
        if "EmptyLatent" in cls or "EmptySD3Latent" in cls or "EmptyFlux" in cls:
            roles["latent"] = nid
        if "KSampler" in cls or "SamplerCustom" in cls:
            roles["sampler"] = nid
        if "seed" in ins and roles["sampler"] is None:
            roles["sampler"] = nid
    return roles


def patch(wf, roles, prompt, negative, params, seed, overrides):
    wf = json.loads(json.dumps(wf))  # deep copy
    pos = overrides.get("positive") or roles["positive"]
    neg = overrides.get("negative") or roles["negative"]
    lat = overrides.get("latent") or roles["latent"]
    smp = overrides.get("sampler") or roles["sampler"]
    if pos is None or smp is None:
        raise SystemExit("Could not find the text-encode or sampler node. Pass "
                         "--positive-node / --sampler-node with the ids from your "
                         "API-format workflow JSON.")
    wf[pos]["inputs"]["text"] = prompt
    if neg is not None:
        wf[neg]["inputs"]["text"] = negative
    elif negative:
        print("WARN: plan has a negative prompt but no negative text-encode node "
              "was found in this workflow. Pass --negative-node, or the negative "
              "prompt is being silently dropped.")
    if lat:
        wf[lat]["inputs"]["width"] = params["width"]
        wf[lat]["inputs"]["height"] = params["height"]
    s = wf[smp]["inputs"]
    for key in ("seed", "noise_seed"):
        if key in s:
            s[key] = seed
    for key in ("steps", "cfg", "sampler_name", "scheduler", "denoise"):
        src = {"sampler_name": "sampler"}.get(key, key)
        if key in s and src in params:
            s[key] = params[src]
    return wf


def wait_for(base, prompt_id, timeout=900, poll=2.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        hist = http_json("%s/history/%s" % (base, prompt_id))
        if prompt_id in hist:
            entry = hist[prompt_id]
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                raise RuntimeError("ComfyUI reported an error: %s" % json.dumps(status)[:400])
            if entry.get("outputs"):
                return entry
        time.sleep(poll)
    raise TimeoutError("Timed out waiting for %s" % prompt_id)


def download_images(base, entry, out_dir, stem, seed):
    saved = []
    for node_out in entry.get("outputs", {}).values():
        for img in node_out.get("images", []):
            q = urllib.parse.urlencode({
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            })
            with urllib.request.urlopen("%s/view?%s" % (base, q), timeout=120) as r:
                blob = r.read()
            name = "%s_seed%d_%s" % (stem, seed, img["filename"])
            path = os.path.join(out_dir, name)
            with open(path, "wb") as fh:
                fh.write(blob)
            saved.append(path)
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="Output of build_prompt.py --out")
    ap.add_argument("--workflow", required=True, help="API-format ComfyUI workflow JSON")
    ap.add_argument("--out", default="./qwen-out")
    ap.add_argument("--server", default="http://127.0.0.1:8188")
    ap.add_argument("--candidates", type=int, default=None,
                    help="Override how many seeds per image (default: the plan's)")
    ap.add_argument("--only", help="Comma-separated image ids to run")
    ap.add_argument("--positive-node")
    ap.add_argument("--negative-node")
    ap.add_argument("--sampler-node")
    ap.add_argument("--latent-node")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-failed-audit", action="store_true", default=True)
    a = ap.parse_args()

    base = a.server.rstrip("/")
    plan = json.load(open(a.plan, encoding="utf-8"))
    wf = json.load(open(a.workflow, encoding="utf-8"))
    if "nodes" in wf and "last_node_id" in wf:
        raise SystemExit("That looks like a UI-format workflow. In ComfyUI use "
                         "Workflow -> Export (API) and pass that file instead.")
    roles = find_nodes(wf)
    overrides = {"positive": a.positive_node, "negative": a.negative_node,
                "sampler": a.sampler_node, "latent": a.latent_node}
    print("Detected nodes: %s" % json.dumps(roles))

    os.makedirs(a.out, exist_ok=True)
    manifest_path = os.path.join(a.out, "manifest.jsonl")
    only = set(x.strip() for x in a.only.split(",")) if a.only else None

    queued = 0
    for img in plan["images"]:
        if only and img["id"] not in only:
            continue
        if a.skip_failed_audit and not img["audit"]["status"].startswith("PASS"):
            print("SKIP %s - failed audit (%d/100)" % (img["id"], img["audit"]["score"]))
            continue
        seeds = img["seeds"][:a.candidates] if a.candidates else img["seeds"]
        for seed in seeds:
            negative = img.get("negative", "")
            body = patch(wf, roles, img["prompt"], negative, img["params"], seed, overrides)
            if a.dry_run:
                print("DRY RUN %s seed=%d %dx%d steps=%s cfg=%s variant=%s negative=%r" % (
                    img["id"], seed, img["params"]["width"], img["params"]["height"],
                    img["params"]["steps"], img["params"]["cfg"],
                    img["params"].get("variant", "?"), negative))
                continue
            resp = http_json("%s/prompt" % base,
                             {"prompt": body, "client_id": "qwen-kids-art-%d" % random.randrange(1 << 30)})
            pid = resp.get("prompt_id")
            if not pid:
                print("QUEUE FAILED for %s: %s" % (img["id"], json.dumps(resp)[:300]))
                continue
            try:
                entry = wait_for(base, pid)
                files = download_images(base, entry, a.out, img["filename_stem"], seed)
            except Exception as exc:  # keep the batch going
                print("ERROR %s seed=%d: %s" % (img["id"], seed, exc))
                continue
            with open(manifest_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "id": img["id"], "seed": seed, "prompt": img["prompt"],
                    "negative": negative, "params": img["params"],
                    "pack": plan["pack"], "age": plan["age"],
                    "files": files, "prompt_id": pid, "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }, ensure_ascii=False) + "\n")
            queued += 1
            print("OK %s seed=%d -> %s" % (img["id"], seed, ", ".join(os.path.basename(f) for f in files)))

    if not a.dry_run:
        print("\n%d images written to %s\nManifest: %s" % (queued, a.out, manifest_path))
        print("Review them, then record the winning seeds in the manifest's sibling "
              "notes file so the next run starts from a known-good setting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
