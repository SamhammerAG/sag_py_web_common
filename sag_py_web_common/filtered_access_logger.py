import logging
from typing import List, Union

from asgi_logger.middleware import (AccessInfo, AccessLogAtoms,
                                    AccessLoggerMiddleware)
from asgiref.typing import (ASGI3Application, ASGIReceiveCallable,
                            ASGISendCallable, HTTPScope)


class FilteredAccessLoggerMiddleware(AccessLoggerMiddleware):
    """The lib asgi-logger wrapped to exclude prtg and health checks from being logged
    Furthermore it adds logging of the incoming requests
    """

    def __init__(
        self,
        app: ASGI3Application,
        format: Union[str, None],
        logger: Union[logging.Logger, None],
        excluded_pathes: Union[List[str], None]
    ) -> None:
        super().__init__(app, format, logger)
        self.excluded_pathes = excluded_pathes or []

    async def __call__(self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if self._should_log(scope):
            self.logger.info("Received: %s %s", scope["method"], scope["path"])

        await super().__call__(scope, receive, send)

    def log(self, scope: HTTPScope, info: AccessInfo) -> None:
        if self._should_log(scope):
            extra_args = {"execution_time": info["end_time"] - info["start_time"]}
            self.logger.info(self.format, AccessLogAtoms(scope, info), extra=extra_args)

    def _should_log(self, scope: HTTPScope) -> bool:
        return scope["type"] == "http" \
            and not FilteredAccessLoggerMiddleware._is_excluded_path(scope, self.excluded_pathes)

    @staticmethod
    def _is_excluded_path(scope: HTTPScope, excluded_pathes: List[str]) -> bool:
        if not excluded_pathes:
            return False

        path: str = str(scope["path"])
        return any(excluded in path for excluded in excluded_pathes)
