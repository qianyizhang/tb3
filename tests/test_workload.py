"""Synthetic source-to-report accounting for the local workload adapter."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tb3_medical import workload


class WorkloadTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.root = self.base / "tb3"
        self.root.mkdir()
        self.home = self.base / "codex"
        (self.home / "sessions").mkdir(parents=True)
        self.rates = self.base / "rates.json"
        self.rates.write_text(
            json.dumps(
                {
                    "schema": "tb3-workload-rates-v1",
                    "basis": "API Standard equivalent",
                    "source": "https://example.test/prices",
                    "checked_at": "2026-09-23",
                    "long_context_threshold_input_tokens": 272000,
                    "models": {
                        "gpt-6-astra": {
                            "input": 10,
                            "cached_input": 1,
                            "cache_write": 12.5,
                            "output": 50,
                            "long_input": 20,
                            "long_cached_input": 2,
                            "long_cache_write": 25,
                            "long_output": 75,
                        },
                        "gpt-6-sol": {
                            "input": 2,
                            "cached_input": 0.2,
                            "cache_write": 2.5,
                            "output": 10,
                            "long_input": 4,
                            "long_cached_input": 0.4,
                            "long_cache_write": 5,
                            "long_output": 15,
                        },
                    },
                }
            )
        )

    def test_cost_buckets_long_context_and_unpriced(self):
        rates = workload._read_json(self.rates)
        usage = {
            "input_tokens": 1000,
            "cached_input_tokens": 200,
            "cache_write_input_tokens": 20,
            "output_tokens": 50,
        }
        self.assertEqual(
            workload._price(rates, "gpt-6-astra", usage), (0.01075, "API Standard estimate")
        )
        long_usage = {**usage, "input_tokens": 300000}
        self.assertEqual(workload._price(rates, "gpt-6-astra", long_usage)[0], 6.00025)
        self.assertEqual(
            workload._price(rates, "codex-auto-review", usage), (None, "unpriced model")
        )
        self.assertTrue(
            workload._belongs_to_repo(
                {
                    "cwd": "/tmp/worktrees/abcd/tb3",
                    "git": {"repository_url": "https://github.com/example/tb3.git"},
                },
                self.root,
                "git@github.com:example/tb3.git",
            )
        )

    def test_report_links_sources_and_keeps_missing_usage_visible(self):
        session_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        trace = self.home / "sessions" / "rollout-example.jsonl"
        records = [
            {
                "type": "session_meta",
                "payload": {
                    "id": session_id,
                    "cwd": str(self.root),
                    "timestamp": "2026-09-21T23:00:00Z",
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "last_token_usage": {
                            "input_tokens": 1000,
                            "cached_input_tokens": 200,
                            "cache_write_input_tokens": 20,
                            "output_tokens": 50,
                        }
                    },
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "custom_tool_call",
                    "name": "functions.exec",
                    "input": "private command",
                },
            },
        ]
        data = [json.dumps(item).encode() + b"\n" for item in records]
        trace.write_bytes(b"".join(data))
        (self.home / "session_index.jsonl").write_text(
            json.dumps({"id": session_id, "thread_name": "Curate source dataset"}) + "\n"
        )
        source_id = workload._tracker_source_id(trace)
        database = self.base / "tracker.sqlite3"
        connection = sqlite3.connect(database)
        connection.executescript(
            "CREATE TABLE sources(source_id TEXT);"
            "CREATE TABLE model_calls(source_id TEXT,event_at TEXT,model TEXT,effort TEXT,input_tokens INTEGER,cached_input_tokens INTEGER,output_tokens INTEGER,source_offset INTEGER,duplicate_state TEXT);"
            "CREATE TABLE tool_calls(source_id TEXT,tool_name TEXT,tool_category TEXT);"
            "CREATE TABLE threads(thread_id TEXT);"
            "CREATE TABLE generations(generation INTEGER);"
        )
        connection.execute("INSERT INTO sources VALUES (?)", (source_id,))
        connection.execute(
            "INSERT INTO model_calls VALUES (?,?,?,?,?,?,?,?,?)",
            (
                source_id,
                "2026-09-22T01:00:00Z",
                "gpt-6-astra",
                "high",
                1000,
                200,
                50,
                len(data[0]),
                "canonical",
            ),
        )
        connection.execute(
            "INSERT INTO tool_calls VALUES (?,?,?)", (source_id, "functions.exec", "tool")
        )
        connection.execute(
            "INSERT INTO model_calls VALUES (?,?,?,?,?,?,?,?,?)",
            (
                source_id,
                "2026-09-22T01:00:00Z",
                "gpt-6-astra",
                "high",
                1000,
                200,
                50,
                len(data[0]),
                "excluded_copy",
            ),
        )
        connection.commit()
        connection.close()
        result_dir = self.root / ".local" / "attempts" / "attempt-test" / "job" / "task__one"
        result_dir.mkdir(parents=True)
        (result_dir / "result.json").write_text(
            json.dumps(
                {
                    "task_name": "test",
                    "finished_at": "2026-09-22T05:00:00Z",
                    "agent_info": {"model_info": {"name": "gpt-6-sol"}},
                    "config": {"agent": {"kwargs": {"reasoning_effort": "medium"}}},
                    "agent_result": {
                        "n_input_tokens": None,
                        "n_cache_tokens": None,
                        "n_output_tokens": None,
                    },
                }
            )
        )
        output = self.base / "output"
        report = workload.build_report(
            self.root,
            self.home,
            database,
            self.rates,
            None,
            output,
            "Asia/Shanghai",
            "http://127.0.0.1:8765",
        )
        self.assertEqual(report["coverage"]["codex_trace_files"], 1)
        self.assertEqual(report["coverage"]["med_results"], 1)
        self.assertEqual(report["coverage"]["excluded_duplicate_calls"], 1)
        self.assertEqual(report["totals"]["total_tokens"], 1050)
        self.assertEqual(report["totals"]["cost_usd"], 0.01075)
        session = next(row for row in report["sessions"] if row["source"] == "codex")
        self.assertEqual(session["purpose"], "curate_data")
        self.assertEqual(session["days"], ["2026-09-22"])
        self.assertEqual(session["slices"]["2026-09-22||gpt-6-astra / high"]["total_tokens"], 1050)
        self.assertIn("?session=", session["trace_url"])
        self.assertEqual(report["tools"][0]["calls"], 1)
        self.assertNotIn("private command", (output / "report.json").read_text())
        self.assertEqual(report["coverage"]["med_without_trace"], 1)


if __name__ == "__main__":
    unittest.main()
