from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import db2b_request

ENRICH_FLAGS = (
    "enrich_profile",
    "enrich_work_email",
    "enrich_personal_email",
    "enrich_phone",
    "enrich_github",
)


class EnrichProfileTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        identifier = tool_parameters.get("profile_identifier")
        if not identifier:
            raise ValueError("'profile_identifier' is required.")

        payload: dict[str, Any] = {"profile_identifier": identifier}
        any_flag = False
        for flag in ENRICH_FLAGS:
            value = bool(tool_parameters.get(flag, False))
            payload[flag] = value
            any_flag = any_flag or value

        # The API requires at least one enrich_* flag — default to full profile.
        if not any_flag:
            payload["enrich_profile"] = True

        data = db2b_request(self.runtime.credentials, "POST", "/enrich/profile", payload)
        yield self.create_json_message(data)
