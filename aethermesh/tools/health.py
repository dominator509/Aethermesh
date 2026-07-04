"""HTTP health endpoints on port 9100.

Per SPEC-007 § Health + OPERATIONS.md. EP-008 M4.
"""

from __future__ import annotations

import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import cast

from aethermesh.common.metrics import all_metrics
from aethermesh.common.metrics import snapshot as metric_snapshot

_STARTUP_GRACE = 5  # seconds before /healthz reports ok


class _HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        pass  # suppress access logs

    def _send(self, code: int, body: str, content_type: str = "text/plain") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._healthz()
        elif self.path == "/readyz":
            self._readyz()
        elif self.path == "/livez":
            self._livez()
        elif self.path == "/metrics":
            self._metrics()
        else:
            self._send(404, "not found")

    def _healthz(self) -> None:
        uptime = time.time() - _server_start_time(self.server)
        if uptime < _STARTUP_GRACE:
            self._send(503, f"starting up ({_STARTUP_GRACE - uptime:.0f}s remaining)")
            return
        self._send(200, "ok")

    def _readyz(self) -> None:
        # Ready when directory loaded + keys present (placeholder: always ready after grace)
        if time.time() - _server_start_time(self.server) < _STARTUP_GRACE:
            self._send(503, "not ready")
            return
        self._send(200, "ok")

    def _livez(self) -> None:
        self._send(200, "ok")

    def _metrics(self) -> None:
        lines = []
        for name, metric in sorted(all_metrics().items()):
            lines.append(f"# HELP {name} {metric.description}")
            lines.append(f"# TYPE {name} {metric.mtype}")
            data = metric_snapshot(name)
            if data:
                for label_key, value in data.items():
                    label_str = ",".join(f'{k}="{v}"' for k, v in label_key)
                    lines.append(f"{name}{{{label_str}}} {value}")
            else:
                lines.append(f"{name} 0")
        self._send(200, "\n".join(lines) + "\n", content_type="text/plain")


def start_health_server(port: int = 9100) -> None:
    """Start health-check HTTP server on *port*.

    Intended to be run in a background thread by callers that need async startup.
    """
    server = HTTPServer(("127.0.0.1", port), _HealthHandler)
    server.start_time = time.time()  # type: ignore[attr-defined]
    server.serve_forever()


def _server_start_time(server: object) -> float:
    return cast(float, getattr(server, "start_time", time.time()))
