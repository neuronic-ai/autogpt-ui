import asyncio
from pathlib import Path
from typing import Optional, Tuple


async def run_command(cmd: str) -> Tuple[Optional[int], str, str]:
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(), stderr.decode()


async def remove_by_path(path: Path) -> None:
    path.unlink(missing_ok=True)
