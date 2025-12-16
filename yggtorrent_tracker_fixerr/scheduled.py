import asyncio
import datetime
import logging

from yggtorrent_tracker_fixerr import arr, utils
from yggtorrent_tracker_fixerr.Classes.Settings import Settings
from yggtorrent_tracker_fixerr.Classes.TorrentClient import TorrentClient

logger = logging.getLogger("yggtorrent_tracker_fixerr")


def update_all_torrents(torrent_client: TorrentClient):
    logger.info(f"Job update_all_torrents started at {datetime.datetime.now()}")
    torrent_client.handle_all_torrents()
    logger.info(f"Job update_all_torrents ended at {datetime.datetime.now()}")


def update_dynamic_settings(settings: Settings, torrent_client: TorrentClient):
    logger.info(f"Job update_dynamic_settings started at {datetime.datetime.now()}")
    old_settings = settings.dynamic_settings.copy()
    settings.fetch_dynamic_settings()
    new_settings = settings.dynamic_settings.copy()
    if not utils.dicts_equals(old_settings, new_settings):
        logger.warning("New dynamic settings recovered, triggering torrents update")
        torrent_client.handle_all_torrents()
    else:
        logger.info("No dynamic settings update")
    logger.info(f"Job update_dynamic_settings ended at {datetime.datetime.now()}")


async def register_radarr_sonarr(settings: Settings) -> None:
    logger.info(f"Job register_radarr_sonarr started at {datetime.datetime.now()}")
    await utils.wait_until_external_api_is_up(f"{settings.external_url}/healthz")
    logger.info("External API is up")
    if settings.radarr_sync_enabled:
        logger.info("Launching initial radarr sync")
        await asyncio.to_thread(arr.sync_radarr_webhook, settings)
    else:
        logger.info("No radarr sync requested")
    if settings.sonarr_sync_enabled:
        logger.info("Launching initial sonarr sync")
        await asyncio.to_thread(arr.sync_sonarr_webhook, settings)
    else:
        logger.info("No sonarr sync requested")
    logger.info(f"Job register_radarr_sonarr ended at {datetime.datetime.now()}")
