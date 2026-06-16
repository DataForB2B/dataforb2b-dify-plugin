from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import db2b_request


class TypeaheadTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        type_ = tool_parameters.get("type")
        q = tool_parameters.get("q")
        if not type_:
            raise ValueError("'type' is required.")
        if not q:
            raise ValueError("'q' (query) is required.")

        limit = int(tool_parameters.get("limit") or 20)
        limit = max(1, min(limit, 20))

        params = {"type": type_, "q": q, "limit": limit}
        data = db2b_request(
            self.runtime.credentials, "GET", "/typeahead", params=params
        )

        results = data.get("results", []) or []
        values = [r.get("value") for r in results if r.get("value")]
        yield self.create_text_message(
            f"{len(results)} suggestion(s) for {type_}: " + ", ".join(values)
            if values
            else f"No suggestions found for {type_} = '{q}'."
        )
        yield self.create_json_message(data)
