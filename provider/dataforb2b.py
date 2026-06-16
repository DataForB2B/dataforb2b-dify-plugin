from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.client import db2b_request


class DataForB2BProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate the API key with a credit-free call to GET /account."""
        try:
            data = db2b_request(credentials, "GET", "/account")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

        if not data.get("valid", False):
            raise ToolProviderCredentialValidationError(
                "DataForB2B reported the API key as invalid."
            )
