import unittest
from unittest.mock import patch, MagicMock


class TestResourceGroup(unittest.TestCase):

    @patch("terraform_ibm_modules.resource_group.rgmod.Module")
    @patch("terraform_ibm_modules.resource_group.EXISTING_RESOURCE_GROUP", "existing-rg")
    def test_existing_resource_group(self, mock_module):
        from terraform_ibm_modules.resource_group import create_resource_group

        rg = create_resource_group()

        mock_module.assert_called_once_with(
            "resource_group",
            existing_resource_group_name="existing-rg",
        )
        self.assertEqual(rg, mock_module.return_value)

    @patch("terraform_ibm_modules.resource_group.rgmod.Module")
    @patch("terraform_ibm_modules.resource_group.EXISTING_RESOURCE_GROUP", None)
    @patch("terraform_ibm_modules.resource_group.PREFIX", "test")
    @patch("terraform_ibm_modules.resource_group.NEW_RG_NAME", "rg")
    def test_new_resource_group(self, mock_module):
        from terraform_ibm_modules.resource_group import create_resource_group

        create_resource_group()

        mock_module.assert_called_once_with(
            "resource_group",
            resource_group_name="test-rg",
        )