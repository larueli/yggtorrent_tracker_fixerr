import logging

from yggtorrent_tracker_fixerr.Classes.Settings import Settings
from yggtorrent_tracker_fixerr.Classes.TorrentClient import TorrentClient

logger = logging.getLogger("yggtorrent_tracker_fixerr")

ignored_trackers = [
    "** [DHT] **",
    "** [PeX] **",
    "** [LSD] **",
]


class QBittorrent(TorrentClient):
    def __init__(self, settings: Settings, base_url: str, username: str, password: str):
        super().__init__(settings)

        self.base_url = base_url
        self.username = username
        self.password = password
        self.login()

    @property
    def name_sonarr(self) -> str:
        return "qBittorrent"

    @property
    def name_radarr(self) -> str:
        return "qBittorrent"

    @property
    def name(self) -> str:
        return "QBittorrent"

    def login(self) -> None:
        r = self.session.post(
            f"{self.base_url}/api/v2/auth/login", data={"username": self.username, "password": self.password}
        )
        if r.text != "Ok.":
            raise RuntimeError(f"qBittorrent login failed: {r.status_code} {r.text}")

    def get_all_torrents(self):
        r = self.request_with_retry("GET", f"{self.base_url}/api/v2/torrents/info")
        r.raise_for_status()
        return r.json()

    def handle_all_torrents(self) -> None:
        torrents = self.get_all_torrents()
        self.handle_torrents(torrents)

    def handle_torrent_hash(self, torrent_hash: str):
        logger.info(f"Handling torrent hash {torrent_hash}")
        r = self.request_with_retry("GET", f"{self.base_url}/api/v2/torrents/info", params={"hashes": torrent_hash})
        r.raise_for_status()
        torrents = r.json()
        self.handle_torrents(torrents)

    def handle_torrents(self, torrents: list[dict]) -> None:
        for torrent in torrents:
            self.handle_torrent(torrent)

    def handle_torrent(self, torrent) -> bool:
        logger.info(f"Handling torrent {torrent['name']}")
        trackers = self.get_torrent_trackers(torrent["hash"])

        to_remove = []
        to_add = [
            f"{self.settings.dynamic_settings['yggtorrent_tracker_url'].strip('/')}/{self.settings.yggtorrent_passkey}/announce"
        ]
        is_yggtorrent = False

        for t in trackers:
            url = t["url"]
            if url in ignored_trackers:
                continue

            if url == to_add[0]:
                is_yggtorrent = True
                to_add = []
            elif any(
                old_url in url
                for old_url in self.settings.dynamic_settings["yggtorrent_old_trackers_urls"]
                + [self.settings.dynamic_settings["yggtorrent_tracker_url"]]
            ):
                is_yggtorrent = True
                logger.info(f"In torrent {torrent['name']} found old YGG tracker URL to remove: {url}")
                to_remove.append(url)
            else:
                to_remove.append(url)

        if not is_yggtorrent:
            logger.info(f"Torrent {torrent['name']} is not from YGG, skipping.")
            return False

        for old_url in to_remove:
            logger.info(f"Removing trackers from torrent {torrent['name']}: {old_url}")
            self.remove_torrent_tracker(torrent["hash"], old_url)
        if len(to_remove) == 0:
            logger.info(f"No trackers to remove from torrent {torrent['name']}")

        for new_url in to_add:
            logger.info(f"Adding tracker to torrent {torrent['name']}: {new_url}")
            self.add_torrent_tracker(torrent["hash"], new_url)
        if len(to_add) == 0:
            logger.info(f"No trackers to add to torrent {torrent['name']}")

        if len(to_add) > 0 or len(to_remove) > 0:
            logger.info(f"Reannouncing torrent {torrent['name']}")
            self.reannounce_torrent(torrent["hash"])

        return True

    def get_torrent_trackers(self, torrent_hash: str):
        r = self.request_with_retry("GET", f"{self.base_url}/api/v2/torrents/trackers", params={"hash": torrent_hash})
        r.raise_for_status()
        return r.json()

    def reannounce_torrent(self, torrent_hash: str):
        r = self.request_with_retry(
            "POST",
            f"{self.base_url}/api/v2/torrents/reannounce",
            data={
                "hashes": torrent_hash,
            },
        )
        r.raise_for_status()

    def remove_torrent_tracker(self, torrent_hash: str, url: str):
        r = self.request_with_retry(
            "POST",
            f"{self.base_url}/api/v2/torrents/removeTrackers",
            data={
                "hash": torrent_hash,
                "urls": url,
            },
        )
        r.raise_for_status()

    def add_torrent_tracker(self, torrent_hash: str, url: str):
        r = self.request_with_retry(
            "POST",
            f"{self.base_url}/api/v2/torrents/addTrackers",
            data={
                "hash": torrent_hash,
                "urls": url,
            },
        )
        r.raise_for_status()
