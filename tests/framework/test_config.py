"""Unit tests for config.get_base_url()."""

import pytest

from config import APP_URLS, VALID_ENVS, get_base_url


@pytest.mark.unit
class TestGetBaseUrl:
    """Verify get_base_url resolves URLs correctly and rejects invalid inputs."""

    @pytest.mark.parametrize(
        ("app_name", "env", "expected_url"),
        [
            pytest.param(
                app,
                env,
                url,
                id=f"{app}-{env}",
            )
            for app, envs in APP_URLS.items()
            for env, url in envs.items()
        ],
    )
    def test_returns_correct_url_for_every_registered_combination(
        self, app_name: str, env: str, expected_url: str
    ) -> None:
        assert get_base_url(app_name, env) == expected_url

    def test_raises_for_invalid_environment(self) -> None:
        app_name = next(iter(APP_URLS))
        with pytest.raises(ValueError, match="Invalid environment 'staging'"):
            get_base_url(app_name, "staging")

    def test_raises_for_unknown_app(self) -> None:
        env = next(iter(VALID_ENVS))
        with pytest.raises(ValueError, match="Unknown app 'nonexistent'"):
            get_base_url("nonexistent", env)

    def test_raises_when_env_not_configured_for_app(self) -> None:
        with pytest.raises(
            ValueError, match="No 'local' URL configured for 'saucedemo'"
        ):
            get_base_url("saucedemo", "local")

    def test_invalid_env_error_lists_valid_options(self) -> None:
        with pytest.raises(ValueError, match="Valid options: local, prod"):
            get_base_url("theinternet", "unknown")

    def test_unknown_app_error_lists_registered_apps(self) -> None:
        with pytest.raises(ValueError, match="Registered apps:"):
            get_base_url("fake", "prod")

    def test_missing_env_error_lists_available_envs(self) -> None:
        with pytest.raises(ValueError, match="Available: prod"):
            get_base_url("saucedemo", "local")
