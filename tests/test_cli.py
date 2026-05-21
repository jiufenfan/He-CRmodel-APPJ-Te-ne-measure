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
