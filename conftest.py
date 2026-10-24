import json
import pytest
from app import create_app
from database import init_db

@pytest.fixture(scope="session")
def app():
    # Force reseed database for clean test environment
    init_db(force_reseed=True)
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

def pytest_report_teststatus(report, config):
    # Suppress progress characters (.F)
    return report.outcome, "", ""

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    # Suppress pytest default summary stats and failures
    terminalreporter.summary_stats = lambda: None
    terminalreporter.summary_failures = lambda: None
    terminalreporter.summary_errors = lambda: None
    if hasattr(terminalreporter, "short_test_summary"):
        terminalreporter.short_test_summary = lambda: None

    passed_reports = [r for r in terminalreporter.stats.get("passed", []) if r.when == "call"]
    failed_reports = [r for r in terminalreporter.stats.get("failed", []) if r.when == "call"]

    results = {}
    total_duration = 0.0

    for rep in passed_reports:
        duration_ms = max(1, int(rep.duration * 1000))
        total_duration += rep.duration
        node_name = rep.nodeid.split("::")[-1]
        results[node_name] = {
            "Status": "passed",
            "Execution time": f"{duration_ms}ms"
        }

    for rep in failed_reports:
        duration_ms = max(1, int(rep.duration * 1000))
        total_duration += rep.duration
        node_name = rep.nodeid.split("::")[-1]
        err_msg = ""
        if hasattr(rep, "longrepr") and rep.longrepr:
            if hasattr(rep.longrepr, "reprcrash"):
                err_msg = rep.longrepr.reprcrash.message
            else:
                err_msg = str(rep.longrepr)
        first_line = err_msg.strip().splitlines()[0] if err_msg else "AssertionError"
        if first_line.startswith("AssertionError: "):
            first_line = first_line.replace("AssertionError: ", "", 1)
        results[node_name] = {
            "Status": "failed",
            "Execution time": f"{duration_ms}ms",
            "Error": first_line
        }

    passed_count = len(passed_reports)
    failed_count = len(failed_reports)

    results["Passed"] = passed_count
    results["Failed"] = failed_count
    results["Total bugs"] = passed_count + failed_count
    results["Total Execution time"] = f"{int(total_duration * 1000)}ms"

    terminalreporter._tw.line(json.dumps(results, indent=2))
