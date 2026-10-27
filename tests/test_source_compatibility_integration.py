"""Execute proposed launcher/catalog code in memory against read-only real public data."""
import contextlib
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
import source_compatibility as compat
import catalog_fallback_policy as policy
import test_source_compatibility as fixtures

REPO = HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "dst-kb-service"))
import prepare_sources


def module(name, path, text):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__package__ = name.rpartition(".")[0]
    exec(compile(text, str(path), "exec"), value.__dict__)
    return value


class PatchIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposed = {name: (REPO / name).read_text(encoding='utf-8') for name in ('run_kb.py', 'dst-kb-service/dst_kb/public_catalog.py')}
        cls.launcher = module("proposed_run_kb", REPO / "run_kb.py", cls.proposed["run_kb.py"])
        name = "dst-kb-service/dst_kb/public_catalog.py"
        cls.catalog = module("dst_kb.public_catalog", REPO / name, cls.proposed[name])

    def run_launcher(self, arguments, error=None):
        aliases = {"scripts.source_compatibility": compat, "scripts.catalog_fallback_policy": policy,
                   "dst_kb.public_catalog": self.catalog}
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(sys.modules, aliases), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if error:
                with patch.object(self.launcher, "prepared_runtime", side_effect=error):
                    code = self.launcher.main(arguments)
            else:
                code = self.launcher.main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_auto_package_upgrade_serves_verified_public_catalog(self):
        code, out, err = self.run_launcher(["status"], prepare_sources.PreparationError("PACKAGE_CHANGED", "synthetic package upgrade"))
        self.assertEqual(code, 0, err)
        value = json.loads(out)
        self.assertEqual(value["records"], json.loads((REPO / "knowledge/CATALOG.json").read_bytes())["counts"]["total"])
        self.assertEqual(value["availability_fallback"]["reason_code"], "PACKAGE_CHANGED")
        self.assertFalse(value["coding_context_delivered"])

    def test_full_package_upgrade_stays_error(self):
        code, _, err = self.run_launcher(["status", "--mode", "full"], prepare_sources.PreparationError("PACKAGE_CHANGED", "fixture"))
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["error"]["code"], "PACKAGE_CHANGED")

    def test_corrupt_runtime_stays_error(self):
        code, _, err = self.run_launcher(["status"], prepare_sources.PreparationError("RUNTIME_CHANGED", "fixture"))
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["error"]["code"], "RUNTIME_CHANGED")

    def test_existing_catalog_mode_still_validates_187_records(self):
        code, out, err = self.run_launcher(["status", "--mode", "catalog"])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["records"], json.loads((REPO / "knowledge/CATALOG.json").read_bytes())["counts"]["total"])

    def test_mcp_initialize_surfaces_fallback_reason(self):
        server = self.catalog.PublicCatalog(REPO)
        self.addCleanup(server.close)
        notice = policy.catalog_fallback("auto", "PACKAGE_CHANGED", REPO)
        server.availability_fallback = notice
        server.instructions += " Availability fallback: " + json.dumps(notice)
        result = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertIn("PACKAGE_CHANGED", result["result"]["instructions"])
        self.assertEqual(len(server.tools), 2)

    def test_single_maintenance_entry_precedes_prepared_runtime(self):
        fixture = fixtures.CompatibilityTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        with patch.object(self.launcher, "prepared_runtime", side_effect=AssertionError("must not prepare sources")):
            code, out, err = self.run_launcher(["maintain-sources", "locate", "--target", str(fixture.old.path), "--symbol", "Producer"])
        self.assertEqual(code, 0, err)
        self.assertTrue(json.loads(out)["matches"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
