from __future__ import annotations

import csv
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from asset_pack_common import read_json, sha256  # noqa: E402
from process_sheet import remove_tiny_components, soft_chroma  # noqa: E402


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "synthetic-pack"
        self.root.mkdir(parents=True)
        self.family_root = self.root / "families" / "seating"
        self.anchor = self.root / "style-anchor" / "anchor.png"
        self.anchor.parent.mkdir(parents=True)
        Image.new("RGB", (64, 64), (20, 120, 220)).save(self.anchor)
        self.spec = self.root / "pack-spec.json"
        self.write_spec()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_spec(self, rights: str = "private-only") -> None:
        self.spec.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "pack": {"id": "synthetic-pack", "name": "Synthetic Pack", "publicationRights": rights},
                    "styleAnchor": {
                        "path": "style-anchor/anchor.png",
                        "ownership": "creator-owned",
                        "stylePrompt": "Friendly casual mobile game asset with a bold clean silhouette.",
                    },
                    "variants": {
                        "large": {"width": 128, "height": 128, "padding": 10, "contract": "detailed perspective"},
                        "small": {"width": 64, "height": 64, "padding": 6, "contract": "simple front icon"},
                    },
                    "retryLimits": {
                        "fullSheetsPerFamilyMaximum": 2,
                        "individualRepairsPerAssetMaximum": 2,
                    },
                    "families": [
                        {
                            "id": "seating",
                            "name": "Seating",
                            "items": [
                                {
                                    "id": "chair",
                                    "name": "Chair",
                                    "referenceType": "semantic-only",
                                    "payloads": {
                                        "large": "one complete three-quarter chair",
                                        "small": "one complete front-facing simplified chair",
                                    },
                                }
                            ],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def run_script(self, name: str, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPTS / name), *map(str, arguments)]
        result = subprocess.run(
            command,
            cwd=SKILL_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            expected,
            f"command: {' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def make_inputs(self, mode: str, label: str, items: bool = False) -> tuple[Path, Path]:
        template_dir = self.family_root / "private-templates" / label
        prompt = self.family_root / "prompts" / f"{label}.txt"
        item_args = ["--items", "chair"] if items else []
        self.run_script(
            "build_template.py",
            "--spec", self.spec,
            "--family", "seating",
            "--mode", mode,
            *item_args,
            "--output-dir", template_dir,
        )
        template = template_dir / f"seating-{mode}-identity-template.png"
        self.run_script(
            "build_prompt.py",
            "--spec", self.spec,
            "--family", "seating",
            "--mode", mode,
            *item_args,
            "--matte", "#ff00ff",
            "--output", prompt,
        )
        return template, prompt

    def make_sheet(self, path: Path, mode: str, variant: int, empty: bool = False) -> Path:
        slots = 2 if mode == "paired" else 1
        cell = 256
        image = Image.new("RGB", (cell * slots, cell), (255, 0, 255))
        if not empty:
            draw = ImageDraw.Draw(image)
            colors = [(20 + variant * 7, 180, 220), (245, 180 - variant * 5, 20)]
            for index in range(slots):
                left = index * cell + 54 + variant
                top = 54 + variant
                right = (index + 1) * cell - 54
                bottom = cell - 54
                draw.rounded_rectangle((left, top, right, bottom), radius=28, fill=colors[index % len(colors)])
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return path

    def process(
        self,
        source: Path,
        template: Path,
        prompt: Path,
        round_name: str,
        mode: str = "paired",
        items: bool = False,
        override: bool = False,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        extras = []
        if items:
            extras.extend(["--items", "chair"])
        if override:
            extras.append("--override-limit")
        return self.run_script(
            "process_sheet.py",
            "--spec", self.spec,
            "--family", "seating",
            "--mode", mode,
            *extras,
            "--source", source,
            "--prompt", prompt,
            "--identity-template", template,
            "--matte", "#ff00ff",
            "--method", "soft-chroma",
            "--round", round_name,
            "--output-root", self.root,
            expected=expected,
        )

    def codex_approve(self) -> None:
        self.run_script(
            "record_review.py",
            "--status", self.family_root / "family-status.json",
            "--reviewer", "codex",
            "--decision", "approve",
            "--comment", "Synthetic review passed.",
        )

    def start_review_server(self) -> tuple[subprocess.Popen[str], int]:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = int(sock.getsockname()[1])
        process = subprocess.Popen(
            [sys.executable, str(SCRIPTS / "review_server.py"), "--pack-root", str(self.root), "--port", str(port)],
            cwd=SKILL_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        url = f"http://127.0.0.1:{port}/api/families"
        for _ in range(50):
            try:
                with urllib.request.urlopen(url, timeout=0.2) as response:
                    self.assertEqual(response.status, 200)
                return process, port
            except (OSError, urllib.error.URLError):
                time.sleep(0.05)
        stdout, stderr = process.communicate(timeout=2)
        self.fail(f"review server did not start\nstdout:{stdout}\nstderr:{stderr}")

    def human_decision(self, decision: str = "approve", test_csrf: bool = False, via_chat: bool = False) -> None:
        process, port = self.start_review_server()
        endpoint = f"http://127.0.0.1:{port}/api/review"
        payload = json.dumps({"familyId": "seating", "decision": decision, "comment": "Human fixture review."}).encode()
        try:
            if test_csrf:
                bad = urllib.request.Request(
                    endpoint,
                    data=payload,
                    headers={"Content-Type": "application/json", "Origin": "http://example.invalid"},
                )
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(bad, timeout=2)
                self.assertEqual(caught.exception.code, 403)
            if via_chat:
                result = self.run_script(
                    "relay_human_review.py",
                    "--server", f"http://127.0.0.1:{port}",
                    "--family", "seating",
                    "--decision", decision,
                    "--comment", "Human fixture review.",
                    "--user-text", f"I explicitly {decision} seating.",
                )
                self.assertIn(f"decision:{decision}", result.stdout)
            else:
                request = urllib.request.Request(
                    endpoint,
                    data=payload,
                    headers={"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{port}"},
                )
                with urllib.request.urlopen(request, timeout=2) as response:
                    result = json.loads(response.read())
                self.assertEqual(result["status"], "approved" if decision == "approve" else "human-rejected")
        finally:
            process.terminate()
            process.communicate(timeout=3)

    def initial_approval(self) -> tuple[str, str]:
        template, prompt = self.make_inputs("paired", "paired-v1")
        source = self.make_sheet(self.family_root / "generated" / "paired-v1.png", "paired", 1)
        self.process(source, template, prompt, "paired-v1")
        self.codex_approve()
        self.human_decision(test_csrf=True)
        approved = self.family_root / "approved"
        return sha256(approved / "chair-large.png"), sha256(approved / "chair-small.png")

    def test_review_queue_reports_history_and_rejects_duplicate_decision(self) -> None:
        self.initial_approval()
        process, port = self.start_review_server()
        base_url = f"http://127.0.0.1:{port}"
        try:
            with urllib.request.urlopen(f"{base_url}/api/families", timeout=2) as response:
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                payload = json.loads(response.read())
            family = payload["families"][0]
            self.assertEqual(family["reviewState"], "approved")
            self.assertFalse(family["canReview"])
            self.assertEqual(family["latestHumanReview"]["decision"], "approve")
            self.assertEqual(family["assetCount"], 2)

            duplicate = urllib.request.Request(
                f"{base_url}/api/review",
                data=json.dumps(
                    {"familyId": "seating", "decision": "approve", "comment": "Duplicate."}
                ).encode(),
                headers={"Content-Type": "application/json", "Origin": base_url},
            )
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(duplicate, timeout=2)
            self.assertEqual(caught.exception.code, 409)
            error = json.loads(caught.exception.read())
            self.assertEqual(error["error"], "human_review_already_recorded")

            with urllib.request.urlopen(base_url, timeout=2) as response:
                html = response.read().decode()
            self.assertIn("Submit and next", html)
            self.assertIn("asset-pack-review-draft", html)
        finally:
            process.terminate()
            process.communicate(timeout=3)

    def test_end_to_end_repair_preservation_and_manifest(self) -> None:
        large_v1, small_v1 = self.initial_approval()
        self.assertTrue((self.root / "approved-manifest.json").is_file())

        human_cli = self.run_script(
            "record_review.py",
            "--status", self.family_root / "family-status.json",
            "--reviewer", "human",
            "--decision", "approve",
            expected=2,
        )
        self.assertIn("invalid choice", human_cli.stderr)

        template, prompt = self.make_inputs("small", "small-repair-v1", items=True)
        repair = self.make_sheet(self.family_root / "generated" / "small-repair-v1.png", "small", 3)
        self.process(repair, template, prompt, "small-repair-v1", mode="small", items=True)
        status = read_json(self.family_root / "family-status.json")
        selected = {(asset["itemId"], asset["kind"]): asset for asset in status["assets"]}
        self.assertEqual(selected[("chair", "large")]["outputSha256"], large_v1)
        self.assertNotEqual(selected[("chair", "small")]["outputSha256"], small_v1)
        self.assertEqual(status["validation"]["human"], "pending")
        self.assertIn("lastApprovedAssets", status)

        self.codex_approve()
        self.human_decision(via_chat=True)
        human_events = [json.loads(line) for line in (self.root / "human-review-log.jsonl").read_text().splitlines()]
        self.assertEqual(human_events[-1]["source"], "chat")
        self.assertEqual(human_events[-1]["userText"], "I explicitly approve seating.")
        approved = self.family_root / "approved"
        self.assertEqual(sha256(approved / "chair-large.png"), large_v1)
        self.assertNotEqual(sha256(approved / "chair-small.png"), small_v1)
        archive = self.family_root / "approval-history" / small_v1[:12] / "chair-small.png"
        self.assertTrue(archive.is_file())
        self.assertEqual(sha256(archive), small_v1)

        self.run_script(
            "verify_approved_manifest.py",
            "--manifest", self.root / "approved-manifest.json",
            "--root", self.root,
            "--spec", self.spec,
            "--expected-count", "2",
        )

        status_before = read_json(self.family_root / "family-status.json")
        selected_before = [asset["outputSha256"] for asset in status_before["assets"]]
        failed = self.make_sheet(self.family_root / "generated" / "small-repair-v2.png", "small", 4, empty=True)
        self.process(failed, template, prompt, "small-repair-v2", mode="small", items=True, expected=1)
        status_after = read_json(self.family_root / "family-status.json")
        self.assertEqual([asset["outputSha256"] for asset in status_after["assets"]], selected_before)
        self.assertEqual(status_after["status"], "approved")
        self.assertEqual(status_after["lastAttempt"]["code"], "rejected")
        self.assertEqual(status_after["validation"]["human"], "approved")

        third = self.make_sheet(self.family_root / "generated" / "small-repair-v3.png", "small", 5)
        blocked = self.process(third, template, prompt, "small-repair-v3", mode="small", items=True, expected=1)
        self.assertIn("item_repair_retry_limit_exceeded", blocked.stderr)
        self.process(third, template, prompt, "small-repair-v3-override", mode="small", items=True, override=True)
        overridden = read_json(self.family_root / "family-status.json")
        self.assertTrue(overridden["lastAttempt"]["limitOverride"])

    def test_full_sheet_limit_counts_distinct_sources(self) -> None:
        template, prompt = self.make_inputs("paired", "paired")
        first = self.make_sheet(self.family_root / "generated" / "paired-1.png", "paired", 1)
        second = self.make_sheet(self.family_root / "generated" / "paired-2.png", "paired", 2)
        third = self.make_sheet(self.family_root / "generated" / "paired-3.png", "paired", 3)
        self.process(first, template, prompt, "paired-1")
        self.process(first, template, prompt, "paired-1-hard-key", expected=0)
        self.process(second, template, prompt, "paired-2")
        blocked = self.process(third, template, prompt, "paired-3", expected=1)
        self.assertIn("full_sheet_retry_limit_exceeded", blocked.stderr)
        self.assertFalse((self.family_root / "extraction-rounds" / "paired-3").exists())
        self.process(third, template, prompt, "paired-3-override", override=True)
        status = read_json(self.family_root / "family-status.json")
        self.assertTrue(status["lastAttempt"]["limitOverride"])

    def test_ledger_paths_failures_and_publication_rights(self) -> None:
        template, prompt = self.make_inputs("paired", "ledger")
        source = self.make_sheet(self.family_root / "generated" / "ledger.png", "paired", 1)
        ledger = self.root / "generation-ledger.csv"
        common = [
            "--ledger", ledger,
            "--family", "seating",
            "--mode", "paired",
            "--prompt", prompt,
            "--style-anchor", self.anchor,
            "--identity-template", template,
        ]
        self.run_script("record_generation.py", *common, "--attempt", "1", "--status", "success", "--output", source)
        self.run_script(
            "record_generation.py",
            *common,
            "--attempt", "2",
            "--status", "failed",
            "--error", "synthetic provider failure",
        )
        with ledger.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["status"] for row in rows], ["success", "failed"])
        for row in rows:
            for field in ("prompt", "style_anchor", "identity_template", "output"):
                self.assertFalse(row[field].startswith("/"))
        private = self.run_script("validate_spec.py", "--spec", self.spec)
        self.assertIn("warning:publication_blocked:private-only", private.stdout)
        public = self.run_script("validate_spec.py", "--spec", self.spec, "--for-publication", expected=1)
        self.assertIn("publication_rights_not_cleared", public.stdout)

    def test_manifest_rejects_unexpected_approved_png(self) -> None:
        self.initial_approval()
        self.run_script(
            "verify_pack.py",
            "--spec", self.spec,
            "--pack-root", self.root,
            "--family", "seating",
        )
        publication = self.run_script(
            "verify_pack.py",
            "--spec", self.spec,
            "--pack-root", self.root,
            "--family", "seating",
            "--for-publication",
            expected=1,
        )
        self.assertIn("publication_rights_not_cleared", publication.stdout)
        orphan = self.family_root / "approved" / "orphan.png"
        Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(orphan)
        family_check = self.run_script(
            "verify_pack.py",
            "--spec", self.spec,
            "--pack-root", self.root,
            "--family", "seating",
            expected=1,
        )
        self.assertIn("unexpected_approved_file", family_check.stdout)
        result = self.run_script(
            "verify_approved_manifest.py",
            "--manifest", self.root / "approved-manifest.json",
            "--root", self.root,
            "--spec", self.spec,
            expected=1,
        )
        self.assertIn("unexpected_approved_file", result.stdout)

    def test_magenta_despill_suppresses_both_spill_channels(self) -> None:
        image = Image.new("RGB", (1, 1), (220, 40, 210))
        result = np.asarray(soft_chroma(image, (255, 0, 255), 10, 300, True))
        self.assertGreater(int(result[0, 0, 3]), 0)
        self.assertLess(int(result[0, 0, 3]), 255)
        self.assertEqual(tuple(int(value) for value in result[0, 0, :3]), (40, 40, 40))

    def test_neutral_matte_skips_despill_without_failing(self) -> None:
        image = Image.new("RGB", (1, 1), (40, 40, 40))
        result = np.asarray(soft_chroma(image, (0, 0, 0), 10, 100, True))
        self.assertGreater(int(result[0, 0, 3]), 0)
        self.assertLess(int(result[0, 0, 3]), 255)
        self.assertEqual(tuple(int(value) for value in result[0, 0, :3]), (40, 40, 40))

    def test_tiny_component_cleanup_removes_only_disconnected_junk(self) -> None:
        image = Image.new("RGBA", (8, 4), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 2, 2), fill=(255, 0, 0, 255))
        draw.point((7, 3), fill=(255, 0, 0, 255))
        result = np.asarray(remove_tiny_components(image, minimum_pixels=2))
        self.assertEqual(int(result[1, 1, 3]), 255)
        self.assertEqual(int(result[3, 7, 3]), 0)


if __name__ == "__main__":
    unittest.main()
