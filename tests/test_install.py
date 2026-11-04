import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sha = lambda value: hashlib.sha256(value).hexdigest()


class InstallerChecks(unittest.TestCase):
    def run_installer(self, script, mode):
        with patch.object(sys, "argv", [str(script), mode]), contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(script), run_name="__main__")

    def test_install_restore_and_unknown_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("tools", "output", "inputs", "payload", "game"):
                (root / name).mkdir()
            original, replacement = b"original fixture", b"replacement fixture"
            target, backup, patched = root / "game/portrait.bundle", root / "payload/original", root / "payload/replacement"
            target.write_bytes(original); backup.write_bytes(original); patched.write_bytes(replacement)
            record = dict(source=str(target), backup=str(backup), patched=str(patched), original_sha256=sha(original), patched_sha256=sha(replacement), previous_sha256=sha(original))
            (root / "output/install-record.json").write_text(json.dumps(record))
            script = root / "tools/install_or_restore.py"
            shutil.copy2(REPO / "tools/install_or_restore.py", script)
            self.run_installer(script, "install")
            self.assertEqual(target.read_bytes(), replacement)
            self.run_installer(script, "restore")
            self.assertEqual(target.read_bytes(), original)
            target.write_bytes(b"unknown version")
            with self.assertRaises(AssertionError):
                self.run_installer(script, "install")
            self.assertEqual(target.read_bytes(), b"unknown version")

    def test_bad_payload_is_rejected_without_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("tools", "output", "inputs", "payload", "game"):
                (root / name).mkdir()
            original = b"original fixture"
            target, backup, patched = root / "game/portrait.bundle", root / "payload/original", root / "payload/replacement"
            target.write_bytes(original); backup.write_bytes(original); patched.write_bytes(b"tampered")
            record = dict(source=str(target), backup=str(backup), patched=str(patched), original_sha256=sha(original), patched_sha256=sha(b"expected replacement"), previous_sha256=sha(original))
            (root / "output/install-record.json").write_text(json.dumps(record))
            script = root / "tools/install_or_restore.py"
            shutil.copy2(REPO / "tools/install_or_restore.py", script)
            with self.assertRaises(AssertionError):
                self.run_installer(script, "install")
            self.assertEqual(target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
