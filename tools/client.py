"""Shared HTTP client and helpers for the DataForB2B Dify plugin."""
import json
from typing import Any, Optional

import requests

BASE_URL = "https://api.dataforb2b.ai"
DEFAULT_TIMEOUT = 120


def _api_key(credentials: dict[str, Any]) -> str:
    api_key = (credentials or {}).get("api_key")
    if not api_key:
        raise ValueError(
            "DataForB2B API key is missing. Add it in the plugin credentials."
        )
    return api_key


def db2b_request(
    credentials: dict[str, Any],
    method: str,
    path: str,
    payload: Optional[dict] = None,
    params: Optional[dict] = None,
) -> dict:
    """Call the DataForB2B API and return the parsed JSON body.

    `payload` is sent as a JSON body (POST); `params` as the query string (GET).
    Raises ValueError with a readable message on auth/HTTP errors so the
    message surfaces cleanly in the Dify UI.
    """
    headers = {"api_key": _api_key(credentials), "Content-Type": "application/json"}
    url = f"{BASE_URL}{path}"

    resp = requests.request(
        method.upper(),
        url,
        headers=headers,
        json=payload,
        params=params,
        timeout=DEFAULT_TIMEOUT,
    )

    if resp.status_code == 401:
        raise ValueError("Invalid or missing DataForB2B API key (401 unauthorized).")
    if resp.status_code == 403:
        raise ValueError(
            "This API key does not have permission for this resource (403 forbidden)."
        )

    if resp.status_code >= 400:
        # Surface the API's error body when available.
        detail = resp.text
        try:
            body = resp.json()
            detail = body.get("error") or body.get("message") or detail
        except Exception:
            pass
        raise ValueError(f"DataForB2B API error ({resp.status_code}): {detail}")

    return resp.json()


def parse_json_param(value: Any, name: str) -> Optional[Any]:
    """Accept either a parsed object or a JSON string for object parameters."""
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for '{name}': {e}")
    return value


def to_number(value: Any) -> Optional[float]:
    """Coerce a string/number param into int or float; None if empty/invalid."""
    if value is None or value == "":
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def to_bool(value: Any) -> Optional[bool]:
    """Coerce a yes/no/true/false select value into a bool; None if unset."""
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("true", "yes", "1"):
        return True
    if s in ("false", "no", "0"):
        return False
    return None


def add_condition(conditions: list, column: str, op: str, value: Any) -> None:
    """Append a {column, type, value} condition unless the value is empty."""
    if value is None or value == "":
        return
    conditions.append({"column": column, "type": op, "value": value})


def merge_advanced_filters(conditions: list, advanced: Any) -> None:
    """Merge an advanced filter group/list (from JSON) into the AND conditions.

    - A FilterGroup with op "and" has its conditions flattened in.
    - A FilterGroup with op "or" (or any nested group) is appended as a nested group.
    - A bare list of conditions is extended in.
    """
    if not advanced:
        return
    if isinstance(advanced, dict):
        if advanced.get("op", "and") == "and" and isinstance(advanced.get("conditions"), list):
            conditions.extend(advanced["conditions"])
        else:
            conditions.append(advanced)
    elif isinstance(advanced, list):
        conditions.extend(advanced)


def coerce_scalar(value: Any) -> Any:
    """Coerce a filter value string into bool/number when it clearly is one."""
    if isinstance(value, (int, float, bool)):
        return value
    s = str(value).strip()
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return s


def build_slot_condition(column: Any, operator: Any, raw: Any) -> Optional[dict]:
    """Build one filter condition from a generic slot (column, operator, value).

    Returns None when the slot is empty (so it is skipped).
    - `in`      -> value is a comma-separated list
    - `between` -> value is "min,max" (two comma-separated values)
    - `like`    -> raw string kept as-is (text pattern)
    - others    -> single value, coerced to bool/number when applicable
    """
    if not column or raw is None or str(raw).strip() == "":
        return None
    op = (str(operator).strip() if operator else "=") or "="

    if op == "in":
        items = [x.strip() for x in str(raw).split(",") if x.strip()]
        if not items:
            return None
        return {"column": column, "type": "in", "value": [coerce_scalar(x) for x in items]}

    if op == "between":
        parts = [x.strip() for x in str(raw).split(",") if x.strip()]
        if len(parts) < 2:
            raise ValueError(
                f"Operator 'between' on '{column}' needs two comma-separated values, e.g. 3,7"
            )
        return {
            "column": column,
            "type": "between",
            "value": coerce_scalar(parts[0]),
            "value2": coerce_scalar(parts[1]),
        }

    if op == "like":
        return {"column": column, "type": "like", "value": str(raw)}

    return {"column": column, "type": op, "value": coerce_scalar(raw)}


def finalize_filters(conditions: list, match: Any, advanced: Any) -> Optional[dict]:
    """Combine slot conditions (with AND/OR) and optional advanced JSON filters."""
    op = (str(match).strip().lower() if match else "and")
    if op not in ("and", "or"):
        op = "and"

    group = {"op": op, "conditions": conditions} if conditions else None

    if advanced:
        if isinstance(advanced, dict) and "conditions" in advanced:
            adv = advanced
        elif isinstance(advanced, list):
            adv = {"op": "and", "conditions": advanced}
        else:  # a single bare condition dict
            adv = {"op": "and", "conditions": [advanced]}
        return {"op": "and", "conditions": [group, adv]} if group else adv

    return group
