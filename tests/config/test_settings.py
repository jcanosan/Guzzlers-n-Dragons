from src.config.settings import Settings


class TestSettings:
    def test_defaults(self, monkeypatch):
        for key in (
            "DATABASE_URL",
            "DEBUG",
            "LLM_MODEL",
            "LLM_TEMPERATURE",
            "AGENT_TIMEOUT_SECONDS",
            "EMBEDDING_MODEL",
        ):
            monkeypatch.delenv(key, raising=False)
        s = Settings(_env_file=None)
        assert s.database_url == "sqlite:///data/ingredients.db"
        assert s.debug is False
        assert s.llm_model == "gemma4:31b-cloud"
        assert s.llm_temperature == 0.7

    def test_custom_values(self):
        s = Settings(DATABASE_URL="sqlite:///test.db", DEBUG=True)
        assert s.database_url == "sqlite:///test.db"
        assert s.debug is True

    def test_model_no_prefix(self):
        s = Settings(LLM_MODEL="gemma4:31b-cloud")
        assert s.llm_model == "gemma4:31b-cloud"
        assert "ollama:" not in s.llm_model
