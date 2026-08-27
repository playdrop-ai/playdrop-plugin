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

from asset_pack_common import append_jsonl, read_json, write_json
from build_approved_manifest import write_approved_manifest
from record_review import promote


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Asset Pack Review</title>
<style>
:root{color-scheme:light;--ink:#18181b;--muted:#71717a;--faint:#a1a1aa;--line:#d4d4d8;--soft:#f4f4f5;--blue:#2563eb;--blue-soft:#eff6ff;--good:#15803d;--good-soft:#f0fdf4;--bad:#b91c1c;--bad-soft:#fef2f2}*{box-sizing:border-box}html,body{height:100%}body{margin:0;font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:#fafafa}button,textarea{font:inherit}button{cursor:pointer}.topbar{height:60px;background:#fff;border-bottom:1px solid var(--line);padding:0 20px;display:flex;align-items:center;justify-content:space-between;gap:16px}.title{display:flex;align-items:baseline;gap:10px;min-width:0}.title h1{font-size:17px;letter-spacing:0;margin:0;white-space:nowrap}.pack-name{color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.progress{font-size:13px;color:var(--muted);white-space:nowrap}.shell{height:calc(100vh - 60px);display:grid;grid-template-columns:250px minmax(0,1fr)}aside{background:#fff;border-right:1px solid var(--line);overflow:auto;padding:12px}.queue-section{margin-bottom:18px}.queue-label{margin:4px 8px 7px;color:var(--muted);font-size:11px;font-weight:700;text-transform:uppercase}.queue-item{width:100%;border:1px solid transparent;background:transparent;border-radius:6px;padding:9px 10px;display:grid;grid-template-columns:10px minmax(0,1fr) auto;gap:9px;align-items:center;text-align:left;color:var(--ink)}.queue-item:hover{background:var(--soft)}.queue-item.active{background:var(--blue-soft);border-color:#bfdbfe}.queue-item strong{font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.queue-item small{color:var(--muted)}.dot{width:8px;height:8px;border-radius:50%;background:#f59e0b}.dot.approved{background:var(--good)}.dot.rejected{background:var(--bad)}.empty{padding:12px;color:var(--muted);font-size:13px}.workspace{min-width:0;overflow:auto}.workspace-inner{min-height:100%;display:flex;flex-direction:column}.family-head{background:#fff;border-bottom:1px solid var(--line);padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px}.family-title{min-width:0}.family-title h2{font-size:18px;letter-spacing:0;margin:0 0 2px}.meta{color:var(--muted);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.state{font-size:12px;font-weight:700;border-radius:999px;padding:4px 9px;white-space:nowrap}.state.pending{color:#92400e;background:#fffbeb}.state.approved{color:var(--good);background:var(--good-soft)}.state.rejected{color:var(--bad);background:var(--bad-soft)}.tabs{background:#fff;border-bottom:1px solid var(--line);padding:8px 20px;display:flex;gap:4px;overflow:auto}.tab{border:0;background:transparent;color:var(--muted);border-radius:5px;padding:7px 10px;white-space:nowrap}.tab:hover{background:var(--soft);color:var(--ink)}.tab.active{background:var(--blue-soft);color:#1d4ed8;font-weight:700}.viewer{flex:1;min-height:380px;padding:18px;display:flex;align-items:flex-start;justify-content:center;background:#e4e4e7}.viewer button{display:block;max-width:100%;border:0;padding:0;background:transparent}.viewer img{display:block;max-width:100%;max-height:calc(100vh - 285px);width:auto;height:auto;border:1px solid #a1a1aa;background:#fff;box-shadow:0 1px 3px rgb(0 0 0/.12)}.decision{position:sticky;bottom:0;z-index:2;background:#fff;border-top:1px solid var(--line);padding:13px 20px}.decision form{display:grid;grid-template-columns:auto minmax(220px,1fr) auto;gap:12px;align-items:center}.choices{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}.choice{position:relative}.choice input{position:absolute;opacity:0;pointer-events:none}.choice span{display:block;padding:9px 12px;font-weight:650;border-right:1px solid var(--line);white-space:nowrap}.choice:last-child span{border-right:0}.choice input:focus-visible+span{outline:2px solid var(--blue);outline-offset:-2px}.choice.approve input:checked+span{background:var(--good-soft);color:var(--good)}.choice.reject input:checked+span{background:var(--bad-soft);color:var(--bad)}textarea{width:100%;min-height:42px;max-height:96px;resize:vertical;padding:9px 10px;border:1px solid #a1a1aa;border-radius:6px;color:var(--ink)}textarea:focus{outline:2px solid #93c5fd;border-color:var(--blue)}.submit{border:0;border-radius:6px;padding:10px 15px;background:var(--blue);color:#fff;font-weight:700;white-space:nowrap}.submit:disabled{opacity:.45;cursor:not-allowed}.reviewed{display:flex;align-items:center;justify-content:space-between;gap:16px}.reviewed-copy{min-width:0}.reviewed-copy strong{display:block}.reviewed-copy p{margin:2px 0 0;color:var(--muted);white-space:pre-wrap}.next{border:1px solid var(--line);border-radius:6px;background:#fff;padding:8px 12px;font-weight:650}.message{min-height:20px;margin-top:7px;font-size:12px;color:var(--muted)}.message.error{color:var(--bad)}dialog{width:min(96vw,1600px);max-width:none;border:0;border-radius:8px;padding:0;background:#18181b;box-shadow:0 20px 60px rgb(0 0 0/.45)}dialog::backdrop{background:rgb(0 0 0/.72)}.dialog-head{height:46px;padding:0 12px 0 16px;display:flex;align-items:center;justify-content:space-between;color:#fff}.dialog-close{border:0;background:#3f3f46;color:#fff;border-radius:5px;padding:6px 10px}.dialog-body{max-height:calc(95vh - 46px);overflow:auto;display:flex;justify-content:center}.dialog-body img{display:block;max-width:none;width:auto;height:auto}.blank{margin:auto;color:var(--muted);padding:40px;text-align:center}@media(max-width:850px){.shell{grid-template-columns:1fr;height:auto;min-height:calc(100vh - 60px)}aside{border-right:0;border-bottom:1px solid var(--line);display:flex;gap:8px;overflow:auto;padding:8px}.queue-section{display:flex;gap:6px;margin:0}.queue-label{display:none}.queue-item{min-width:150px}.workspace{overflow:visible}.viewer{min-height:300px;padding:10px}.viewer img{max-height:none}.decision form{grid-template-columns:1fr}.choices{width:100%}.choice{flex:1;text-align:center}.submit{width:100%}.reviewed{align-items:flex-start;flex-direction:column}.topbar{padding:0 12px}.pack-name{display:none}.family-head,.tabs,.decision{padding-left:12px;padding-right:12px}}
</style>
</head>
<body>
<header class="topbar"><div class="title"><h1>Asset Pack Review</h1><span id="pack-name" class="pack-name"></span></div><div id="summary" class="progress">Loading</div></header>
<div class="shell">
  <aside id="queue" aria-label="Review queue"></aside>
  <main class="workspace"><div id="workspace" class="workspace-inner"><div class="blank">Loading review queue</div></div></main>
</div>
<dialog id="image-dialog"><div class="dialog-head"><span id="dialog-title"></span><button id="dialog-close" class="dialog-close" type="button">Close</button></div><div class="dialog-body"><img id="dialog-image" alt=""></div></dialog>
<script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const state={families:[],currentId:null,boardIndex:0};
const reviewable=()=>state.families.filter(f=>f.reviewState!=='unavailable');
const pending=()=>reviewable().filter(f=>f.reviewState==='pending');
const completed=()=>reviewable().filter(f=>f.reviewState!=='pending');
const current=()=>reviewable().find(f=>f.familyId===state.currentId);
const draftKey=id=>`asset-pack-review-draft:${id}`;
function saveDraft(){const f=current(),form=document.getElementById('review-form');if(!f||!form)return;const data=new FormData(form);localStorage.setItem(draftKey(f.familyId),JSON.stringify({decision:data.get('decision')||'',comment:data.get('comment')||''}));updateSubmit();}
function readDraft(id){try{return JSON.parse(localStorage.getItem(draftKey(id))||'{}')}catch{return {}}}
function clearDraft(id){localStorage.removeItem(draftKey(id));}
function renderQueue(){const queue=document.getElementById('queue');const section=(label,items)=>`<div class="queue-section"><div class="queue-label">${esc(label)} · ${items.length}</div>${items.map(f=>`<button class="queue-item ${f.familyId===state.currentId?'active':''}" type="button" data-family="${esc(f.familyId)}"><span class="dot ${esc(f.reviewState)}"></span><strong>${esc(f.family)}</strong><small>${f.assetCount}</small></button>`).join('')||`<div class="empty">None</div>`}</div>`;queue.innerHTML=section('To review',pending())+section('Completed',completed());queue.querySelectorAll('[data-family]').forEach(button=>button.addEventListener('click',()=>selectFamily(button.dataset.family)));}
function selectFamily(id){state.currentId=id;state.boardIndex=0;renderQueue();renderFamily();}
function renderFamily(){const f=current(),root=document.getElementById('workspace');if(!f){root.innerHTML='<div class="blank">No families are ready for review.</div>';return}const board=f.boards[state.boardIndex]||f.boards[0];if(!board)state.boardIndex=0;const selected=f.boards[state.boardIndex]||null;const draft=readDraft(f.familyId);root.innerHTML=`<header class="family-head"><div class="family-title"><h2>${esc(f.family)}</h2><div class="meta">${f.assetCount} assets · round ${esc(f.selectedRound||'unknown')} · code approved · agent approved</div></div><span class="state ${esc(f.reviewState)}">${f.reviewState==='pending'?'Needs review':f.reviewState==='approved'?'Approved':'Needs changes'}</span></header><nav class="tabs" aria-label="Validation backgrounds">${f.boards.map((b,i)=>`<button class="tab ${i===state.boardIndex?'active':''}" type="button" data-board="${i}">${esc(b.label)}</button>`).join('')}</nav><section class="viewer">${selected?`<button id="open-image" type="button" title="Open full size"><img src="${esc(selected.url)}" alt="${esc(f.family)} ${esc(selected.label)}"></button>`:'<div class="blank">No validation board found.</div>'}</section><footer class="decision">${f.canReview?`<form id="review-form"><div class="choices"><label class="choice approve"><input type="radio" name="decision" value="approve" ${draft.decision==='approve'?'checked':''}><span>Approve</span></label><label class="choice reject"><input type="radio" name="decision" value="reject" ${draft.decision==='reject'?'checked':''}><span>Needs changes</span></label></div><textarea name="comment" placeholder="Optional comment">${esc(draft.comment||'')}</textarea><button class="submit" type="submit" disabled>Submit and next</button></form><div id="message" class="message">Draft feedback stays in this browser until submitted.</div>`:renderCompleted(f)}</footer>`;root.querySelectorAll('[data-board]').forEach(button=>button.addEventListener('click',()=>{state.boardIndex=Number(button.dataset.board);renderFamily()}));const open=document.getElementById('open-image');if(open)open.addEventListener('click',()=>openImage(f,selected));const form=document.getElementById('review-form');if(form){form.addEventListener('input',saveDraft);form.addEventListener('submit',submitReview);updateSubmit();}renderQueue();}
function renderCompleted(f){const r=f.latestHumanReview||{};const title=f.reviewState==='approved'?'Approved':'Changes requested';const comment=r.comment?`<p>${esc(r.comment)}</p>`:'';return `<div class="reviewed"><div class="reviewed-copy"><strong>${title}</strong>${comment}</div>${pending().length?'<button id="next-pending" class="next" type="button">Next pending</button>':''}</div>`}
function updateSubmit(){const form=document.getElementById('review-form');if(!form)return;form.querySelector('.submit').disabled=!form.querySelector('input[name="decision"]:checked');}
function openImage(f,b){const dialog=document.getElementById('image-dialog');document.getElementById('dialog-title').textContent=`${f.family} · ${b.label}`;const img=document.getElementById('dialog-image');img.src=b.url;img.alt=`${f.family} ${b.label}`;dialog.showModal();}
async function submitReview(event){event.preventDefault();const f=current(),form=event.currentTarget,button=form.querySelector('.submit'),message=document.getElementById('message'),data=new FormData(form);button.disabled=true;button.textContent='Saving';message.className='message';const body={familyId:f.familyId,decision:data.get('decision'),comment:data.get('comment')||'',source:'browser'};try{const response=await fetch('/api/review',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const result=await response.json();if(!response.ok)throw new Error(result.error||'review_not_saved');clearDraft(f.familyId);const nextId=pending().find(item=>item.familyId!==f.familyId)?.familyId;await load(nextId||f.familyId);}catch(error){message.textContent=`Could not save: ${error.message}`;message.className='message error';button.textContent='Submit and next';updateSubmit();}}
async function load(preferredId){const response=await fetch('/api/families',{cache:'no-store'});const data=await response.json();state.families=data.families;document.getElementById('pack-name').textContent=data.packName||'';const visible=reviewable();state.currentId=preferredId&&visible.some(f=>f.familyId===preferredId)?preferredId:(state.currentId&&visible.some(f=>f.familyId===state.currentId)?state.currentId:(pending()[0]||visible[0])?.familyId||null);const remaining=pending().length,done=completed().length;document.getElementById('summary').textContent=`${remaining} remaining · ${done} completed`;renderQueue();renderFamily();}
document.getElementById('dialog-close').addEventListener('click',()=>document.getElementById('image-dialog').close());document.getElementById('image-dialog').addEventListener('click',event=>{if(event.target===event.currentTarget)event.currentTarget.close()});document.addEventListener('click',event=>{if(event.target.id==='next-pending'&&pending()[0])selectFamily(pending()[0].familyId)});document.addEventListener('keydown',event=>{if(event.key==='Escape'&&document.getElementById('image-dialog').open)document.getElementById('image-dialog').close()});load();
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
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/":
            data = HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if route == "/api/families":
            spec = read_json(self.spec_path)
            self.json_response({"packName": spec.get("pack", {}).get("name"), "families": self.list_families()})
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
                ("split-overlay.png", "Adaptive split overlay"),
            ):
                path = validation_root / name
                if path.exists():
                    boards.append({"label": label, "url": f"/files/{path.relative_to(self.pack_root)}"})
            validation = status.get("validation", {})
            human_gate = validation.get("human")
            gates_pass = validation.get("code") == "approved" and validation.get("agent") == "approved"
            if human_gate == "approved":
                review_state = "approved"
            elif human_gate == "rejected":
                review_state = "rejected"
            elif gates_pass:
                review_state = "pending"
            else:
                review_state = "unavailable"
            human_history = [
                entry for entry in status.get("reviewHistory", []) if entry.get("reviewer") == "human"
            ]
            families.append(
                {
                    "family": status.get("family"),
                    "familyId": status.get("familyId"),
                    "status": status.get("status"),
                    "validation": validation,
                    "canReview": gates_pass and review_state == "pending",
                    "reviewState": review_state,
                    "latestHumanReview": human_history[-1] if human_history else None,
                    "selectedRound": selected_round,
                    "assetCount": len(status.get("assets", [])),
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
        source = str(payload.get("source", "browser"))
        user_text = str(payload.get("userText", ""))
        if decision not in ("approve", "reject"):
            raise ValueError("invalid_decision")
        if source not in ("browser", "chat"):
            raise ValueError("invalid_review_source")
        if source == "chat" and not user_text.strip():
            raise ValueError("chat_review_requires_user_text")
        status_path = self.pack_root / "families" / family_id / "family-status.json"
        status = read_json(status_path)
        validation = status.get("validation", {})
        if validation.get("code") != "approved" or validation.get("agent") != "approved":
            raise SystemExit("human_review_requires_code_and_agent_approval")
        if validation.get("human") in ("approved", "rejected"):
            raise SystemExit("human_review_already_recorded")
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
            "source": source,
            "userText": user_text,
            "recordedAt": now(),
            "selectedRound": status.get("selectedRound"),
        }
        status["reviewHistory"] = [*status.get("reviewHistory", []), {"reviewer": "human", **event}]
        pipeline = status.setdefault("pipeline", {})
        pipeline["stage"] = "approved" if decision == "approve" else "human-rejected"
        pipeline.setdefault("timing", {})["humanApprovedAt" if decision == "approve" else "humanRejectedAt"] = event["recordedAt"]
        pipeline["lastError"] = None if decision == "approve" else (comment or "Human review rejected")
        status["updatedAt"] = event["recordedAt"]
        write_json(status_path, status)
        write_approved_manifest(self.pack_root, self.spec_path)
        append_jsonl(self.pack_root / "human-review-log.jsonl", event)
        append_jsonl(
            status_path.parent / "events.jsonl",
            {
                "at": event["recordedAt"],
                "event": "human-reviewed",
                "decision": decision,
                "comment": comment,
                "source": source,
            },
        )
        return {
            "ok": True,
            "familyId": family_id,
            "decision": decision,
            "status": status["status"],
            "recordedAt": event["recordedAt"],
        }


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
