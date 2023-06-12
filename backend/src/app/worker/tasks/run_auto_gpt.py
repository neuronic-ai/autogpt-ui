import asyncio
import os

import anyio
import yaml
from asyncio import exceptions, streams
from loguru import logger
from prisma.models import Bot, User

from app.api.helpers.bots import build_prompt_settings_path, build_workspace_path, build_settings_path, build_log_path
from app.auto_gpt import cli
from app.clients import AuthBackendClient, RequestType
from app.core import globals, settings


PROMPT_SETTINGS = dict(
    constraints=[
        "~4000 word limit for short term memory. Your short term memory is short, "
        "so immediately save important information to files.",
        "If you are unsure how you previously did something or want to recall past events, "
        "thinking about similar events will help you remember.",
        "No user assistance",
        "Exclusively use the commands listed below e.g. command_name",
    ],
    resources=[
        "Internet access for searches and information gathering.",
        "Long Term memory management.",
        "GPT-3.5 powered Agents for delegation of simple tasks.",
        "File output.",
    ],
    performance_evaluations=[
        "Continuously review and analyze your actions to ensure you are performing to the best of your abilities.",
        "Constructively self-criticize your big-picture behavior constantly.",
        "Reflect on past decisions and strategies to refine your approach.",
        "Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.",
        "Write all code to a file.",
    ],
)


