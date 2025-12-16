import json
import logging
from typing import Any

import httpx
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("yggtorrent_tracker_fixerr")


class Settings(BaseSettings):
    torrent_client: str = Field("qbittorrent")
    qbittorrent_url: str
    qbittorrent_auth_username: str = Field("")
    qbittorrent_auth_password: str = Field("")

    dynamic_settings_location: str = Field(
        "https://raw.githubusercontent.com/larueli/yggtorrent_tracker_fixerr_data/refs/heads/main/data.json"
    )
    dynamic_settings_refresh_interval_seconds: int = Field(60 * 30)
    all_torrents_refresh_interval_seconds: int = Field(60 * 30)
    radarr_sonarr_sync_interval_seconds: int = Field(60 * 30)
    yggtorrent_tracker_url: str = Field("")
    yggtorrent_old_trackers_urls: list[str] = Field([])
    yggtorrent_passkey: str
    log_level: str = Field("INFO")
    api_key: str

    external_url: str = Field("")
    sonarr_sync_enabled: bool = Field(False)
    sonarr_url: str = Field("")
    sonarr_api_key: str = Field("")
    sonarr_webhook_name: str = Field("yggtorrent_tracker_fixerr")
    radarr_sync_enabled: bool = Field(False)
    radarr_url: str = Field("")
    radarr_api_key: str = Field("")
    radarr_webhook_name: str = Field("yggtorrent_tracker_fixerr")

    dynamic_settings: dict = Field({"yggtorrent_old_trackers_urls": [], "yggtorrent_tracker_url": ""})

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
        env_nested_delimiter="__",
    )

    @model_validator(mode="after")
    def check_radarr_config(self):
        if self.radarr_sync_enabled:
            missing = []
            if not self.radarr_url:
                missing.append("radarr_url")
            if not self.radarr_api_key:
                missing.append("radarr_api_key")
            if not self.external_url:
                missing.append("external_url")

            if missing:
                raise ValueError(f"Radarr sync is enabled, but these fields are missing: {', '.join(missing)}")

        return self

    @model_validator(mode="after")
    def check_sonarr_config(self):
        if self.sonarr_sync_enabled:
            missing = []
            if not self.sonarr_url:
                missing.append("sonarr_url")
            if not self.sonarr_api_key:
                missing.append("sonarr_api_key")
            if not self.external_url:
                missing.append("external_url")

            if missing:
                raise ValueError(f"Sonarr sync is enabled, but these fields are missing: {', '.join(missing)}")

        return self

    @model_validator(mode="after")
    def check_torrent_config(self):
        if self.torrent_client.lower() == "qbittorrent":
            if len(self.qbittorrent_url) == 0:
                raise ValueError("qbittorrent_url is required when using qbittorrent")
        else:
            raise ValueError(f"Invalid torrent client: {self.torrent_client}. Must be one of : qbittorrent")

        return self

    def __init__(self, **data: Any):
        super().__init__(**data)
        logger.setLevel(self.log_level.upper())
        self.fetch_dynamic_settings()

    def fetch_dynamic_settings_from_url(self, url) -> dict:
        logger.info(f"Fetching dynamic settings from URL: {url}")
        r = httpx.get(url)
        r.raise_for_status()
        data = r.json()
        return data

    def fetch_dynamic_settings_from_file(self, path) -> dict:
        logger.info(f"Loading dynamic settings from file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def fetch_dynamic_settings(self) -> None:
        logger.info("Fetching dynamic settings...")
        if self.dynamic_settings_location.startswith("http"):
            data = self.fetch_dynamic_settings_from_url(self.dynamic_settings_location)
        else:
            data = self.fetch_dynamic_settings_from_file(self.dynamic_settings_location)

        # old urls
        if len(self.yggtorrent_old_trackers_urls) > 0:
            self.dynamic_settings["yggtorrent_old_trackers_urls"] = self.yggtorrent_old_trackers_urls
        else:
            self.dynamic_settings["yggtorrent_old_trackers_urls"] = data["yggtorrent_old_trackers_urls"]

        # tracker url
        if len(self.yggtorrent_tracker_url) > 0:
            self.dynamic_settings["yggtorrent_tracker_url"] = self.yggtorrent_tracker_url
        else:
            self.dynamic_settings["yggtorrent_tracker_url"] = data["yggtorrent_tracker_url"]
        logger.info("Dynamic settings fetched.")
