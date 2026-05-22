import json

from he_cr_model.cli import main


def test_list_levels_command(capsys) -> None:
    assert main(["list-levels"]) == 0
    captured = capsys.readouterr()
    assert "3_1S" in captured.out
    assert "5_3G" in captured.out


def test_scan_fails_closed(capsys) -> None:
    assert main(["scan"]) == 2
    captured = capsys.readouterr()
    assert "FAIL_CLOSED" in captured.err


def test_build_network_exports_audit_file(tmp_path, capsys) -> None:
    output = tmp_path / "network_build.json"
    assert main(["build-network", "--output", str(output)]) == 0
    captured = capsys.readouterr()
    assert "network_build_exported" in captured.out
    assert "templates=" in captured.out
    assert "network_all=" in captured.out
    assert "network_solver_ready=" in captured.out
    assert "issues=" in captured.out
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "metadata" in payload
    assert "templates_count" in payload["metadata"]
    assert "network_all_count" in payload["metadata"]
    assert "network_solver_ready_count" in payload["metadata"]
    assert "validation_issues_count" in payload["metadata"]
