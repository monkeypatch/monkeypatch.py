import json
from typing import Any, Dict



class APIManager(object):
    """
    A class to manage the API providers for the language models.
    Does conditional importing of the API providers.
    """

    def __init__(self,
                 ) -> None:
        self.api_providers = {}

    def  __getitem__(self,
                 provider: str) -> Any:
        if provider not in self.api_providers:
            self.add_api_provider(provider)
        
        return self.api_providers[provider]

    def keys(self):
        """
        Returns the keys of the API providers.
        """
        return self.api_providers.keys()

    def add_api_provider(self, provider):
        """
        Adds an API provider to the API manager.
        """
        if provider =="openai":
            try:
                from tanuki.language_models.openai_api import OpenAI_API
                self.api_providers[provider] = OpenAI_API()
            except ImportError:
                raise Exception(f"You need to install the Tanuki {provider} package to use the {provider} api provider")
        elif provider == "llama_bedrock":
            try:
                from tanuki.language_models.Llama_bedrock_api import LLama_Bedrock_API
                self.api_providers[provider] = LLama_Bedrock_API()
            except ImportError:
                raise Exception(f"You need to install the Tanuki {provider} package to use the {provider} api provider")
        else:
            raise Exception(f"Provider {provider} is not supported")

