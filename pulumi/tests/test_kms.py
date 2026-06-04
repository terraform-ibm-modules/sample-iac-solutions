import unittest
from unittest.mock import MagicMock, patch


class TestKMS(unittest.TestCase):
    @patch("terraform_ibm_modules.key_protect.ibm_kms_module.Module")
    @patch("terraform_ibm_modules.key_protect.PREFIX", "test")
    @patch("terraform_ibm_modules.key_protect.REGION", "us-south")
    @patch("terraform_ibm_modules.key_protect.KMS_KEYS", {"mock": "key"})
    @patch("terraform_ibm_modules.key_protect.KP_NAME", "kp")
    def test_create_kms_instance(self, mock_module):
        from terraform_ibm_modules.key_protect import create_kms_instance

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
