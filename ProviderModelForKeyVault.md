
# Provider Model with Key Vault
Hooray, it's now possible to use the `azure.common.client_factory` module's function `get_client_from_auth_file` with `KeyVaultClient`!

Here's a snippet to show a sample class using this method:

```python
from azure.keyvault import KeyVaultClient
from azure.common.client_factory import get_client_from_auth_file

class KeyVaultConfigProvider(ConfigProvider):
    def __init__(self):
        self._client = get_client_from_auth_file(KeyVaultClient)
        self._vault_url = "https://" + self._key_vault_name + ".vault.azure.net"

    def get_config(self, name: str) -> str:
        # Will raise KeyVaultErrorException: (SecretNotFound) if secret is not found
        return self._client.get_secret(self._vault_url, name, '').value
```

A sample auth file looks like this:

```json
{
       "clientId": "ad735158-65ca-11e7-ba4d-ecb1d756380e",
       "clientSecret": "b70bb224-65ca-11e7-810c-ecb1d756380e",
       "subscriptionId": "bfc42d3a-65ca-11e7-95cf-ecb1d756380e",
       "tenantId": "c81da1d8-65ca-11e7-b1d1-ecb1d756380e",
       "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
       "resourceManagerEndpointUrl": "https://management.azure.com/",
       "activeDirectoryGraphResourceId": "https://graph.windows.net/",
       "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
       "galleryEndpointUrl": "https://gallery.azure.com/",
       "managementEndpointUrl": "https://management.core.windows.net/"
   }
```

which came from the [Microsoft docs](https://docs.microsoft.com/en-us/python/api/azure-common/azure.common.client_factory?view=azure-python) that also includes instructions for generating this file.

Note, the environment variable `AZURE_AUTH_LOCATION` must be setup and pointing to the path of this auth file if not specifying the path as the `auth_path` parameter.

## Providers

The class `KeyVaultConfigProvider` class inherits from the `ConfigProvider` base class. This class ensures that the each implemented provider has the same properties or methods available. 

For instance: 

```python
from abc import ABC

class ConfigProvider(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_config(self, name: str) -> str:
        pass
```

which ensures that each provider in this case has a method `get_config`. 

The concept of providers comes from the [Factory Design Pattern](https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/factory-model-overview). This pattern gives us vocabulary around generating "provider-independent" code or the ability to use the same calls regardless of what is actually being called. 


Another common possible provider is a local env file configuration. 

This may look something like this:
```python

class EnvVarConfigProvider(ConfigProvider):

    def __init__(self):
        super().__init__()

    def get_config(self, name: str) -> str:
        return os.getenv(name, '')
```

and a .env file full of keys and values.

## Putting it all together

Each provider can now be instantiated as needed. To do this, it's possible to place a value in the .env file that will signal which provider to use, `CONFIG_PROVIDER`. In the code snippet below, it contains a list of possible providers, checks which one was selected to use in the configuration, then instantiates the provider or defaults to `EnvVarConfigProvider` if one wasn't provided. This is completed with a single `get` call with no customization for the individual providers. This is kicked off in the `__init__` function that then can call a single `get_config` method for the desired properties also without modifying for each provider. 


```python

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

```

Code samples are available in the `Sample Code` folder. 


## Testing

Setting up some quick unit tests can be beneficial. These can ensure that the code meets a certain level of quality and that the logic performs as expected. 

Thi following test case shows how to instansiate the Config class, provide a sample .env dictionary, and mock the `EnvVarConfigProvider` `get_config` method so that there is no dependency on the os module or file system. Finally, the method asserts that the `Config` object has correctly populated it's properties

```python
    @mock.patch.dict('os.environ',{'CONFIG_PROVIDER':''})
    @mock.patch('SampleCode.config_provider.EnvVarConfigProvider.get_config')
    def test_config(self, mock_get_config):

        mock_get_config.return_value = "my props"

        c = Config('resource_group')

        self.assertEquals(c.prop1, "my props")
        self.assertEquals(c.prop2, "my props")


```

The more interesting testing scenario occurs when working with Key Vault. Since this is a service that requires requests to be made to it, there are many factors involved that may be unwanted when running tests such as a cost per call or a latency in speed. Therefore, it's preferred to mock the calls made those providers. 

The `test_keyvault_key_vault_config` method works almost exactly the same as `test_config` with the addition of the mock for `get_client_from_auth_file` to prevent that call being made to the server. The mock for that is stored in the parameter `mock_get_client_from_auth_file` and there is nothing else needed to do with that variable other than perhaps assert that it was indeed called. Mocking the `get_config` method here also mimics the call that would be made to get a secret from Key Vault. 


## Closing

Tons of material exists on working with Key Vault, unit testing and mocking with Python, the Provider Model or the Factory Design Pattern, etc. These topics have mostly been around for some time now so hopefully this is a nice example of all of these in a combined solution.


Happy hacking!