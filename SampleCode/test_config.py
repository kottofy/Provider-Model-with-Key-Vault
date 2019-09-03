import unittest
from .config import Config
from unittest import mock


class TestConfig(unittest.TestCase):

    @mock.patch.dict('os.environ',{'CONFIG_PROVIDER':''})
    @mock.patch('SampleCode.config_provider.EnvVarConfigProvider.get_config')
    def test_config(self, mock_get_config):

        mock_get_config.return_value = "my props"

        c = Config('resource_group')

        self.assertEquals(c.prop1, "my props")
        self.assertEquals(c.prop2, "my props")
