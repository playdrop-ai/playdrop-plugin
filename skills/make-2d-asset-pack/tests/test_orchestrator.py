from __future__ import annotations

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

from PIL import Image, ImageDraw


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from asset_pack_common import read_json, sha256  # noqa: E402
from process_family import code_failures, source_crop_edge_pixels, source_matte_subject_overlap  # noqa: E402
from process_sheet import finish_chroma_edge, image_metrics, soft_chroma  # noqa: E402


class OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.pack = self.workspace / "pack"
        self.anchor = self.workspace / "anchor.png"
        Image.new("RGB", (64, 64), (20, 120, 220)).save(self.anchor)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, name: str, *arguments: object, expected: int = 0) -> subprocess.CompletedProcess[str]:
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

    def write_request(self, families: list[dict], with_anchor: bool = True, kind: str = "pack") -> Path:
        request = {
            "schemaVersion": 1,
            "kind": kind,
            "id": "orchestrated-pack",
            "name": "Orchestrated Pack",
            "description": "Synthetic orchestration fixture.",
            "style": {
                "description": "Friendly casual mobile game art with bold clean silhouettes.",
                "referenceImages": [
                    {"path": str(self.anchor), "ownership": "creator-owned"}
                ] if with_anchor else [],
            },
            "sourceFolder": None,
            "metadata": {
                "version": "1.0.0",
                "license": "PLAYDROP",
                "visibility": "PRIVATE",
                "publicationRights": "private-only",
                "tags": ["asset-purpose/prop"],
            },
            "families": families,
        }
        path = self.workspace / "request.json"
        path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
        return path

    def family(self, family_id: str, items: list[str]) -> dict:
        return {
            "id": family_id,
            "name": family_id.title(),
            "mode": "paired",
            "columns": 2,
            "matte": "#ff00ff",
            "fallbackMattes": ["#00ff00", "#00ffff"],
            "items": items,
        }

    def make_sheet(self, path: Path, rows: int, matte: tuple[int, int, int], missing: set[int] | None = None) -> Path:
        missing = missing or set()
        cell = 256
        image = Image.new("RGB", (cell * 2, cell * rows), matte)
        draw = ImageDraw.Draw(image)
        colors = [(30, 170, 225), (245, 180, 20), (160, 90, 20), (235, 80, 45)]
        for index in range(rows * 2):
            if index in missing:
                continue
            row, column = divmod(index, 2)
            left = column * cell + 60
            top = row * cell + 60
            right = (column + 1) * cell - 60
            bottom = (row + 1) * cell - 60
            draw.rounded_rectangle((left, top, right, bottom), radius=30, fill=colors[index % len(colors)])
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return path

    def make_single(self, path: Path, matte: tuple[int, int, int]) -> Path:
        image = Image.new("RGB", (256, 256), matte)
        ImageDraw.Draw(image).ellipse((58, 58, 198, 198), fill=(30, 130, 230))
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return path

    def prepare(self, request: Path) -> None:
        self.run_script("prepare_request.py", "--request", request, "--output-root", self.pack)

    def claim_and_ingest(
        self,
        family: str,
        job: str,
        source: Path,
        elapsed: float = 0.25,
        source_review: str = "approve",
    ) -> None:
        self.run_script("claim_job.py", "--pack-root", self.pack, "--family", family, "--job", job, "--worker", "test-worker")
        self.run_script(
            "ingest_generation.py",
            "--pack-root", self.pack,
            "--family", family,
            "--job", job,
            "--status", "success",
            "--output", source,
            "--elapsed-seconds", str(elapsed),
            "--source-review", source_review,
            "--comment", "Synthetic source accepted.",
        )

    def human_approve(self, family: str) -> None:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = int(sock.getsockname()[1])
        process = subprocess.Popen(
            [sys.executable, str(SCRIPTS / "review_server.py"), "--pack-root", str(self.pack), "--port", str(port)],
            cwd=SKILL_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        endpoint = f"http://127.0.0.1:{port}/api/review"
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/families", timeout=0.2)
                break
            except (OSError, urllib.error.URLError):
                time.sleep(0.05)
        try:
            payload = json.dumps({"familyId": family, "decision": "approve", "comment": "Fixture approved."}).encode()
            request = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{port}"},
            )
            with urllib.request.urlopen(request, timeout=2) as response:
                result = json.loads(response.read())
            self.assertEqual(result["status"], "approved")
        finally:
            process.terminate()
            process.communicate(timeout=3)

    def test_text_only_bootstrap_unblocks_parallel_family_jobs(self) -> None:
        request = self.write_request(
            [self.family("seating", ["Chair"]), self.family("lighting", ["Lamp"])],
            with_anchor=False,
        )
        self.prepare(request)
        first = read_json(self.pack / "families/seating/jobs/generation-v1.json")
        second_path = self.pack / "families/lighting/jobs/generation-v1.json"
        self.assertEqual(first["state"], "ready")
        self.assertTrue(first["bootstrapStyle"])
        self.assertEqual(read_json(second_path)["state"], "blocked-style-anchor")
        prompt = (self.pack / first["prompt"]).read_text(encoding="utf-8")
        self.assertIn("There is no visual style reference", prompt)
        self.assertIn("Image 1 is the authoritative identity", prompt)

        source = self.make_sheet(self.workspace / "bootstrap.png", 1, (255, 0, 255))
        self.claim_and_ingest("seating", "generation-v1", source)
        spec = read_json(self.pack / "pack-spec.json")
        self.assertEqual(spec["styleAnchor"]["origin"], "generated-bootstrap")
        self.assertTrue((self.pack / spec["styleAnchor"]["path"]).is_file())
        self.assertEqual(read_json(second_path)["state"], "ready")

        self.run_script(
            "claim_job.py",
            "--pack-root", self.pack,
            "--family", "lighting",
            "--job", "generation-v1",
            "--worker", "worker-two",
        )
        duplicate = self.run_script(
            "claim_job.py",
            "--pack-root", self.pack,
            "--family", "lighting",
            "--job", "generation-v1",
            "--worker", "worker-three",
            expected=1,
        )
        self.assertIn("job_not_ready", duplicate.stderr)

    def test_family_continuity_style_reference_is_portable_and_job_scoped(self) -> None:
        continuity = self.workspace / "seating-continuity.png"
        Image.new("RGB", (64, 64), (240, 170, 30)).save(continuity)
        seating = self.family("seating", ["Chair"])
        seating["styleReferenceImages"] = [
            {"path": str(continuity), "ownership": "creator-owned"}
        ]
        request = self.write_request(
            [seating, self.family("lighting", ["Lamp"])],
        )

        self.prepare(request)

        seating_job = read_json(self.pack / "families/seating/jobs/generation-v1.json")
        lighting_job = read_json(self.pack / "families/lighting/jobs/generation-v1.json")
        self.assertEqual(len(seating_job["styleReferences"]), 2)
        self.assertEqual(len(lighting_job["styleReferences"]), 1)
        self.assertEqual(seating_job["styleReferences"][0], lighting_job["styleReferences"][0])
        self.assertTrue((self.pack / seating_job["styleReferences"][1]).is_file())
        self.assertNotIn(seating_job["styleReferences"][1], lighting_job["styleReferences"])
        seating_prompt = (self.pack / seating_job["prompt"]).read_text(encoding="utf-8")
        lighting_prompt = (self.pack / lighting_job["prompt"]).read_text(encoding="utf-8")
        self.assertIn("Images 1 through 2", seating_prompt)
        self.assertIn("Image 3 is the authoritative identity", seating_prompt)
        self.assertIn("Follow Image 3 exactly", seating_prompt)
        self.assertIn("Image 2 is the authoritative identity", lighting_prompt)

        spec = read_json(self.pack / "pack-spec.json")
        seating_spec = next(family for family in spec["families"] if family["id"] == "seating")
        self.assertEqual(
            seating_spec["continuityStyleReferences"],
            [{"path": seating_job["styleReferences"][1], "ownership": "creator-owned"}],
        )

    def test_routed_extraction_targeted_repair_and_catalogue(self) -> None:
        request = self.write_request([self.family("seating", ["Chair", "Sofa"])], kind="sheet")
        self.prepare(request)
        prepared_job = read_json(self.pack / "families/seating/jobs/generation-v1.json")
        prompt = (self.pack / prepared_job["prompt"]).read_text(encoding="utf-8")
        self.assertIn("Image 1", prompt)
        self.assertIn("Image 2 is the authoritative identity", prompt)
        source = self.make_sheet(self.workspace / "initial.png", 2, (255, 0, 255), missing={1})
        self.claim_and_ingest("seating", "generation-v1", source)
        initial = self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
            expected=1,
        )
        self.assertIn("unresolved:1", initial.stdout)
        status = read_json(self.pack / "families/seating/family-status.json")
        self.assertEqual(status["selectedAssetCount"], 3)
        self.assertEqual(status["status"], "needs-repair")
        repair_id = status["lastAttempt"]["repairJobs"][0]
        self.assertEqual(repair_id, "repair-chair-small-v1")
        repair_job = read_json(self.pack / f"families/seating/jobs/{repair_id}.json")
        self.assertEqual(len(repair_job["styleReferences"]), 2)
        self.assertEqual(repair_job["styleReferences"][-1], prepared_job["output"])
        repair_prompt = (self.pack / repair_job["prompt"]).read_text(encoding="utf-8")
        self.assertIn("Images 1 through 2", repair_prompt)
        self.assertIn("Image 3 is the authoritative identity", repair_prompt)
        preserved = {
            (asset["itemId"], asset["kind"]): asset["outputSha256"]
            for asset in status["assets"]
        }

        repair = self.make_single(self.workspace / "repair.png", (0, 255, 0))
        self.claim_and_ingest("seating", repair_id, repair)
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", repair_id,
            "--methods", "soft-chroma,hard-key",
        )
        repaired = read_json(self.pack / "families/seating/family-status.json")
        self.assertEqual(repaired["status"], "awaiting-codex-review")
        self.assertEqual(repaired["selectedAssetCount"], 4)
        for asset in repaired["assets"]:
            key = (asset["itemId"], asset["kind"])
            if key in preserved:
                self.assertEqual(asset["outputSha256"], preserved[key])

        self.run_script(
            "record_review.py",
            "--status", self.pack / "families/seating/family-status.json",
            "--reviewer", "codex",
            "--decision", "approve",
            "--comment", "Synthetic routed extraction passed.",
        )
        self.human_approve("seating")
        spec_path = self.pack / "pack-spec.json"
        spec = read_json(spec_path)
        spec["pack"]["tags"] = ["synthetic", "asset-purpose/prop"]
        spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        finalized = self.run_script("finalize_pack.py", "--pack-root", self.pack)
        self.assertIn("ignored_noncanonical_tag:synthetic", finalized.stderr)
        catalogue = read_json(self.pack / "catalogue.json")
        self.assertEqual(len(catalogue["assetPacks"][0]["ownedAssets"]), 4)
        self.assertTrue(all(asset["files"]["primary"].endswith(".png") for asset in catalogue["assetPacks"][0]["ownedAssets"]))
        self.assertEqual(catalogue["assetPacks"][0]["tags"], ["asset-purpose/prop"])
        self.assertTrue(all(asset["tags"] == ["asset-purpose/prop"] for asset in catalogue["assetPacks"][0]["ownedAssets"]))
        pack_status = read_json(self.pack / "pack-status.json")
        self.assertEqual(pack_status["status"], "finalized")
        self.assertEqual(pack_status["catalogue"]["ownedAssetCount"], 4)
        self.assertEqual(pack_status["catalogue"]["playdropValidation"], "not-run")
        self.assertIsNotNone(pack_status["timing"]["finalizedAt"])
        summary = self.run_script("status.py", "--pack-root", self.pack, "--json")
        report = json.loads(summary.stdout)
        self.assertEqual(report["summary"]["approved"], 1)
        self.assertIsNotNone(report["families"][0]["elapsedSeconds"])
        self.assertIsNotNone(report["families"][0]["activeElapsedSeconds"])
        self.assertIsNotNone(report["families"][0]["timing"]["queueLatencySeconds"])
        self.assertIsNotNone(report["summary"]["medianActiveSecondsToCodeApproval"])
        self.assertIsNotNone(report["summary"]["medianActiveSecondsToCodexApproval"])
        filtered = self.run_script(
            "status.py", "--pack-root", self.pack, "--families", "seating", "--json"
        )
        self.assertEqual(json.loads(filtered.stdout)["summary"]["familyCount"], 1)

        spec = read_json(spec_path)
        spec["pack"]["visibility"] = "PUBLIC"
        spec["pack"]["publicationRights"] = "private-only"
        spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        blocked = self.run_script("finalize_pack.py", "--pack-root", self.pack, expected=1)
        self.assertIn("publication_rights_not_cleared", blocked.stderr)

    def test_failed_calls_resume_and_generated_sheet_limits(self) -> None:
        request = self.write_request([self.family("seating", ["Chair"])], kind="sheet")
        self.prepare(request)
        status_path = self.pack / "families/seating/family-status.json"

        self.run_script(
            "claim_job.py", "--pack-root", self.pack, "--family", "seating",
            "--job", "generation-v1", "--worker", "failed-provider",
        )
        self.run_script(
            "ingest_generation.py", "--pack-root", self.pack, "--family", "seating",
            "--job", "generation-v1", "--status", "failed", "--error", "provider unavailable",
        )
        ledger = (self.pack / "generation-ledger.csv").read_text(encoding="utf-8")
        self.assertIn("provider unavailable", ledger)
        self.assertEqual(read_json(status_path)["status"], "generation-failed")

        retry_two = self.run_script(
            "prepare_retry.py", "--pack-root", self.pack, "--family", "seating",
            "--reason", "Retry provider failure.",
        )
        self.assertIn("retry_job:generation-v2", retry_two.stdout)
        job_two = read_json(self.pack / "families/seating/jobs/generation-v2.json")
        self.assertEqual(job_two["matte"], "#ff00ff")
        preserved = status_path.read_bytes()
        self.run_script("prepare_request.py", "--request", request, "--output-root", self.pack, "--resume")
        self.assertEqual(status_path.read_bytes(), preserved)

        rejected_two = self.make_sheet(self.workspace / "rejected-two.png", 1, (255, 0, 255))
        self.claim_and_ingest("seating", "generation-v2", rejected_two, source_review="reject")

        retry_three = self.run_script(
            "prepare_retry.py", "--pack-root", self.pack, "--family", "seating",
            "--reason", "Source has a cast shadow.",
        )
        self.assertIn("retry_job:generation-v3", retry_three.stdout)
        job_three = read_json(self.pack / "families/seating/jobs/generation-v3.json")
        self.assertEqual(job_three["matte"], "#00ff00")
        self.assertNotIn("#ff00ff", job_three["fallbackMattes"])
        self.assertEqual(job_three["fallbackMattes"], ["#00ffff"])
        retry_prompt = (self.pack / job_three["prompt"]).read_text(encoding="utf-8")
        self.assertIn("RETRY CORRECTION", retry_prompt)
        self.assertIn("Source has a cast shadow.", retry_prompt)
        rejected_three = self.make_sheet(self.workspace / "rejected-three.png", 1, (0, 255, 0))
        self.claim_and_ingest("seating", "generation-v3", rejected_three, source_review="reject")

        blocked = self.run_script(
            "prepare_retry.py", "--pack-root", self.pack, "--family", "seating",
            "--reason", "Would exceed the generated-source limit.", expected=1,
        )
        self.assertIn("full_sheet_retry_limit_exceeded", blocked.stderr)
        override = self.run_script(
            "prepare_retry.py", "--pack-root", self.pack, "--family", "seating",
            "--reason", "Owner-approved exception.", "--override-limit",
        )
        self.assertIn("retry_job:generation-v4", override.stdout)
        self.assertTrue(read_json(self.pack / "families/seating/jobs/generation-v4.json")["retry"]["limitOverride"])

    def test_sheet_request_rejects_multiple_families(self) -> None:
        request = self.write_request(
            [self.family("seating", ["Chair"]), self.family("lighting", ["Lamp"])],
            kind="sheet",
        )
        result = self.run_script(
            "prepare_request.py", "--request", request, "--output-root", self.pack, expected=1,
        )
        self.assertIn("sheet_request_requires_one_family", result.stderr)

    def test_targeted_batch_retry_caps_columns_to_requested_items(self) -> None:
        family = self.family("seating", ["Chair", "Sofa", "Bench", "Stool"])
        family["columns"] = 4
        request = self.write_request([family], kind="sheet")
        self.prepare(request)

        result = self.run_script(
            "prepare_retry.py", "--pack-root", self.pack, "--family", "seating",
            "--mode", "large", "--items", "chair,sofa", "--matte", "#00ff00",
            "--reason", "Repair two large assets.",
        )

        self.assertIn("retry_job:repair-batch-large-v1", result.stdout)
        job = read_json(self.pack / "families/seating/jobs/repair-batch-large-v1.json")
        self.assertEqual(job["columns"], 2)
        with Image.open(self.pack / job["identityTemplate"]) as template:
            self.assertEqual(template.size, (768, 384))

    def test_human_retry_replaces_payload_and_uses_approved_family_source(self) -> None:
        request = self.write_request([self.family("seating", ["Chair"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "approved-family.png", 1, (255, 0, 255))
        self.claim_and_ingest("seating", "generation-v1", source)
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
        )
        overrides = self.workspace / "payload-overrides.json"
        overrides.write_text(
            json.dumps(
                {
                    "chair": {
                        "large": "One complete throne with one required red cushion and no other objects."
                    }
                }
            ) + "\n",
            encoding="utf-8",
        )

        result = self.run_script(
            "prepare_retry.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--mode", "large",
            "--items", "chair",
            "--payload-overrides", overrides,
            "--reason", "Owner requires the red cushion.",
        )

        self.assertIn("retry_job:repair-chair-large-v1", result.stdout)
        job = read_json(self.pack / "families/seating/jobs/repair-chair-large-v1.json")
        self.assertEqual(len(job["styleReferences"]), 2)
        self.assertEqual(job["retry"]["repairContinuitySourceJobId"], "generation-v1")
        self.assertTrue((self.pack / job["retry"]["payloadOverrides"]).is_file())
        prompt = (self.pack / job["prompt"]).read_text(encoding="utf-8")
        self.assertIn("Images 1 through 2", prompt)
        self.assertIn("Image 3 is the authoritative identity", prompt)
        self.assertIn("One complete throne with one required red cushion", prompt)
        self.assertIn("AUTHORITATIVE RETRY CORRECTION", prompt)
        self.assertIn("overrides any conflicting earlier payload text", prompt)
        template_metadata = read_json(
            self.pack
            / "families/seating/private-templates/repair-chair-large-v1/seating-large-identity-template.json"
        )
        slot = template_metadata["slots"][0]
        self.assertTrue(slot["payloadOverride"])
        self.assertEqual(slot["referenceType"], "semantic-only")
        self.assertIn("required red cushion", slot["payload"])

    def test_matte_hue_fringe_and_source_clipping_are_rejected(self) -> None:
        rgba = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(rgba)
        draw.rectangle((47, 47, 208, 208), fill=(150, 240, 150, 255))
        draw.rectangle((50, 50, 205, 205), fill=(245, 245, 245, 255))
        metrics = image_metrics(rgba, (0, 255, 0))
        self.assertLess(metrics["residualMatteRatioWithin48"], 0.002)
        self.assertGreater(metrics["residualMatteHueRatio"], 0.002)
        self.assertIn("matte_hue_fringe_or_subject_overlap", code_failures(metrics, rgba.size))

        crop = Image.new("RGB", (128, 128), (255, 0, 255))
        ImageDraw.Draw(crop).rectangle((30, 30, 127, 100), fill=(160, 90, 20))
        self.assertGreater(source_crop_edge_pixels(crop, (255, 0, 255)), 2)

    def test_hue_aware_soft_chroma_removes_fringe_but_source_overlap_is_rejected(self) -> None:
        fringe = Image.new("RGB", (128, 128), (0, 255, 0))
        draw = ImageDraw.Draw(fringe)
        draw.ellipse((22, 22, 106, 106), fill=(90, 210, 90))
        draw.ellipse((27, 27, 101, 101), fill=(235, 90, 35))
        extracted = soft_chroma(fringe, (0, 255, 0), 12, 115, True, True)
        metrics = image_metrics(extracted, (0, 255, 0))
        self.assertLessEqual(metrics["residualMatteHueRatio"], 0.002)
        self.assertEqual(metrics["residualMatteRatioWithin48"], 0.0)

        downscaled = extracted.resize((64, 64), Image.Resampling.LANCZOS)
        downscaled_metrics = image_metrics(downscaled, (0, 255, 0))
        finished = finish_chroma_edge(downscaled, (0, 255, 0))
        finished_metrics = image_metrics(finished, (0, 255, 0))
        self.assertLessEqual(finished_metrics["residualMatteHueRatio"], 0.002)
        self.assertLessEqual(
            finished_metrics["residualMatteHuePixels"],
            downscaled_metrics["residualMatteHuePixels"],
        )

        overlapping_subject = Image.new("RGB", (128, 128), (0, 255, 0))
        ImageDraw.Draw(overlapping_subject).rectangle((25, 25, 103, 103), fill=(105, 175, 15))
        overlap = source_matte_subject_overlap(overlapping_subject, (0, 255, 0), 115)
        self.assertTrue(overlap["detectable"])
        self.assertGreater(overlap["ratio"], 0.5)

    def test_systemic_failure_requests_full_sheet_retry_without_item_fanout(self) -> None:
        request = self.write_request([self.family("seating", ["Chair", "Sofa"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "empty.png", 2, (255, 0, 255), missing={0, 1, 2, 3})
        self.claim_and_ingest("seating", "generation-v1", source)
        result = self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
            expected=1,
        )
        self.assertIn("repair_strategy:full-sheet", result.stdout)
        status = read_json(self.pack / "families/seating/family-status.json")
        self.assertEqual(status["status"], "needs-retry")
        self.assertEqual(status["lastAttempt"]["repairStrategy"], "full-sheet")
        self.assertEqual(status["lastAttempt"]["repairJobs"], [])
        self.assertEqual(list((self.pack / "families/seating/jobs").glob("repair-*.json")), [])

    def test_large_small_failures_for_one_item_share_one_paired_repair(self) -> None:
        request = self.write_request([self.family("seating", ["Chair", "Sofa", "Bench"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "overlap.png", 3, (255, 0, 255))
        image = Image.open(source).convert("RGB")
        draw = ImageDraw.Draw(image)
        for column in (0, 1):
            draw.rounded_rectangle(
                (column * 256 + 60, 60, (column + 1) * 256 - 60, 196),
                radius=30,
                fill=(125, 70, 210),
            )
        image.save(source)
        self.claim_and_ingest("seating", "generation-v1", source)
        result = self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
            expected=1,
        )
        self.assertIn("repair_job:repair-chair-paired-v1", result.stdout)
        status = read_json(self.pack / "families/seating/family-status.json")
        self.assertEqual(status["lastAttempt"]["repairJobs"], ["repair-chair-paired-v1"])
        repair = read_json(self.pack / "families/seating/jobs/repair-chair-paired-v1.json")
        self.assertEqual(repair["mode"], "paired")
        self.assertEqual(repair["items"], ["chair"])

    def test_reextract_job_reuses_retained_source_without_consuming_generation_limit(self) -> None:
        request = self.write_request([self.family("seating", ["Chair"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "initial.png", 1, (255, 0, 255))
        self.claim_and_ingest("seating", "generation-v1", source)
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
        )
        result = self.run_script(
            "prepare_reextract.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--from-job", "generation-v1",
            "--reason", "Improved deterministic extractor.",
        )
        self.assertIn("reextract_job:reextract-v1", result.stdout)
        reextract = read_json(self.pack / "families/seating/jobs/reextract-v1.json")
        self.assertEqual(reextract["type"], "reextraction")
        self.assertEqual(reextract["output"], read_json(self.pack / "families/seating/jobs/generation-v1.json")["output"])
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "reextract-v1",
            "--methods", "soft-chroma,hard-key",
        )
        retry = self.run_script(
            "prepare_retry.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--reason", "Generated-source retry after re-extraction.",
        )
        self.assertIn("retry_job:generation-v2", retry.stdout)

    def test_reextract_rejected_source_requires_audited_override(self) -> None:
        request = self.write_request([self.family("seating", ["Chair"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "rejected.png", 1, (255, 0, 255))
        self.claim_and_ingest("seating", "generation-v1", source, source_review="reject")
        denied = self.run_script(
            "prepare_reextract.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--from-job", "generation-v1",
            "--reason", "Diagnostic extraction passed.",
            expected=1,
        )
        self.assertIn("reextract_source_not_approved", denied.stderr)
        accepted = self.run_script(
            "prepare_reextract.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--from-job", "generation-v1",
            "--reason", "Diagnostic extraction passed on all review backgrounds.",
            "--override-source-review",
        )
        self.assertIn("reextract_job:reextract-v1", accepted.stdout)
        reextract = read_json(self.pack / "families/seating/jobs/reextract-v1.json")
        self.assertEqual(reextract["state"], "source-approved")
        self.assertEqual(reextract["sourceReviewOverride"]["scope"], "extraction-only")
        self.assertEqual(reextract["sourceReviewOverride"]["originalDecision"], "reject")

    def test_item_scoped_visual_overrides_are_recorded_and_do_not_apply_by_default(self) -> None:
        request = self.write_request([self.family("seating", ["Chair"])], kind="sheet")
        self.prepare(request)
        source = Image.new("RGB", (512, 256), (255, 0, 255))
        draw = ImageDraw.Draw(source)
        draw.ellipse((70, 60, 190, 196), fill=(100, 0, 100))
        draw.ellipse((326, 60, 446, 196), fill=(100, 0, 100))
        source_path = self.workspace / "hue-overlap.png"
        source.save(source_path)
        self.claim_and_ingest("seating", "generation-v1", source_path)
        rejected = self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
            expected=1,
        )
        self.assertIn("family_requires_repair", rejected.stderr)
        self.run_script(
            "prepare_reextract.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--from-job", "generation-v1",
            "--reason", "Dark magenta chair pixels are verified subject color.",
        )
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "reextract-v1",
            "--methods", "soft-chroma,hard-key",
            "--allow-source-hue-overlap-items", "chair",
            "--allow-matte-warning-items", "chair",
            "--skip-hue-cleanup-items", "chair",
        )
        status = read_json(self.pack / "families/seating/family-status.json")
        self.assertEqual(status["status"], "awaiting-codex-review")
        overrides = status["lastAttempt"]["visualReviewOverrideItems"]
        self.assertEqual(overrides["sourceHueOverlap"], ["chair"])
        self.assertEqual(overrides["outputMatteWarnings"], ["chair"])
        self.assertEqual(overrides["sourceCropEdge"], [])
        self.assertEqual(overrides["forcedHueCleanup"], [])
        self.assertEqual(overrides["skippedHueCleanup"], ["chair"])
        self.assertTrue(all(not asset["finalHueCleanupApplied"] for asset in status["assets"]))

    def test_forced_hue_cleanup_is_item_scoped_audited_and_removes_residue(self) -> None:
        family = self.family("seating", ["Chair"])
        family["matte"] = "#00ff00"
        request = self.write_request([family], kind="sheet")
        self.prepare(request)
        source = Image.new("RGB", (512, 256), (0, 255, 0))
        draw = ImageDraw.Draw(source)
        draw.ellipse((70, 60, 190, 196), fill=(0, 145, 100))
        draw.ellipse((78, 68, 182, 188), fill=(0, 145, 125))
        draw.ellipse((326, 60, 446, 196), fill=(0, 145, 100))
        draw.ellipse((334, 68, 438, 188), fill=(0, 145, 125))
        source_path = self.workspace / "green-overlap.png"
        source.save(source_path)
        self.claim_and_ingest("seating", "generation-v1", source_path)
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma",
            expected=1,
        )
        self.run_script(
            "prepare_reextract.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--from-job", "generation-v1",
            "--reason", "Teal subject remains intact after audited hue cleanup.",
        )
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "reextract-v1",
            "--methods", "soft-chroma",
            "--allow-source-hue-overlap-items", "chair",
            "--force-hue-cleanup-items", "chair",
        )
        status = read_json(self.pack / "families/seating/family-status.json")
        self.assertEqual(status["status"], "awaiting-codex-review")
        self.assertEqual(status["lastAttempt"]["visualReviewOverrideItems"]["forcedHueCleanup"], ["chair"])
        round_metrics = read_json(
            self.pack / "families/seating/extraction-rounds/reextract-v1-routed/metrics.json"
        )
        for attempt in round_metrics["attempts"]:
            self.assertEqual(attempt["residualMatteHuePixels"], 0)

    def test_reextract_supersedes_only_unstarted_repairs_from_source_round(self) -> None:
        request = self.write_request([self.family("seating", ["Chair", "Sofa"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "initial.png", 2, (255, 0, 255), missing={1})
        self.claim_and_ingest("seating", "generation-v1", source)
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
            expected=1,
        )
        source_job = read_json(self.pack / "families/seating/jobs/generation-v1.json")
        self.assertEqual(source_job["result"]["repairJobs"], ["repair-chair-small-v1"])
        result = self.run_script(
            "prepare_reextract.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--from-job", "generation-v1",
            "--reason", "Retry deterministic extraction first.",
        )
        self.assertIn("superseded_jobs:1", result.stdout)
        repair = read_json(self.pack / "families/seating/jobs/repair-chair-small-v1.json")
        self.assertEqual(repair["state"], "superseded")
        self.assertEqual(repair["supersededBy"], "reextract-v1")

    def test_complete_round_supersedes_all_remaining_unstarted_repairs(self) -> None:
        request = self.write_request([self.family("seating", ["Chair", "Sofa"])], kind="sheet")
        self.prepare(request)
        source = self.make_sheet(self.workspace / "initial.png", 2, (255, 0, 255), missing={1})
        self.claim_and_ingest("seating", "generation-v1", source)
        self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v1",
            "--methods", "soft-chroma,hard-key",
            expected=1,
        )
        repair_path = self.pack / "families/seating/jobs/repair-chair-small-v1.json"
        self.assertEqual(read_json(repair_path)["state"], "ready")

        retry = self.run_script(
            "prepare_retry.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--reason", "Use a complete replacement sheet.",
        )
        self.assertIn("retry_job:generation-v2", retry.stdout)
        retry_job = read_json(self.pack / "families/seating/jobs/generation-v2.json")
        retry_matte = tuple(bytes.fromhex(retry_job["matte"].removeprefix("#")))
        complete_source = self.make_sheet(self.workspace / "complete.png", 2, retry_matte)
        self.claim_and_ingest("seating", "generation-v2", complete_source)
        result = self.run_script(
            "process_family.py",
            "--pack-root", self.pack,
            "--family", "seating",
            "--job", "generation-v2",
            "--methods", "soft-chroma,hard-key",
        )
        self.assertIn("superseded_jobs:1", result.stdout)
        repair = read_json(repair_path)
        self.assertEqual(repair["state"], "superseded")
        self.assertEqual(repair["supersededBy"], "generation-v2")

    def test_auto_matte_avoids_reference_color(self) -> None:
        red_reference = self.workspace / "red-chair.png"
        image = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
        ImageDraw.Draw(image).ellipse((10, 10, 86, 86), fill=(255, 0, 0, 255))
        image.save(red_reference)
        family = self.family("seating", [])
        family["matte"] = "auto"
        family.pop("fallbackMattes")
        family["items"] = [
            {
                "name": "Chair",
                "references": {"large": str(red_reference), "small": str(red_reference)},
            }
        ]
        request = self.write_request([family], kind="sheet")
        self.prepare(request)
        spec = read_json(self.pack / "pack-spec.json")
        production = spec["families"][0]["production"]
        self.assertNotEqual(production["matte"], "#ff0000")
        self.assertEqual(production["matteAnalysis"]["selection"], "automatic")
        red = next(score for score in production["matteAnalysis"]["ranking"] if score["matte"] == "#ff0000")
        self.assertGreater(red["conflictRatio"], 0.9)


if __name__ == "__main__":
    unittest.main()
