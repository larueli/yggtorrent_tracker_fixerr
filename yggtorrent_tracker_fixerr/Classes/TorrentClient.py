import logging
from abc import ABC, abstractmethod

import httpx

from yggtorrent_tracker_fixerr.Classes.Settings import Settings

logger = logging.getLogger("yggtorrent_tracker_fixerr")


class TorrentClient(ABC):
    def __init__(self, settings: Settings):
        """
        Instantiate the class with self.settings and self.session (httpx.Client())
        """
        self.settings = settings
        self.session = httpx.Client()

    @property
    @abstractmethod
    def name(self) -> str:
        """Name for the torrent client, will be used in logs for instance"""
        pass

    @property
    @abstractmethod
    def name_sonarr(self) -> str:
        """
        Name for the torrent client type in sonarr. Will be sent to the webhook as downloadClientType.
        Do not confuse it with the name of the download client, which can be freely choosed by the user and is meaningless.
        """
        pass

    @property
    @abstractmethod
    def name_radarr(self) -> str:
        """
        Name for the torrent client type in radarr. Will be sent to the webhook as downloadClientType
        Do not confuse it with the name of the download client, which can be freely choosed by the user and is meaningless.
        """
        pass

    @abstractmethod
    def login(self) -> None:
        """Should login the user with the self.session, called by request_with_retry in case of token expired for instance.
        If not applicable (API key with unlimited lifetime for example), should do nothing.

        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def handle_all_torrents(self) -> None:
        """
        Should scan every torrent of the client, check if they are yggtorrent or not and change trackers, then reannounce

        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def handle_torrent_hash(self, torrent_hash: str):
        """
        Should check if the torrent with given hash is yggtorrent or not and change trackers if needed then reannounce

        :param torrent_hash str: The hash of a torrent (not the name), usually given by sonarr or radarr in downloadId in the webhook
        :return: None
        :rtype: None
        """
        pass

    def request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Given a method, a URL and other args given to httpx.Request, it will try to send the request and if got a 403 error, will use self.login() to login and retry the request.

        :param method: HTTP Method
        :param url: URL to request
        :param kwargs: Other args to pass to httpx.Request

        :return: Response from the request
        :rtype: httpx.Response
        """
        req = httpx.Request(method, url, **kwargs)
        prepped = self.session.build_request(method=req.method, url=req.url, headers=req.headers, content=req.content)
        logger.debug(f"Requesting {req.method} {req.url} with headers {req.headers} and body {req.content.decode()}")

        response = self.session.send(prepped)
        logger.debug(f"Torrent client response: {response.status_code} - {response.text}")

        if response.status_code == 403:
            print("403 received, refreshing auth...")
            self.login()
            response = self.session.send(prepped)
            logger.debug(f"Torrent client response: {response.status_code} - {response.text}")

        return response
