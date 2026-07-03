"""Pytest configuration and fixtures for Pulumi tests."""

# ruff: noqa: E402
import importlib
import importlib.util
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PULUMI_DIR = os.path.join(PROJECT_ROOT, "pulumi")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# Also add the pulumi/ dir itself so bare imports like `from config import …`
# inside the local modules resolve correctly.
if PULUMI_DIR not in sys.path:
    sys.path.insert(1, PULUMI_DIR)

# Stub third-party Pulumi provider packages BEFORE importing local modules
sys.modules["pulumi_ibm_kms_module"] = MagicMock()
sys.modules["pulumi_ibm_rg_module"] = MagicMock()
sys.modules["pulumi_ibm_cos_module"] = MagicMock()
sys.modules["pulumi_wx_discovery"] = MagicMock()
sys.modules["pulumi_ibm"] = MagicMock()


# 3. Stub the Pulumi SDK core module.

mock_pulumi = MagicMock()
mock_config = MagicMock()
mock_config.get = MagicMock(return_value=None)
mock_pulumi.Config = MagicMock(return_value=mock_config)
mock_pulumi.export = MagicMock()
mock_pulumi.log = MagicMock()
mock_pulumi.log.warn = MagicMock()
sys.modules["pulumi"] = mock_pulumi


_tim_spec = importlib.util.spec_from_file_location(
    "pulumi.terraform_ibm_modules",
    os.path.join(PULUMI_DIR, "terraform_ibm_modules", "__init__.py"),
    submodule_search_locations=[os.path.join(PULUMI_DIR, "terraform_ibm_modules")],
)
assert _tim_spec is not None, (
    "Could not locate pulumi/terraform_ibm_modules/__init__.py"
)
terraform_ibm_modules = importlib.util.module_from_spec(_tim_spec)
sys.modules["pulumi.terraform_ibm_modules"] = terraform_ibm_modules
mock_pulumi.terraform_ibm_modules = terraform_ibm_modules
assert _tim_spec.loader is not None, "ModuleSpec has no loader"
_tim_spec.loader.exec_module(terraform_ibm_modules)


from pulumi.terraform_ibm_modules.key_protect import create_kms_instance
from pulumi.terraform_ibm_modules.object_storage import (
    configure_public_access,
    create_cos_instance,
    upload_static_files,
)
from pulumi.terraform_ibm_modules.resource_group import create_resource_group
from pulumi.terraform_ibm_modules.watson_discovery import create_watson_discovery


class TestMain(unittest.TestCase):
    @patch("terraform_ibm_modules.watson_discovery.create_watson_discovery")
    @patch("terraform_ibm_modules.object_storage.configure_bucket_website")
    @patch("terraform_ibm_modules.object_storage.upload_static_files")
    @patch("terraform_ibm_modules.object_storage.configure_public_access")
    @patch("terraform_ibm_modules.object_storage.create_cos_instance")
    @patch("terraform_ibm_modules.resource_group.create_resource_group")
    @patch("pulumi.export")
    def test_main_flow(
        self,
        mock_export,
        mock_rg,
        mock_cos,
        mock_public,
        mock_upload,
        mock_website,
        mock_wd,
    ):
        # Setup mock return values
        mock_rg.return_value = MagicMock(resource_group_name="test-rg")
        mock_cos_instance = MagicMock()
        mock_cos_instance.bucket_name = "test-bucket"
        mock_cos_instance.cos_instance_name = "test-cos"
        mock_cos_instance.bucket_crn = MagicMock()
        mock_cos_instance.bucket_crn.apply = MagicMock(return_value="test-crn")
        mock_cos.return_value = mock_cos_instance

        mock_wd_instance = MagicMock()
        mock_wd_instance.id = "wd-id"
        mock_wd_instance.dashboard_url = "https://dashboard.url"
        mock_wd.return_value = mock_wd_instance

        # Import the __main__ module from parent directory
        import os
        import sys

        pulumi_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "pulumi",
        )
        sys.path.insert(0, pulumi_dir)

        # Import and execute main
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "__main__", os.path.join(pulumi_dir, "__main__.py")
        )
        if spec is not None and spec.loader is not None:
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)

        # Verify all functions were called
        self.assertTrue(mock_rg.called)
        self.assertTrue(mock_cos.called)
        self.assertTrue(mock_public.called)
        self.assertTrue(mock_upload.called)
        self.assertTrue(mock_website.called)
        self.assertTrue(mock_wd.called)
        self.assertTrue(mock_export.called)


