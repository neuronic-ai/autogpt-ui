import gzip
import os
from pathlib import Path
from typing import IO, Generator, List, Optional, Union


def is_gz(path: Union[str, Path]) -> bool:
    if isinstance(path, str):
        path = Path(path)
    return path.suffix == ".gz"


def any_open(path: Union[str, Path], mode: Optional[str] = None) -> Union[gzip.GzipFile, IO]:
    if is_gz(path):
        return gzip.open(path, mode or "rb")
    else:
        return open(path, mode or "r")


def tail(f: Union[str, Path, IO, gzip.GzipFile], lines: int = 1, _buffer: int = 4098) -> Generator[str, None, None]:
    """Tail a file and get X lines from the end"""
    if isinstance(f, (str, Path)):
        with any_open(f, "rb") as r:
            yield from tail(r, lines, _buffer)
    else:
        f.seek(0, os.SEEK_END)
        block_end_byte = f.tell()
        lines_to_go = lines
        block_number = -1
        blocks = []
        while lines_to_go > 0 and block_end_byte > 0:
            if block_end_byte - _buffer > 0:
                f.seek(block_number * _buffer, os.SEEK_END)
                blocks.append(f.read(_buffer))
            else:
                f.seek(0, 0)
                blocks.append(f.read(block_end_byte))
            lines_found = blocks[-1].count(b"\n")
            lines_to_go -= lines_found
            block_end_byte -= _buffer
            block_number -= 1
        all_read_text = b"".join(reversed(blocks))
        for row in all_read_text.splitlines()[-lines:]:
            yield row.decode()


def tail_as_text(f: Union[str, Path, IO, gzip.GzipFile], lines: int = 1, _buffer: int = 4098) -> str:
    return "\n".join(tail(f, lines, _buffer))


def tail_as_list(f: Union[str, Path, IO, gzip.GzipFile], lines: int = 1, _buffer: int = 4098) -> List[str]:
    return list(tail(f, lines, _buffer))
