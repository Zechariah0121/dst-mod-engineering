"""Package drift cannot mask damage to the independently committed old cache.

Reuse the authored tiny hydration fixture. Its rebind/original-KB guard stubs
remain explicit; activation, runtime manifest/files and package checks are real.
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'dst-kb-service'))
import prepare_sources as prepare
import run_kb as launcher
import test_public_source_bootstrap as bootstrap_fixtures
from dst_kb import public_catalog


class PackageDriftCacheIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.fixture=bootstrap_fixtures.BootstrapTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.build([self.fixture.current,self.fixture.historical])
        self.root=self.fixture.root
        self.config,self.build=prepare.prepared_runtime(self.root)

    def drift(self):
        path=self.root/'run_kb.py'
        path.write_bytes(path.read_bytes()+b'\n# authored package drift fixture\n')

    def failure(self,expected):
        with self.assertRaises(prepare.PreparationError) as caught:
            prepare.prepared_runtime(self.root)
        self.assertEqual(caught.exception.code,expected)

    def test_healthy_cache_and_changed_package_reports_only_package_drift(self):
        self.drift();self.failure('PACKAGE_CHANGED')

    def test_runtime_file_damage_without_package_drift_fails_closed(self):
        (self.build/'knowledge/evidence.json').write_bytes(b'{}\n')
        self.failure('RUNTIME_CHANGED')

    def test_manifest_damage_without_package_drift_fails_closed(self):
        path=self.build/'RUNTIME-MANIFEST.json';path.write_bytes(path.read_bytes()+b' ')
        self.failure('RUNTIME_CHANGED')

    def test_package_drift_plus_runtime_file_damage_is_runtime_error(self):
        self.drift()
        (self.build/'knowledge/evidence.json').write_bytes(b'{}\n')
        self.failure('RUNTIME_CHANGED')

    def test_package_drift_plus_manifest_damage_is_runtime_error(self):
        self.drift()
        path=self.build/'RUNTIME-MANIFEST.json';path.write_bytes(path.read_bytes()+b' ')
        self.failure('RUNTIME_CHANGED')

    def test_added_public_module_does_not_expand_old_runtime_file_set(self):
        path=self.root/'dst-kb-service/new_public_module.py'
        path.write_text('# authored new package module\n',encoding='utf-8')
        self.assertFalse((self.build/'dst-kb-service/new_public_module.py').exists())
        self.failure('PACKAGE_CHANGED')

    def test_removed_public_required_input_is_package_error_not_cache_error(self):
        (self.root/'run_kb.py').unlink()
        self.failure('PACKAGE_INCOMPLETE')

    def test_invalid_activation_path_is_not_masked_by_package_drift(self):
        self.drift()
        value=json.loads(self.config.read_bytes())
        value['prepared_runtime']['runtime_build']='builds/../../outside'
        prepare.write(self.config,value)
        self.failure('INVALID_PATH')

    def test_auto_launcher_never_falls_back_for_combined_damage(self):
        self.drift()
        (self.build/'knowledge/evidence.json').write_bytes(b'{}\n')
        stdout,stderr=io.StringIO(),io.StringIO()
        with patch.object(launcher,'prepared_runtime',side_effect=lambda _root:prepare.prepared_runtime(self.root)), \
                patch.object(public_catalog,'main') as catalog,contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            result=launcher.main(['status','--mode','auto'])
        self.assertEqual(result,2)
        self.assertEqual(json.loads(stderr.getvalue())['error']['code'],'RUNTIME_CHANGED')
        catalog.assert_not_called()


if __name__=='__main__':unittest.main(verbosity=2)
