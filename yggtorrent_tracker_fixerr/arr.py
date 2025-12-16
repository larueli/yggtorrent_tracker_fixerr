import logging

import httpx

from yggtorrent_tracker_fixerr.Classes.Settings import Settings

logger = logging.getLogger("yggtorrent_tracker_fixerr")


def sync_radarr_webhook(settings: Settings) -> None:
    payload = {
        "configContract": "WebhookSettings",
        "fields": [
            {"name": "url", "value": f"{settings.external_url}/webhook/radarr"},
            {"name": "method", "value": 1},
            {"name": "username"},
            {"name": "password"},
            {"name": "headers", "value": [{"key": "X-Api-Key", "value": f"{settings.api_key}"}]},
        ],
        "implementation": "Webhook",
        "implementationName": "Webhook",
        "includeHealthWarnings": False,
        "infoLink": "https://wiki.servarr.com/radarr/supported#webhook",
        "name": settings.radarr_webhook_name,
        "onApplicationUpdate": False,
        "onDownload": False,
        "onGrab": True,
        "onHealthIssue": False,
        "onHealthRestored": False,
        "onManualInteractionRequired": False,
        "onMovieAdded": False,
        "onMovieDelete": False,
        "onMovieFileDelete": False,
        "onMovieFileDeleteForUpgrade": False,
        "onRename": False,
        "onUpgrade": False,
        "supportsOnApplicationUpdate": True,
        "supportsOnDownload": True,
        "supportsOnGrab": True,
        "supportsOnHealthIssue": True,
        "supportsOnHealthRestored": True,
        "supportsOnManualInteractionRequired": True,
        "supportsOnMovieAdded": True,
        "supportsOnMovieDelete": True,
        "supportsOnMovieFileDelete": True,
        "supportsOnMovieFileDeleteForUpgrade": True,
        "supportsOnRename": True,
        "supportsOnUpgrade": True,
        "tags": [],
    }

    headers = {"X-Api-Key": settings.radarr_api_key, "Content-Type": "application/json"}
    try:
        r = httpx.get(f"{settings.radarr_url}/api/v3/notification", headers=headers)
        logger.debug(f"Radarr webhook get response: {r.status_code} - {r.text}")
        r.raise_for_status()
        notifications = r.json()
        existing = False
        for n in notifications:
            if n["name"] == settings.radarr_webhook_name:
                existing = True
                logger.info("Radarr webhook already exists, updating...")
                r = httpx.put(f"{settings.radarr_url}/api/v3/notification/{n['id']}", json=payload, headers=headers)
                logger.debug(f"Radarr webhook update response: {r.status_code} - {r.text}")
                r.raise_for_status()
                logger.info("Radarr webhook updated successfully.")
        if not existing:
            logger.info("Radarr webhook does not exist, creating...")
            r = httpx.post(f"{settings.radarr_url}/api/v3/notification", json=payload, headers=headers)
            logger.debug(f"Radarr webhook sync response: {r.status_code} - {r.text}")
            r.raise_for_status()
        logger.info("Radarr webhook synced successfully.")
    except Exception as e:
        logger.error(f"Failed to sync Radarr webhook: {e}")


def sync_sonarr_webhook(settings: Settings) -> None:
    payload = {
        "configContract": "WebhookSettings",
        "fields": [
            {"name": "url", "value": f"{settings.external_url}/webhook/sonarr"},
            {"name": "method", "value": 1},
            {"name": "username"},
            {"name": "password"},
            {"name": "headers", "value": [{"key": "X-Api-Key", "value": f"{settings.api_key}"}]},
        ],
        "implementation": "Webhook",
        "implementationName": "Webhook",
        "includeHealthWarnings": False,
        "infoLink": "https://wiki.servarr.com/sonarr/supported#webhook",
        "name": settings.sonarr_webhook_name,
        "onApplicationUpdate": False,
        "onDownload": False,
        "onGrab": True,
        "onHealthIssue": False,
        "onHealthRestored": False,
        "onManualInteractionRequired": False,
        "onMovieAdded": False,
        "onMovieDelete": False,
        "onMovieFileDelete": False,
        "onMovieFileDeleteForUpgrade": False,
        "onRename": False,
        "onUpgrade": False,
        "supportsOnApplicationUpdate": True,
        "supportsOnDownload": True,
        "supportsOnGrab": True,
        "supportsOnHealthIssue": True,
        "supportsOnHealthRestored": True,
        "supportsOnManualInteractionRequired": True,
        "supportsOnMovieAdded": True,
        "supportsOnMovieDelete": True,
        "supportsOnMovieFileDelete": True,
        "supportsOnMovieFileDeleteForUpgrade": True,
        "supportsOnRename": True,
        "supportsOnUpgrade": True,
        "tags": [],
    }

    headers = {"X-Api-Key": settings.sonarr_api_key, "Content-Type": "application/json"}
    try:
        r = httpx.get(f"{settings.sonarr_url}/api/v3/notification", headers=headers)
        logger.debug(f"Sonarr webhook get response: {r.status_code} - {r.text}")
        r.raise_for_status()
        notifications = r.json()
        existing = False
        for n in notifications:
            if n["name"] == settings.sonarr_webhook_name:
                existing = True
                logger.info("Sonarr webhook already exists, updating...")
                r = httpx.put(f"{settings.sonarr_url}/api/v3/notification/{n['id']}", json=payload, headers=headers)
                logger.debug(f"Sonarr webhook update response: {r.status_code} - {r.text}")
                r.raise_for_status()
                logger.info("Sonarr webhook updated successfully.")
        if not existing:
            logger.info("Sonarr webhook does not exist, creating...")
            r = httpx.post(f"{settings.sonarr_url}/api/v3/notification", json=payload, headers=headers)
            logger.debug(f"Sonarr webhook sync response: {r.status_code} - {r.text}")
            r.raise_for_status()
        logger.info("Sonarr webhook synced successfully.")
    except Exception as e:
        logger.error(f"Failed to sync Sonarr webhook: {e}")
