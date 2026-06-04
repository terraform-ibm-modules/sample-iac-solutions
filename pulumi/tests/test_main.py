import unittest
from unittest.mock import patch, MagicMock


class TestMain(unittest.TestCase):

    @patch("terraform_ibm_modules.watson_discovery.create_watson_discovery")
    @patch("terraform_ibm_modules.object_storage.configure_bucket_website")
    @patch("terraform_ibm_modules.object_storage.upload_static_files")
    @patch("terraform_ibm_modules.object_storage.configure_public_access")
    @patch("terraform_ibm_modules.object_storage.create_cos_instance")
    @patch("terraform_ibm_modules.resource_group.create_resource_group")
    @patch("pulumi.export")
    def test_main_flow(self, mock_export, mock_rg, mock_cos, mock_public, mock_upload, mock_website, mock_wd):
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
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        # Import and execute main
        import importlib.util
        spec = importlib.util.spec_from_file_location("__main__", os.path.join(parent_dir, "__main__.py"))
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
