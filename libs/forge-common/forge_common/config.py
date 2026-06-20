"""Environment-driven settings shared by all Forge services.

Each service may subclass `Settings` to add its own fields. Values come from the
environment (or a local `.env`), keeping the gateway 12-factor and air-gap friendly.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FORGE_", env_file=".env", extra="ignore")

    # Service identity
    service_name: str = "forge-service"
    log_level: str = "INFO"

    # Event bus (NATS)
    nats_url: str = "nats://localhost:4222"

    # Graph + time-series (Postgres + AGE + Timescale)
    postgres_dsn: str = "postgresql://forge:forge@localhost:5432/forge"

    # MQTT / UNS broker
    mqtt_url: str = "mqtt://localhost:1883"

    # Identity (Keycloak OIDC)
    oidc_issuer: str = "http://localhost:8080/realms/forge"

    # HTTP
    host: str = "0.0.0.0"
    port: int = 8000
