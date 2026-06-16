from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import (
    db2b_request,
    parse_json_param,
    build_slot_condition,
    finalize_filters,
)

NUM_SLOTS = 5


class SearchPeopleTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        p = tool_parameters

        conditions: list[dict] = []
        for i in range(1, NUM_SLOTS + 1):
            cond = build_slot_condition(
                p.get(f"filter_{i}_column"),
                p.get(f"filter_{i}_operator"),
                p.get(f"filter_{i}_value"),
            )
            if cond:
                conditions.append(cond)

        advanced = parse_json_param(p.get("advanced_filters"), "advanced_filters")
        filters = finalize_filters(conditions, p.get("match"), advanced)

        if not filters:
            raise ValueError(
                "Provide at least one filter slot (column + value) or advanced_filters."
            )

        payload = {
            "filters": filters,
            "count": int(p.get("count") or 25),
            "offset": int(p.get("offset") or 0),
            "enrich_live": bool(p.get("enrich_live", False)),
        }

        data = db2b_request(self.runtime.credentials, "POST", "/search/people", payload)

        total = data.get("total", 0)
        results = data.get("results", []) or []
        count = data.get("count", len(results))
        yield self.create_text_message(
            f"Found {total} matching people (returned {count})."
        )
        yield self.create_json_message(data)
