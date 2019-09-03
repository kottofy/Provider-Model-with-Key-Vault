import unittest
from unittest import mock
from .config import Config


class TestKeyVaultConfig(unittest.TestCase):

    @mock.patch.dict('os.environ', {'CONFIG_PROVIDER': 'keyvault', 'KEY_VAULT_NAME':'mykeyvaultname'}, clear=True)
    @mock.patch('SampleCode.config_provider.KeyVaultConfigProvider.get_config')
    @mock.patch('SampleCode.config_provider.get_client_from_auth_file')
    def test_keyvault_key_vault_config(
            self,
            mock_get_client_from_auth_file,
            mock_get_config
                ):

        mock_get_config.return_value = "my prop"

        c = Config('resource_group')
        self.assertEquals(c.prop1, "my prop")
        self.assertEquals(c.prop2, "my prop")
