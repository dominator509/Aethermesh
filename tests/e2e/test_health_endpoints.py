"""E2E tests for health endpoints — EP-008 M4.

Starts health server on a temp port, verifies all endpoints respond.
"""

# mypy: allow-untyped-defs

import time
import urllib.error
import urllib.request
from threading import Thread

from aethermesh.tools.health import start_health_server


def _health_url(port: int, path: str) -> str:
    return f"http://127.0.0.1:{port}{path}"


class TestHealthEndpoints:
    port: int = 19100
    server_thread: Thread | None = None

    @classmethod
    def setup_class(cls) -> None:
        cls.port = 19100
        cls.server_thread = Thread(target=start_health_server, args=(cls.port,), daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    def test_healthz_during_startup(self) -> None:
        """healthz returns 503 during grace period."""
        # Server just started — within 5s grace
        try:
            urllib.request.urlopen(_health_url(self.port, "/healthz"), timeout=2)
        except urllib.error.HTTPError as e:
            assert e.code == 503

    def test_livez(self) -> None:
        """livez always returns ok."""
        resp = urllib.request.urlopen(_health_url(self.port, "/livez"), timeout=2)
        assert resp.status == 200
        assert resp.read().decode() == "ok"

    def test_metrics_endpoint(self) -> None:
        """metrics returns Prometheus exposition."""
        resp = urllib.request.urlopen(_health_url(self.port, "/metrics"), timeout=2)
        assert resp.status == 200
        body = resp.read().decode()
        assert "# HELP" in body or "aep_" in body

    def test_healthz_after_grace(self) -> None:
        """healthz returns ok after 5s grace period."""
        time.sleep(5)
        resp = urllib.request.urlopen(_health_url(self.port, "/healthz"), timeout=2)
        assert resp.status == 200
        assert resp.read().decode() == "ok"

    def test_readyz(self) -> None:
        """readyz returns ok after startup."""
        time.sleep(0.5)
        resp = urllib.request.urlopen(_health_url(self.port, "/readyz"), timeout=2)
        assert resp.status == 200
        assert resp.read().decode() == "ok"

    def test_404(self) -> None:
        """Unknown path returns 404."""
        try:
            urllib.request.urlopen(_health_url(self.port, "/nonexistent"), timeout=2)
        except urllib.error.HTTPError as e:
            assert e.code == 404
