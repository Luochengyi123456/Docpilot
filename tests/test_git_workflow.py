import subprocess

import pytest

from docpilot import cli


def test_commit_and_maybe_push_rollback_only_after_commit(monkeypatch):
    calls: list[list[str]] = []

    def fake_run(args, check=True):
        calls.append(args)
        if args[:2] == ["git", "push"]:
            raise subprocess.CalledProcessError(returncode=1, cmd=args)
        return None

    monkeypatch.setattr(cli, "_run_git_command", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        cli._commit_and_maybe_push("docs: update", True)

    assert ["git", "add", "."] in calls
    assert ["git", "commit", "-m", "docs: update"] in calls
    assert ["git", "push"] in calls
    assert ["git", "reset", "--hard", "HEAD~1"] in calls


def test_commit_and_maybe_push_no_push_no_rollback(monkeypatch):
    calls: list[list[str]] = []

    def fake_run(args, check=True):
        calls.append(args)
        return None

    monkeypatch.setattr(cli, "_run_git_command", fake_run)

    result = cli._commit_and_maybe_push("docs: update", False)

    assert result.commit_created is True
    assert result.push_attempted is False
    assert ["git", "reset", "--hard", "HEAD~1"] not in calls
