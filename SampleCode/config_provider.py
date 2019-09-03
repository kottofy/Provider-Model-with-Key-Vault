
import os
import json
import logging
from abc import ABC, abstractmethod
from azure.keyvault import KeyVaultClient
from azure.common.client_factory import get_client_from_auth_file


class ConfigProvider(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_config(self, name: str) -> str:
        pass


class EnvVarConfigProvider(ConfigProvider):

    def __init__(self, resource_group=None):
        super().__init__()

    def get_config(self, name: str) -> str:
        return os.getenv(name, '')


class KeyVaultConfigProvider(ConfigProvider):

    def __init__(self, resource_group):
        super().__init__()
        self._key_vault_name = os.getenv("KEY_VAULT_NAME")
        self._vault_url = "https://" + self._key_vault_name + ".vault.azure.net"
        self._client = get_client_from_auth_file(KeyVaultClient)


    def get_config(self, name: str) -> str:
        # Will raise KeyVaultErrorException: (SecretNotFound) if secret is not found
        return self._client.get_secret(self._vault_url, name, '').value
