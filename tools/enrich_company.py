from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import db2b_request


class EnrichCompanyTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        identifier = tool_parameters.get("company_identifier")
        if not identifier:
            raise ValueError("'company_identifier' is required.")

        payload = {"company_identifier": identifier}
        data = db2b_request(self.runtime.credentials, "POST", "/enrich/company", payload)
        yield self.create_json_message(data)
