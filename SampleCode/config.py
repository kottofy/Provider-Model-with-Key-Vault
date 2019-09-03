
import os

from .config_provider import \
    EnvVarConfigProvider, KeyVaultConfigProvider


class Config:

    def __init__(self, resource_group):
        config_prov = Config.__get_config_prov(resource_group)
        self.prop1 = config_prov.get_config("PROP1")
        self.prop2 = config_prov.get_config("PROP2")

    @classmethod
    def __get_config_prov(cls, resource_group):

        __config_providers = {
            "envvar": EnvVarConfigProvider,
            "keyvault": KeyVaultConfigProvider
        }

        config_prov_name = os.getenv("CONFIG_PROVIDER")

        config_prov_cls = __config_providers.get(config_prov_name, EnvVarConfigProvider)

        return config_prov_cls(resource_group)
