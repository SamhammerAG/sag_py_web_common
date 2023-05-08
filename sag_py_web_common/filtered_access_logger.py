from typing import Dict

from asgi_logger.middleware import AccessInfo, AccessLogAtoms, AccessLoggerMiddleware
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope


class FilteredAccessLoggerMiddleware(AccessLoggerMiddleware):
    """The lib asgi-logger wrapped to exclude prtg and health checks from being logged
    Furthermore it adds logging of the incoming requests
    """

    async def __call__(self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if self._should_log(scope):
            self.logger.info("Received: %s %s", scope["method"], scope["path"])

        await super().__call__(scope, receive, send)

    def log(self, scope: HTTPScope, info: AccessInfo) -> None:
        if self._should_log(scope):
            extra_args = {"execution_time": info["end_time"] - info["start_time"]}
            self.logger.info(self.format, AccessLogAtoms(scope, info), extra=extra_args)

    def _should_log(self, scope: HTTPScope) -> bool:
        return scope["type"] == "http" and not self._has_health_check_header(scope)

    def _has_health_check_header(self, scope: HTTPScope) -> bool:
        header_dict: Dict[bytes, bytes] = dict(scope["headers"])
        return b"healthcheck" in header_dict and header_dict[b"healthcheck"] in {
            b"livenessprobe",
            b"readinessprobe",
            b"startupprobe",
            b"prtg",
        }
