import unittest
from unittest.mock import MagicMock, patch


class TestCOSInstance(unittest.TestCase):
    @patch("terraform_ibm_modules.object_storage.generate_suffix", return_value="abcd")
    @patch("terraform_ibm_modules.object_storage.cosmod.Module")
    @patch("terraform_ibm_modules.object_storage.PREFIX", "test")
    @patch("terraform_ibm_modules.object_storage.REGION", "us-south")
    @patch("terraform_ibm_modules.object_storage.BUCKET_NAME", "bucket")
    @patch("terraform_ibm_modules.object_storage.COS_INSTANCE_NAME", "cos")
    def test_create_cos_instance(self, mock_module, *_):
        from terraform_ibm_modules.object_storage import create_cos_instance

        rg = MagicMock()
        rg.resource_group_id = "rg-id"

        cos = create_cos_instance(rg)

        mock_module.assert_called_once()
        self.assertEqual(cos, mock_module.return_value)

    @patch("terraform_ibm_modules.object_storage.os.path.isdir", return_value=False)
    @patch("terraform_ibm_modules.object_storage.pulumi.log.warn")
    def test_upload_static_files_no_dir(self, mock_warn, _):
        from terraform_ibm_modules.object_storage import upload_static_files

        upload_static_files(MagicMock())
        mock_warn.assert_called_once()

    @patch("terraform_ibm_modules.object_storage.ibm.IamAccessGroupPolicy")
    @patch("terraform_ibm_modules.object_storage.ibm.get_iam_access_group")
    def test_configure_public_access(self, mock_get_group, mock_policy):
        from terraform_ibm_modules.object_storage import configure_public_access

        mock_group = MagicMock()
        mock_group.groups = [MagicMock(id="group-id")]
        mock_get_group.return_value = mock_group

        cos = MagicMock()
        cos.cos_instance_guid.apply = MagicMock()
        cos.bucket_name.apply = MagicMock()

        configure_public_access(cos)

        mock_policy.assert_called_once()
