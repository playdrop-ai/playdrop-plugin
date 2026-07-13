#!/usr/bin/env python3
"""Serve a local human-review queue and persist family decisions."""

from __future__ import annotations

import argparse
import json
import mimetypes
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from asset_pack_common import read_json, write_json
from build_approved_manifest import write_approved_manifest
from record_review import promote


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>2D Asset Pack Review</title>
<style>
:root{color-scheme:light;--ink:#18181b;--muted:#6b7280;--line:#d4d4d8;--accent:#7c3aed;--good:#15803d;--bad:#b91c1c}*{box-sizing:border-box}body{margin:0;font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:#f4f4f5}header{position:sticky;top:0;z-index:2;background:#fff;border-bottom:1px solid var(--line);padding:14px 22px;display:flex;align-items:center;justify-content:space-between}h1{font-size:18px;margin:0;letter-spacing:0}main{max-width:1440px;margin:0 auto;padding:20px}.status{color:var(--muted)}.family{background:#fff;border:1px solid var(--line);border-radius:8px;margin-bottom:18px;overflow:hidden}.family-head{padding:16px 18px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;align-items:center}.family h2{font-size:17px;margin:0;letter-spacing:0}.gates{color:var(--muted);font-size:13px}.boards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line)}figure{margin:0;background:#fff;padding:12px}figcaption{font-size:12px;color:var(--muted);margin-bottom:8px}img{display:block;width:100%;height:auto;border:1px solid var(--line)}form{padding:16px 18px;display:grid;grid-template-columns:auto auto minmax(180px,1fr) auto;gap:12px;align-items:center}.choice{display:flex;align-items:center;gap:6px}input[type=text]{width:100%;padding:9px 10px;border:1px solid #a1a1aa;border-radius:5px;font:inherit}button{border:0;border-radius:5px;padding:9px 14px;background:var(--accent);color:#fff;font-weight:650;cursor:pointer}button:disabled{opacity:.45;cursor:not-allowed}.message{padding:0 18px 14px;color:var(--muted)}@media(max-width:800px){.boards{grid-template-columns:1fr}form{grid-template-columns:1fr 1fr}input[type=text]{grid-column:1/-1}button{grid-column:1/-1}}
</style>
</head>
<body><header><h1>2D Asset Pack Review</h1><div id="summary" class="status">Loading</div></header><main id="app"></main>
<script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){const response=await fetch('/api/families');const data=await response.json();const count=data.families.length;document.getElementById('summary').textContent=count===1?'1 family':`${count} families`;const app=document.getElementById('app');app.innerHTML=data.families.map(f=>`<section class="family" data-id="${esc(f.familyId)}"><div class="family-head"><h2>${esc(f.family)}</h2><div class="gates">code ${esc(f.validation.code)} | Codex ${esc(f.validation.codex)} | human ${esc(f.validation.human)}</div></div><div class="boards">${f.boards.map(b=>`<figure><figcaption>${esc(b.label)}</figcaption><img loading="lazy" src="${esc(b.url)}" alt="${esc(f.family)} ${esc(b.label)}"></figure>`).join('')}</div><form><label class="choice"><input required type="radio" name="decision" value="approve">Approve</label><label class="choice"><input required type="radio" name="decision" value="reject">Reject</label><input type="text" name="comment" placeholder="Optional comment"><button ${f.canReview?'':'disabled'} type="submit">Submit</button></form><div class="message">${f.canReview?'Ready for human review':'Codex approval is required first.'}</div></section>`).join('')||'<p>No family status files found.</p>';for(const form of app.querySelectorAll('form'))form.addEventListener('submit',submit);}
async function submit(event){event.preventDefault();const section=event.target.closest('.family');const body={familyId:section.dataset.id,decision:new FormData(event.target).get('decision'),comment:new FormData(event.target).get('comment')||''};const response=await fetch('/api/review',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const result=await response.json();section.querySelector('.message').textContent=response.ok?`Saved: ${result.status}`:`Error: ${result.error}`;if(response.ok)await load();}
load();
</script></body></html>"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReviewHandler(BaseHTTPRequestHandler):
    pack_root: Path
    spec_path: Path

    def log_message(self, format: str, *args: object) -> None:
        return

    def json_response(self, value: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/":
            data = HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if route == "/api/families":
            self.json_response({"families": self.list_families()})
            return
        if route.startswith("/files/"):
            self.serve_file(unquote(route[len("/files/"):]))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/review":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        expected_origin = f"http://{self.headers.get('Host', '')}"
        if self.headers.get("Origin") != expected_origin:
            self.json_response({"error": "origin_not_allowed"}, HTTPStatus.FORBIDDEN)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            result = self.record(payload)
            self.json_response(result)
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            self.json_response({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except SystemExit as error:
            self.json_response({"error": str(error)}, HTTPStatus.CONFLICT)

    def list_families(self) -> list[dict]:
        families: list[dict] = []
        for status_path in sorted((self.pack_root / "families").glob("*/family-status.json")):
            status = read_json(status_path)
            selected_round = status.get("selectedRound")
            validation_root = status_path.parent / "validation" / str(selected_round)
            boards = []
            for name, label in (
                ("review-checker.png", "Checker"),
                ("review-white.png", "White"),
                ("review-purple.png", "Purple"),
                ("review-black.png", "Black"),
                ("small-raw-64.png", "Raw small assets at 64x64"),
                ("split-overlay.png", "Adaptive split overlay"),
            ):
                path = validation_root / name
                if path.exists():
                    boards.append({"label": label, "url": f"/files/{path.relative_to(self.pack_root)}"})
            validation = status.get("validation", {})
            families.append(
                {
                    "family": status.get("family"),
                    "familyId": status.get("familyId"),
                    "status": status.get("status"),
                    "validation": validation,
                    "canReview": validation.get("code") == "approved" and validation.get("codex") == "approved",
                    "boards": boards,
                }
            )
        return families

    def serve_file(self, relative: str) -> None:
        candidate = (self.pack_root / relative).resolve()
        try:
            candidate.relative_to(self.pack_root)
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(candidate.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def record(self, payload: dict) -> dict:
        family_id = str(payload["familyId"])
        decision = str(payload["decision"])
        comment = str(payload.get("comment", ""))
        if decision not in ("approve", "reject"):
            raise ValueError("invalid_decision")
        status_path = self.pack_root / "families" / family_id / "family-status.json"
        status = read_json(status_path)
        validation = status.get("validation", {})
        if validation.get("code") != "approved" or validation.get("codex") != "approved":
            raise SystemExit("human_review_requires_code_and_codex_approval")
        validation["human"] = "approved" if decision == "approve" else "rejected"
        if decision == "approve":
            prior_approved = status.get("approvedAssets") or status.get("lastApprovedAssets")
            newly_approved = promote(status_path, status)
            if prior_approved and prior_approved != newly_approved:
                status["lastApprovedAssets"] = prior_approved
            status["approvedAssets"] = newly_approved
            status["status"] = "approved"
        else:
            status["status"] = "human-rejected"
        event = {
            "familyId": family_id,
            "decision": decision,
            "comment": comment,
            "recordedAt": now(),
            "selectedRound": status.get("selectedRound"),
        }
        status["reviewHistory"] = [*status.get("reviewHistory", []), {"reviewer": "human", **event}]
        status["updatedAt"] = event["recordedAt"]
        write_json(status_path, status)
        write_approved_manifest(self.pack_root, self.spec_path)
        with (self.pack_root / "human-review-log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(f"{json.dumps(event)}\n")
        return {"ok": True, "status": status["status"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4177)
    args = parser.parse_args()
    root = args.pack_root.resolve()
    if not (root / "families").is_dir():
        raise SystemExit(f"families_directory_not_found:{root / 'families'}")
    spec_path = root / "pack-spec.json"
    if not spec_path.is_file():
        raise SystemExit(f"pack_spec_not_found:{spec_path}")
    handler = type("ConfiguredReviewHandler", (ReviewHandler,), {"pack_root": root, "spec_path": spec_path})
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"review_url:http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
