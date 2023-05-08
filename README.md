# sag_py_web_common
[![Maintainability][codeclimate-image]][codeclimate-url]
[![Coverage Status][coveralls-image]][coveralls-url]
[![Known Vulnerabilities][snyk-image]][snyk-url]

This contains samhammer specific and internally used helper functions for web projects.

Requirements for code to be added here:
- It's sag/project specific and not of general/public use, so that it does not make sense to create a individual lib
- It's nothing private either, that should not be publically on the internet
- It has no, or very little dependencies
   (because the deps are in all projects using the lib, even if the feaute isn't required)

Note: See this as last option and try to create individual libs as much as possible.

### Installation
pip install sag-py-web-common

## How to use
### Default routing

All requests to the main route / are redirected to /swagger if nothing specified.

```python
from sag_py_web_common.default_route import build_default_route

app: FastAPI = FastAPI(...)

app.include_router(build_default_route(ingress_base_path=config.ingress_base_path))
```

- ingress_base_path: Empty or a path starting with / if proxy hosting like kubernetes is used
- default_redirect_path: Per default /swagger but can be configured to an alternative route

### Filtered access logging

Extends the asgi-logger and adds a log entry for received requests.
Furthermore the requests are filtered, so that health checks don't spam the logs.

For requests to be filtered, they need to have the header "healthcheck" with one of these values:
"livenessprobe", "readinessprobe", "startupprobe", "prtg"

```python
from sag_py_web_common.filtered_access_logger import FilteredAccessLoggerMiddleware

app: FastAPI = FastAPI(...)

app.add_middleware(
    FilteredAccessLoggerMiddleware,
    format="Completed: %(R)s - %(st)s - %(L)s",
    logger=logging.getLogger("access"),
)
```

Also see this page for further configuration details: https://github.com/Kludex/asgi-logger

### Json exception handler

Per default fastapi falls back to text responses if there are exceptions.
That's not the desired behaviour for json api's.

This handler ensures that a json is returned. It contains the field "detail" with the exception message.

```python
from sag_py_web_common.json_exception_handler import handle_exception

app.add_exception_handler(Exception, handle_exception)
```

## How to start developing

### With vscode

Just install vscode with dev containers extension. All required extensions and configurations are prepared automatically.

### With pycharm

* Install latest pycharm
* Install pycharm plugin BlackConnect
* Install pycharm plugin Mypy
* Configure the python interpreter/venv
* pip install requirements-dev.txt
* pip install black[d]
* Ctl+Alt+S => Check Tools => BlackConnect => Trigger when saving changed files
* Ctl+Alt+S => Check Tools => BlackConnect => Trigger on code reformat
* Ctl+Alt+S => Click Tools => BlackConnect => "Load from pyproject.yaml" (ensure line length is 120)
* Ctl+Alt+S => Click Tools => BlackConnect => Configure path to the blackd.exe at the "local instance" config (e.g. C:\Python310\Scripts\blackd.exe)
* Ctl+Alt+S => Click Tools => Actions on save => Reformat code
* Restart pycharm

## How to publish
* Update the version in setup.py and commit your change
* Create a tag with the same version number
* Let github do the rest


[codeclimate-image]:https://api.codeclimate.com/v1/badges/533686a1f4d644151adb/maintainability
[codeclimate-url]:https://codeclimate.com/github/SamhammerAG/sag_py_web_common/maintainability
[coveralls-image]:https://coveralls.io/repos/github/SamhammerAG/sag_py_web_common/badge.svg?branch=master
[coveralls-url]:https://coveralls.io/github/SamhammerAG/sag_py_web_common?branch=master
[snyk-image]:https://snyk.io/test/github/SamhammerAG/sag_py_web_common/badge.svg
[snyk-url]:https://snyk.io/test/github/SamhammerAG/sag_py_web_common