from itertools import islice
from pathlib import Path
from typing import Awaitable, Callable

import anyio
from fastapi.responses import FileResponse, ORJSONResponse
from typing_extensions import ParamSpec
from app.helpers.readers import any_open, is_gz, tail_as_text
from app.core import settings

P = ParamSpec("P")


async def build_read_log_response(path: Path) -> ORJSONResponse:
    if not path.exists() and is_gz(path):
        path = path.with_suffix("")
    text = ""
    if path.exists():
        if is_gz(path):
            with any_open(path, "rt") as r:
                text = "".join([row for row in islice(r, 0, 1000)])
        elif path.suffix == ".log":
            text = await anyio.to_thread.run_sync(tail_as_text, path, settings.TAIL_LOG_COUNT)
        else:
            text = await anyio.to_thread.run_sync(tail_as_text, path, 10000)
    return ORJSONResponse(
        {"text": text},
    )


async def build_download_log_response(
    func: Callable[P, Awaitable[Path]], *args: P.args, **kwargs: P.kwargs
) -> FileResponse:
    path = await func(*args, **kwargs)
    if not path.exists():
        path.touch()
    return FileResponse(path, filename=path.name)
