from __future__ import annotations

import logging
import time
import urllib.robotparser
from urllib.parse import urljoin

import requests

logger = logging.getLogger("scraper.acquisition")


class RobotsDisallowedError(Exception):
    """Levée quand robots.txt interdit explicitement l'URL demandée."""


class HttpClient:
    def __init__(self, base_url: str, user_agent: str, delay_seconds: float, timeout: int = 10):
        self.base_url = base_url
        self.user_agent = user_agent
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self._last_request_at: float | None = None

        self._robots = urllib.robotparser.RobotFileParser()
        self._robots.set_url(urljoin(base_url, "/robots.txt"))
        self._robots.read()
        crawl_delay = self._robots.crawl_delay(user_agent)
        if crawl_delay and crawl_delay > self.delay_seconds:
            logger.info(
                "robots.txt impose un Crawl-delay=%ss, supérieur au délai configuré (%ss) : alignement.",
                crawl_delay, self.delay_seconds,
            )
            self.delay_seconds = float(crawl_delay)

        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    def _throttle(self) -> None:
        if self._last_request_at is not None:
            elapsed = time.monotonic() - self._last_request_at
            remaining = self.delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_at = time.monotonic()

    def get(self, url: str) -> requests.Response:
        if not self._robots.can_fetch(self.user_agent, url):
            raise RobotsDisallowedError(f"robots.txt interdit la collecte de : {url}")

        self._throttle()
        logger.info("GET %s", url)
        response = self._session.get(url, timeout=self.timeout)
        logger.info("-> %s (%d octets)", response.status_code, len(response.content))
        response.raise_for_status()
        return response
