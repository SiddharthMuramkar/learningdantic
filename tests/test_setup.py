"""setup() and has_key(), the helpers the notebooks lean on. No keys, no network."""

import pytest

from learningdantic import has_key, setup

KEYS = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "LOGFIRE_TOKEN", "MODEL"]


@pytest.fixture(autouse=True)
def no_keys(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # no .env above a temp dir, so only what a test writes is loaded
    monkeypatch.setenv("LOGFIRE_CREDENTIALS_DIR", str(tmp_path / ".logfire"))
    for key in KEYS:
        monkeypatch.delenv(key, raising=False)


def test_the_fake_model_needs_no_key():
    assert has_key("test")


def test_a_missing_key_is_reported():
    assert not has_key("openai:gpt-6-luna")
    assert not has_key("anthropic:claude-haiku-5-5")  # the old `LIVE` check got this one wrong
    assert not has_key("xai:grok-4")  # its extra isn't installed


def test_a_blank_key_in_env_counts_as_missing(tmp_path):
    # `cp .env.example .env` without pasting a key leaves `OPENAI_API_KEY=` in the file.
    (tmp_path / ".env").write_text("OPENAI_API_KEY=\n")
    assert setup() == "openai:gpt-6-luna"
    assert not has_key("openai:gpt-6-luna")


def test_a_key_is_reported(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")  # building the model makes no request
    assert has_key("openai:gpt-6-luna")
