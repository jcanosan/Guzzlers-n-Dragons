from src.config.settings import Settings


class TestSettings:
    def test_defaults(self):
        s = Settings()
        assert s.database_url == "sqlite:///data/ingredients.db"
        assert s.debug is False
        assert s.llm_model == "ollama:gemma4:31b-cloud"
        assert s.llm_temperature == 0.7

    def test_custom_values(self):
        s = Settings(DATABASE_URL="sqlite:///test.db", DEBUG=True)
        assert s.database_url == "sqlite:///test.db"
        assert s.debug is True

    def test_port_defaults(self):
        s = Settings()
        assert s.host == "0.0.0.0"
        assert s.port == 8000
