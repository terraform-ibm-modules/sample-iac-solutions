import unittest
from unittest.mock import patch, MagicMock


class TestWatsonDiscovery(unittest.TestCase):

    @patch("terraform_ibm_modules.watson_discovery.wxd_mod.Module")
    @patch("terraform_ibm_modules.watson_discovery.PREFIX", "test")
    @patch("terraform_ibm_modules.watson_discovery.WATSON_DISCOVERY_NAME", "wd")
    def test_create_watson_discovery(self, mock_module):
        from terraform_ibm_modules.watson_discovery import create_watson_discovery

        rg = MagicMock()
        rg.resource_group_id = "rg-id"

        wd = create_watson_discovery(rg)

        mock_module.assert_called_once_with(
            "wd",
            resource_group_id="rg-id",
            watson_discovery_name="test-wd",
        )

        self.assertEqual(wd, mock_module.return_value)
