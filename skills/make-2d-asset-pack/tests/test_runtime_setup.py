#!/usr/bin/env python3

from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import setup_runtime  # noqa: E402


class RuntimeSetupTests(unittest.TestCase):
    def test_runtime_setup_rechecks_after_acquiring_shared_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "venv-v1"
            expected_python = setup_runtime.runtime_python(root)
            with patch.object(setup_runtime, "check", side_effect=[False, True]) as check, \
                    patch.object(setup_runtime, "exclusive_file_lock", return_value=nullcontext()) as lock, \
                    patch.object(setup_runtime, "resolve_bootstrap_python") as bootstrap:
                actual_python = setup_runtime.prepare_runtime(root)

            self.assertEqual(actual_python, expected_python)
            self.assertEqual(check.call_count, 2)
            lock.assert_called_once_with(
                root.parent / ".venv-v1.setup.lock",
                timeout_seconds=setup_runtime.RUNTIME_SETUP_LOCK_TIMEOUT_SECONDS,
                stale_seconds=setup_runtime.RUNTIME_SETUP_LOCK_STALE_SECONDS,
            )
            bootstrap.assert_not_called()


if __name__ == "__main__":
    unittest.main()