class ExtendedStreamReader(streams.StreamReader):
    @classmethod
    def cast(cls, some_a: streams.StreamReader):
        """Cast an A into a MyA."""
        assert isinstance(some_a, streams.StreamReader)
        some_a.__class__ = cls
        assert isinstance(some_a, ExtendedStreamReader)
        return some_a

    async def readline(self):
        """Read chunk of data from the stream until newline (b'\n') is found.

        On success, return chunk that ends with newline. If only partial
        line can be read due to EOF, return incomplete line without
        terminating newline. When EOF was reached while no bytes read, empty
        bytes object is returned.

        If limit is reached, ValueError will be raised. In that case, if
        newline was found, complete line including newline will be removed
        from internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without newline.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        sep = [b"\n", b"\r"]
        seplen = len(sep)
        try:
            line = await self.readuntil(sep)
        except exceptions.IncompleteReadError as e:
            return e.partial
        except exceptions.LimitOverrunError as e:
            if self._buffer.startswith(sep, e.consumed):
                del self._buffer[: e.consumed + seplen]
            else:
                self._buffer.clear()
            self._maybe_resume_transport()
            raise ValueError(e.args[0])
        return line

    async def readuntil(self, separator: bytes | list[bytes] = b"\n"):
        """Read data from the stream until ``separator`` is found.
        On success, the data and separator will be removed from the
        internal buffer (consumed). Returned data will include the
        separator at the end.
        Configured stream limit is used to check result. Limit sets the
        maximal length of data that can be returned, not counting the
        separator.
        If an EOF occurs and the complete separator is still not found,
        an IncompleteReadError exception will be raised, and the internal
        buffer will be reset.  The IncompleteReadError.partial attribute
        may contain the separator partially.
        If the data cannot be read because of over limit, a
        LimitOverrunError exception  will be raised, and the data
        will be left in the internal buffer, so it can be read again.
        The ``separator`` may also be an iterable of separators. In this
        case the return value will be the shortest possible that has any
        separator as the suffix. For the purposes of LimitOverrunError,
        the shortest possible separator is considered to be the one that
        matched.
        """
        if isinstance(separator, bytes):
            separator = [separator]
        else:
            # Makes sure shortest matches wins, and supports arbitrary iterables
            separator = sorted(separator, key=len)
        if not separator:
            raise ValueError("Separator should contain at least one element")
        min_seplen = len(separator[0])
        max_seplen = len(separator[-1])
        if min_seplen == 0:
            raise ValueError("Separator should be at least one-byte string")

        if self._exception is not None:
            raise self._exception

        # Consume whole buffer except last bytes, which length is
        # one less than max_seplen. Let's check corner cases with
        # separator[-1]='SEPARATOR':
        # * we have received almost complete separator (without last
        #   byte). i.e buffer='some textSEPARATO'. In this case we
        #   can safely consume len(separator) - 1 bytes.
        # * last byte of buffer is first byte of separator, i.e.
        #   buffer='abcdefghijklmnopqrS'. We may safely consume
        #   everything except that last byte, but this require to
        #   analyze bytes of buffer that match partial separator.
        #   This is slow and/or require FSM. For this case our
        #   implementation is not optimal, since require rescanning
        #   of data that is known to not belong to separator. In
        #   real world, separator will not be so long to notice
        #   performance problems. Even when reading MIME-encoded
        #   messages :)

        # `offset` is the number of bytes from the beginning of the buffer
        # where there is no occurrence of any `separator`.
        offset = 0

        # Loop until we find a `separator` in the buffer, exceed the buffer size,
        # or an EOF has happened.
        while True:
            buflen = len(self._buffer)

            # Check if we now have enough data in the buffer for shortest
            # separator to fit.
            if buflen - offset >= min_seplen:
                match_start = None
                match_end = None
                for sep in separator:
                    isep = self._buffer.find(sep, offset)

                    if isep != -1:
                        # `separator` is in the buffer. `match_start` and
                        # `match_end` will be used later to retrieve the
                        # data.
                        end = isep + len(sep)
                        if match_end is None or end < match_end:
                            match_end = end
                            match_start = isep
                if match_end is not None:
                    break

                # see upper comment for explanation.
                offset = max(0, buflen + 1 - max_seplen)
                if offset > self._limit:
                    raise exceptions.LimitOverrunError("Separator is not found, and chunk exceed the limit", offset)

            # Complete message (with full separator) may be present in buffer
            # even when EOF flag is set. This may happen when the last chunk
            # adds data which makes separator be found. That's why we check for
            # EOF *after* inspecting the buffer.
            if self._eof:
                chunk = bytes(self._buffer)
                self._buffer.clear()
                raise exceptions.IncompleteReadError(chunk, None)

            # _wait_for_data() will resume reading if stream was paused.
            await self._wait_for_data("readuntil")

        if match_start > self._limit:
            raise exceptions.LimitOverrunError("Separator is found, but chunk is longer than limit", match_start)

        chunk = self._buffer[:match_end]
        del self._buffer[:match_end]
        self._maybe_resume_transport()
        return bytes(chunk)


CMD = (
    "{binary} "
    "{cli_path} "
    "-w {workspace_folder} "
    "-C {settings_path} "
    "-P {prompt_settings} "
    "--max-cache-size={max_cache_size} "
    "--skip-news "
    "--skip-reprompt"
)


def build_command(bot: Bot):
    ai_settings_path = build_settings_path(bot.user_id)
    with open(ai_settings_path, "w") as w:
        yaml.dump(bot.ai_settings, w)
    prompt_settings_path = build_prompt_settings_path(bot.user_id)
    with open(prompt_settings_path, "w") as w:
        yaml.dump(PROMPT_SETTINGS, w)
    cmd = CMD.format(
        binary=settings.PYTHON_BINARY,
        cli_path=cli.__file__,
        workspace_folder=build_workspace_path(bot.user_id),
        settings_path=ai_settings_path,
        prompt_settings=prompt_settings_path,
        max_cache_size=settings.MAX_CACHE_SIZE,
    )
    return cmd


async def run(ctx, bot_id: int):
    bot = await Bot.prisma().find_unique(where={"id": bot_id})

    user = await User.prisma().find_unique(where={"id": bot.user_id})
    auth_client = AuthBackendClient(
        settings.SESSION_API_URL,
        user_path=settings.SESSION_API_USER_PATH,
        session_path=settings.SESSION_API_SESSION_PATH,
        session_cookie=settings.SESSION_COOKIE,
    )
    if settings.NO_AUTH:
        openai_key = settings.OPENAI_LOCAL_KEY
    else:
        openai_key = (await auth_client.get_user(RequestType.userdata, username=user.username))["openai"]
    disabled_command_categories = []
    if not settings.ALLOW_CODE_EXECUTION:
        disabled_command_categories.append("autogpt.commands.execute_code")
    proc = await asyncio.create_subprocess_shell(
        build_command(bot),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={
            "OPENAI_API_KEY": openai_key,
            "FAST_TOKEN_LIMIT": str(bot.fast_tokens),
            "SMART_TOKEN_LIMIT": str(bot.smart_tokens),
            "FAST_LLM_MODEL": bot.fast_engine,
            "SMART_LLM_MODEL": bot.smart_engine,
            "IMAGE_SIZE": str(bot.image_size),
            "USE_WEB_BROWSER": "firefox",
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
            "PATH": os.environ.get("PATH"),
            "WDM_PROGRESS_BAR": "0",
            "EXECUTE_LOCAL_COMMANDS": str(settings.EXECUTE_LOCAL_COMMANDS),
            "DISABLED_COMMAND_CATEGORIES": ",".join(disabled_command_categories),
            "DENY_COMMANDS": ",".join(settings.DENY_COMMANDS),
            "ALLOW_COMMANDS": ",".join(settings.ALLOW_COMMANDS),
        },
    )
    log_path = build_log_path(bot.user_id)
    ExtendedStreamReader.cast(proc.stdout)
    is_carriage = False
    buf: bytes | None = None
    prev_buf: bytes | None = None
    prev_prev_buf: bytes | None = None
    async with (await anyio.open_file(log_path, "a+")) as w:
        while proc.returncode is None:
            prev_prev_buf = prev_buf
            prev_buf = buf
            buf = await proc.stdout.readline()
            if not buf:
                break
            if b"\r" in buf:
                if not is_carriage:
                    is_carriage = True
                    await w.write(buf.decode())
                else:
                    continue
            else:
                is_carriage = False
            await w.write(buf.decode())
            await w.flush()
    await proc.wait()
    if proc.returncode != 0:
        logger.warning(f"Bot {bot.id} exited with non 0 return code: {proc.returncode}")
        await Bot.prisma().update(
            data={"is_failed": True, "is_active": False, "runs_left": 0, "worker_message_id": None},
            where={"id": bot.id},
        )
        if proc.stderr:
            with open(log_path, "a+") as w:
                w.write((await proc.stderr.read()).decode())
        return None
    if prev_prev_buf and b"Shutting down..." in prev_prev_buf:
        logger.info(f"Bot {bot.id} finished")
        await Bot.prisma().update(
            data={"is_active": False, "runs_left": 0, "worker_message_id": None}, where={"id": bot.id}
        )
        return None
    await Bot.prisma().update(data={"runs_left": bot.runs_left - 1, "worker_message_id": None}, where={"id": bot.id})
    if bot.runs_left <= 1:
        return None
    job = await globals.arq_redis.enqueue_job("run_auto_gpt", bot_id=bot.id)
    await Bot.prisma().update(data={"worker_message_id": job.job_id}, where={"id": bot.id})