class TestResourceGroup(unittest.TestCase):
    @patch("pulumi.terraform_ibm_modules.resource_group.rgmod.Module")
    @patch(
        "pulumi.terraform_ibm_modules.resource_group.EXISTING_RESOURCE_GROUP",
        "existing-rg",
    )
    def test_existing_resource_group(self, mock_module):

        rg = create_resource_group()

        mock_module.assert_called_once_with(
            "resource_group",
            existing_resource_group_name="existing-rg",
        )
        self.assertEqual(rg, mock_module.return_value)

    @patch("pulumi.terraform_ibm_modules.resource_group.rgmod.Module")
    @patch("pulumi.terraform_ibm_modules.resource_group.EXISTING_RESOURCE_GROUP", None)
    @patch("pulumi.terraform_ibm_modules.resource_group.PREFIX", "test")
    @patch("pulumi.terraform_ibm_modules.resource_group.NEW_RG_NAME", "rg")
    def test_new_resource_group(self, mock_module):

        create_resource_group()

        mock_module.assert_called_once_with(
            "resource_group",
            resource_group_name="test-rg",
        )


class TestKMS(unittest.TestCase):
    @patch("pulumi.terraform_ibm_modules.key_protect.ibm_kms_module.Module")
    @patch("pulumi.terraform_ibm_modules.key_protect.PREFIX", "test")
    @patch("pulumi.terraform_ibm_modules.key_protect.REGION", "us-south")
    @patch("pulumi.terraform_ibm_modules.key_protect.KMS_KEYS", {"mock": "key"})
    @patch("pulumi.terraform_ibm_modules.key_protect.KP_NAME", "kp")
    def test_create_kms_instance(self, mock_module):
        rg = MagicMock()
        rg.resource_group_id = "rg-id"

        kms = create_kms_instance(rg)

        mock_module.assert_called_once_with(
            "pulumi-key-protect",
            resource_group_id="rg-id",
            key_protect_instance_name="test-kp",
            region="us-south",
            keys=[{"mock": "key"}],
        )

        self.assertEqual(kms, mock_module.return_value)


class TestCOSInstance(unittest.TestCase):
    @patch(
        "pulumi.terraform_ibm_modules.object_storage.generate_suffix",
        return_value="abcd",
    )
    @patch("pulumi.terraform_ibm_modules.object_storage.cosmod.Module")
    @patch("pulumi.terraform_ibm_modules.object_storage.PREFIX", "test")
    @patch("pulumi.terraform_ibm_modules.object_storage.REGION", "us-south")
    @patch("pulumi.terraform_ibm_modules.object_storage.BUCKET_NAME", "bucket")
    @patch("pulumi.terraform_ibm_modules.object_storage.COS_INSTANCE_NAME", "cos")
    def test_create_cos_instance(self, mock_module, *_):

        rg = MagicMock()
        rg.resource_group_id = "rg-id"

        cos = create_cos_instance(rg)

        mock_module.assert_called_once()
        self.assertEqual(cos, mock_module.return_value)

    @patch(
        "pulumi.terraform_ibm_modules.object_storage.os.path.isdir", return_value=False
    )
    @patch("pulumi.terraform_ibm_modules.object_storage.pulumi.log.warn")
    def test_upload_static_files_no_dir(self, mock_warn, _):
        upload_static_files(MagicMock())
        mock_warn.assert_called_once()

    @patch("pulumi.terraform_ibm_modules.object_storage.ibm.IamAccessGroupPolicy")
    @patch("pulumi.terraform_ibm_modules.object_storage.ibm.get_iam_access_group")
    def test_configure_public_access(self, mock_get_group, mock_policy):
        mock_group = MagicMock()
        mock_group.groups = [MagicMock(id="group-id")]
        mock_get_group.return_value = mock_group

        cos = MagicMock()
        cos.cos_instance_guid.apply = MagicMock()
        cos.bucket_name.apply = MagicMock()

        configure_public_access(cos)

        mock_policy.assert_called_once()


class TestWatsonDiscovery(unittest.TestCase):
    @patch("pulumi.terraform_ibm_modules.watson_discovery.wxd_mod.Module")
    @patch("pulumi.terraform_ibm_modules.watson_discovery.PREFIX", "test")
    @patch("pulumi.terraform_ibm_modules.watson_discovery.WATSON_DISCOVERY_NAME", "wd")
    def test_create_watson_discovery(self, mock_module):

        rg = MagicMock()
        rg.resource_group_id = "rg-id"

        wd = create_watson_discovery(rg)

        mock_module.assert_called_once_with(
            "wd",
            resource_group_id="rg-id",
            watson_discovery_name="test-wd",
        )

        self.assertEqual(wd, mock_module.return_value)
