import logging

from litestar import get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException, NotAuthorizedException
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

from yggtorrent_tracker_fixerr.Classes.Settings import Settings
from yggtorrent_tracker_fixerr.Classes.TorrentClient import TorrentClient

logger = logging.getLogger("yggtorrent_tracker_fixerr")


class APIAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        """Given a request, parse the request api key stored in the header and validate it by the settings"""
        settings: Settings = await connection.app.dependencies["settings"]()

        auth_header = connection.headers.get("X-API-Key")
        if not auth_header:
            raise NotAuthorizedException()

        if auth_header != settings.api_key:
            if connection.client is not None and len(connection.client) > 0:
                logger.warning(
                    f"Unauthorized access attempt with API key: {auth_header} from IP {connection.client[0]}"
                )
            else:
                logger.warning(f"Unauthorized access attempt with API key: {auth_header} from unknown IP")
            raise NotAuthorizedException()
        return AuthenticationResult(user=None, auth=None)


@get("/healthz", exclude_from_auth=True)
async def healthz_endpoint(torrent_client: TorrentClient) -> dict:
    """Health check endpoint."""
    try:
        torrent_client.login()
        return {"status": "ok", "reason": "Connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Torrent Client {torrent_client.name} login failed: {e}")


@post("/handle_all_torrents")
async def handle_all_torrents_endpoint(torrent_client: TorrentClient) -> dict:
    """Endpoint to handle all torrents."""
    logger.warning("Received a request to handle all torrents")
    torrent_client.handle_all_torrents()
    return {"status": "Handled all torrents."}


@post("/handle_torrent/{torrent_hash:str}")
async def handle_torrent_endpoint(torrent_client: TorrentClient, torrent_hash: str) -> dict:
    """Endpoint to handle a specific torrent by its hash."""
    logger.warning(f"Received a request to handle torrent hash {torrent_hash}")
    try:
        torrent_client.handle_torrent_hash(torrent_hash)
    except IndexError:
        raise HTTPException(status_code=404, detail="Torrent not found.")
    return {"status": "Handled torrent", "reason": torrent_hash}


@post("/webhook/radarr")
async def radarr_webhook_endpoint(torrent_client: TorrentClient, data: dict) -> dict:
    """Endpoint suitable for radarr webhook to handle a specific torrent by its hash."""
    try:
        event_type = data.get("eventType", "")
        download_client_type = data.get("downloadClientType", "")
        download_id = data.get("downloadId", "")

        logger.warning(
            f"Received on radarr webhook event {event_type} from download client {download_client_type} with download ID {download_id}"
        )
        if event_type not in ["Grab"]:
            logger.info(f"Ignoring event type {event_type}")
            return {"status": "ignored", "reason": f"eventType {event_type} not relevant"}
        elif download_client_type != torrent_client.name_radarr:
            logger.info(f"Ignoring download client type {download_client_type}")
            return {"status": "ignored", "reason": f"downloadClientType not {torrent_client.name_radarr}"}

        torrent_hash = download_id
        logger.info(f"Processing radarr webhook for torrent hash {torrent_hash}")
        torrent_client.handle_torrent_hash(torrent_hash)

        return {"status": "ok", "hash": torrent_hash}
    except Exception as e:
        logger.error(f"Error handling radarr webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error handling radarr webhook: {e}")


@post("/webhook/sonarr")
async def sonarr_webhook_endpoint(torrent_client: TorrentClient, data: dict) -> dict:
    """Endpoint suitable for sonarr webhook to handle a specific torrent by its hash."""
    try:
        event_type = data.get("eventType", "")
        download_client_type = data.get("downloadClientType", "")
        download_id = data.get("downloadId", "")

        logger.warning(
            f"Received on sonarr webhook event {event_type} from download client {download_client_type} with download ID {download_id}"
        )
        if event_type not in ["Grab"]:
            logger.info(f"Ignoring event type {event_type}")
            return {"status": "ignored", "reason": f"eventType {event_type} not relevant"}
        elif download_client_type != torrent_client.name_sonarr:
            logger.info(f"Ignoring download client type {download_client_type}")
            return {"status": "ignored", "reason": f"downloadClientType not {torrent_client.name_sonarr}"}

        torrent_hash = download_id
        logger.info(f"Processing sonarr webhook for torrent hash {torrent_hash}")
        torrent_client.handle_torrent_hash(torrent_hash)

        return {"status": "ok", "hash": torrent_hash}
    except Exception as e:
        logger.error(f"Error handling sonarr webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error handling sonarr webhook: {e}")
