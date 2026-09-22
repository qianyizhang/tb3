"""Discriminating pre-inference lifecycle checks; no Docker or model calls."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone

from guards import validate_dispatch


def main():
    now = datetime.now(timezone.utc)
    queue = {
        "no_further_dispatch": False,
        "order": [
            {"experiment": "first", "state": "ready"},
            {"experiment": "second", "state": "queued_after_first"},
        ],
        "quota_remaining_last_observed_percent": 76,
        "quota_reserve_percent": 20,
        "quota_observed_at": now.isoformat(),
    }
    controls = {"first": {"passed": True}, "second": {"passed": True}}
    setup = {"passed": True}
    validate_dispatch(queue, "first", controls, setup, now)

    def reject(q, c=controls, s=setup, experiment="first"):
        try:
            validate_dispatch(q, experiment, c, s, now)
        except RuntimeError:
            return
        raise AssertionError("Expected dispatch rejection")

    for value in [None, 20, 19]:
        q = deepcopy(queue)
        q["quota_remaining_last_observed_percent"] = value
        reject(q)
    q = deepcopy(queue)
    q["no_further_dispatch"] = True
    reject(q)
    for state in ["running", "terminal_reviewed", "queued_resource_wait"]:
        q = deepcopy(queue)
        q["order"][0]["state"] = state
        reject(q)
    q = deepcopy(queue)
    q["quota_observed_at"] = (now - timedelta(minutes=16)).isoformat()
    reject(q)
    reject(queue, c={"first": {"passed": True}})
    reject(queue, s={"passed": False})
    q = deepcopy(queue)
    q["order"][1]["state"] = "ready"
    reject(q, experiment="second")
    q["order"][0]["state"] = "terminal_reviewed"
    validate_dispatch(q, "second", controls, setup, now)
    print(
        "Passed: first/second dispatch, stop, reserve, unavailable/stale quota, duplicate state, both controls, prior boundary"
    )


if __name__ == "__main__":
    main()
