from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import db2b_request, parse_json_param


class ReasoningSearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query = tool_parameters.get("query")
        session_id = tool_parameters.get("session_id")
        answers = parse_json_param(tool_parameters.get("answers"), "answers")

        if not query and not (session_id and answers):
            raise ValueError(
                "Provide 'query' (first call) or 'session_id' + 'answers' (to resolve a "
                "needs_input turn)."
            )

        payload: dict[str, Any] = {}
        if query:
            payload["query"] = query
        if session_id:
            payload["session_id"] = session_id
        if answers is not None:
            payload["answers"] = answers

        payload["category"] = tool_parameters.get("category") or "people"
        payload["max_results"] = int(tool_parameters.get("max_results") or 25)
        payload["enrich_live"] = bool(tool_parameters.get("enrich_live", False))

        data = db2b_request(
            self.runtime.credentials, "POST", "/search/reasoning", payload
        )

        status = data.get("status")
        if status == "needs_input":
            questions = data.get("questions") or []
            lines = [
                "The agent needs clarification before searching. "
                f"Reply by calling reasoning_search again with session_id="
                f"\"{data.get('session_id')}\" and an answers object.",
            ]
            for q in questions:
                suggestions = q.get("suggestions") or []
                hint = f" (suggestions: {', '.join(map(str, suggestions))})" if suggestions else ""
                lines.append(f"- [{q.get('id')}] {q.get('text')}{hint}")
            yield self.create_text_message("\n".join(lines))
        else:
            yield self.create_text_message(
                f"{data.get('total', 0)} results "
                f"(returned {data.get('count', 0)}, "
                f"{data.get('credits_used', 0)} credits used)."
            )

        yield self.create_json_message(data)
