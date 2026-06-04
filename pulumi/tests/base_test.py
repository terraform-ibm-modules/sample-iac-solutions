import sys
import os
from unittest.mock import MagicMock

# Add pulumi/ to PYTHONPATH
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---- Stub Pulumi core module ----
mock_pulumi = MagicMock()
mock_config = MagicMock()
mock_config.get = MagicMock(return_value=None)
mock_pulumi.Config = MagicMock(return_value=mock_config)
mock_pulumi.export = MagicMock()
mock_pulumi.log = MagicMock()
mock_pulumi.log.warn = MagicMock()
sys.modules["pulumi"] = mock_pulumi

# ---- Stub Pulumi provider modules ----
sys.modules["pulumi_ibm_kms_module"] = MagicMock()
sys.modules["pulumi_ibm_rg_module"] = MagicMock()
sys.modules["pulumi_ibm_cos_module"] = MagicMock()
sys.modules["pulumi_wx_discovery"] = MagicMock()
sys.modules["pulumi_ibm"] = MagicMock()