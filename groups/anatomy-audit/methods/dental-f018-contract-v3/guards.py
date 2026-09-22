"""Pure pre-dispatch checks shared by the v3 operator and its controls."""

from datetime import datetime, timezone


def validate_dispatch(queue, experiment, controls, setup, now=None):
    now = now or datetime.now(timezone.utc)
    if queue.get("no_further_dispatch"):
        raise RuntimeError("The operator has stopped further dispatch")
    order = queue["order"]
    index = next(i for i, item in enumerate(order) if item["experiment"] == experiment)
    if order[index]["state"] != "ready":
        raise RuntimeError("This experiment is not ready for dispatch")
    if any(item["state"] != "terminal_reviewed" for item in order[:index]):
        raise RuntimeError("Earlier experiment requires terminal boundary review")
    if not setup.get("passed") or any(
        not controls.get(item["experiment"], {}).get("passed") for item in order
    ):
        raise RuntimeError("Both condition controls must pass before dispatch")
    remaining = queue.get("quota_remaining_last_observed_percent")
    if remaining is None or remaining <= queue["quota_reserve_percent"]:
        raise RuntimeError("Account reserve exhausted or unavailable")
    observed = datetime.fromisoformat(queue["quota_observed_at"])
    age = (now - observed).total_seconds()
    if not 0 <= age <= 900:
        raise RuntimeError("Refresh account quota before dispatch")
