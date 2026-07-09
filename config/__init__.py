"""Centralised configuration for the multi-app test platform."""

VALID_ENVS = frozenset(("prod", "local", "docker"))

APP_URLS: dict[str, dict[str, str]] = {
    "acceptapayment": {
        "local": "http://localhost:4242",
        # Hostname of the `stripe-app` service on the docker-compose network.
        # Must never match an HSTS-preloaded gTLD (e.g. bare `app`, `dev`) —
        # browsers force https:// on those, breaking plain-http navigation.
        "docker": "http://stripe-app:4242",
    },
}


def get_base_url(app_name: str, env: str) -> str:
    """Resolve the base URL for *app_name* in the given *env*.

    Raises:
        ValueError: If *env* is not in VALID_ENVS or has no URL for *app_name*.
    """
    if env not in VALID_ENVS:
        msg = f"Invalid environment '{env}'. Valid options: {', '.join(sorted(VALID_ENVS))}"
        raise ValueError(msg)

    urls = APP_URLS.get(app_name)
    if urls is None:
        msg = (
            f"Unknown app '{app_name}'. Registered apps: {', '.join(sorted(APP_URLS))}"
        )
        raise ValueError(msg)

    if env not in urls:
        msg = (
            f"No '{env}' URL configured for '{app_name}'. Available: {', '.join(urls)}"
        )
        raise ValueError(msg)

    return urls[env]
