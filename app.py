import os
import sys

sys.path.append(os.getcwd())
import asyncio
import logging
from contextlib import asynccontextmanager

from litestar import Litestar
from litestar.di import Provide
from litestar.logging import LoggingConfig
from litestar.middleware import DefineMiddleware

from yggtorrent_tracker_fixerr import api, scheduled, utils
from yggtorrent_tracker_fixerr.Classes.QBittorrent import QBittorrent
from yggtorrent_tracker_fixerr.Classes.Settings import Settings
from yggtorrent_tracker_fixerr.Classes.TorrentClient import TorrentClient

logger = logging.getLogger("yggtorrent_tracker_fixerr")

settings = Settings()

if settings.torrent_client.lower() == "qbittorrent":
    torrent_client = QBittorrent(
        settings=settings,
        base_url=settings.qbittorrent_url,
        username=settings.qbittorrent_auth_username,
        password=settings.qbittorrent_auth_password,
    )
else:
    raise Exception("Invalid torrent client")

logger.warning(f"Choosen torrent client : {torrent_client.name}")


async def torrent_client_fn() -> TorrentClient:
    return torrent_client


async def settings_fn() -> Settings:
    return settings


auth_mw = DefineMiddleware(api.APIAuthenticationMiddleware, exclude="schema")
logger.info("Started")


@asynccontextmanager
async def lifespan_tasks(app: Litestar):
    scheduled_tasks = []
    if settings.radarr_sync_enabled or settings.sonarr_sync_enabled:
        logger.warning("Triggering registering to sonarr and/or radarr now")
        asyncio.create_task(scheduled.register_radarr_sonarr(settings))
        if settings.radarr_sonarr_sync_interval_seconds > 0:
            logger.warning(
                f"Scheduling radarr sonarr sync every {str(settings.radarr_sonarr_sync_interval_seconds)} seconds"
            )
            radarr_sonarr_sync_task = asyncio.create_task(
                utils.run_job_periodically(
                    settings.radarr_sonarr_sync_interval_seconds, scheduled.register_radarr_sonarr, settings
                )
            )
            scheduled_tasks.append(radarr_sonarr_sync_task)
        else:
            logger.info("Disabling scheduled radarr sonarr sync")

    if settings.dynamic_settings_refresh_interval_seconds > 0:
        logger.warning(
            f"Scheduling dynamic settings update every {str(settings.dynamic_settings_refresh_interval_seconds)} seconds"
        )
        dynamic_settings_task = asyncio.create_task(
            utils.run_job_periodically(
                settings.dynamic_settings_refresh_interval_seconds,
                scheduled.update_dynamic_settings,
                settings,
                torrent_client,
            )
        )
        scheduled_tasks.append(dynamic_settings_task)
    else:
        logger.info("Disabling scheduled dynamic settings update")

    if settings.all_torrents_refresh_interval_seconds > 0:
        logger.warning(
            f"Scheduling all torrents refresh every {str(settings.all_torrents_refresh_interval_seconds)} seconds"
        )
        refresh_all_torrents_task = asyncio.create_task(
            utils.run_job_periodically(
                settings.all_torrents_refresh_interval_seconds, scheduled.update_all_torrents, torrent_client
            )
        )
        scheduled_tasks.append(refresh_all_torrents_task)
    else:
        logger.info("Disabling scheduled all torrents refresh")

    yield

    for task in scheduled_tasks:
        if not task.done():
            task.cancel()

    try:
        await asyncio.wait_for(asyncio.gather(*scheduled_tasks, return_exceptions=True), timeout=30.0)
        logger.info("All scheduled tasks completed successfully during shutdown")
    except asyncio.TimeoutError:
        logger.warning("Some jobs didn't finish in time during shutdown")
    except Exception as e:
        logger.error(f"Error during task shutdown: {e}")


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
    log_exceptions="always",
)

app = Litestar(
    route_handlers=[
        api.healthz_endpoint,
        api.handle_all_torrents_endpoint,
        api.handle_torrent_endpoint,
        api.sonarr_webhook_endpoint,
        api.radarr_webhook_endpoint,
    ],
    dependencies={"torrent_client": Provide(torrent_client_fn), "settings": Provide(settings_fn)},
    middleware=[auth_mw],
    lifespan=[lifespan_tasks],
    logging_config=logging_config,
)
