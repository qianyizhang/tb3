"""Synthetic Harbor launcher for workflow tests; no external process or model."""

import subprocess
from pathlib import Path

from tb3_medical import storage


def fake_harbor(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    config_path = Path(argv[-1])
    config = storage.read(config_path)
    agent = config["agents"][0]["name"]
    phase = {"started_at": "2026-09-20T00:00:00Z", "finished_at": "2026-09-20T00:00:01Z"}
    storage.write_new(
        config_path.parent / "job/trial/result.json",
        {
            **phase,
            "task_name": "task",
            "trial_name": "trial",
            "task_checksum": "a" * 64,
            "config": {"agent": config["agents"][0]},
            "agent_execution": phase,
            "verifier": phase,
            "exception_info": None,
            "verifier_result": {"rewards": {"reward": 1 if agent == "oracle" else 0}},
        },
    )
    return subprocess.CompletedProcess(argv, 0)
