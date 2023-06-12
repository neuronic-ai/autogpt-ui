import shutil
from pathlib import Path

from fastapi import Depends, HTTPException, status
from prisma.models import Bot, User

from app.api.helpers.security import check_user
from app.auto_gpt.api_manager import GPT_CACHE
from app.core import settings
from app.helpers.jobs import abort_job


async def get_bot(user: User = Depends(check_user)) -> Bot:
    bot = await Bot.prisma().find_unique(where={"user_id": user.id})
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified bot does not exit")
    return bot


async def delete_bot(bot: Bot) -> None:
    if bot.worker_message_id:
        await abort_job(bot.worker_message_id)
    await Bot.prisma().delete(where={"id": bot.id})


async def stop_bot(bot: Bot) -> None:
    if bot.worker_message_id:
        await abort_job(bot.worker_message_id)
    await Bot.prisma().update(data={"is_active": False}, where={"id": bot.id})


def build_workspace_path(user_id: int, fmt: str | None = None, suffix: str | None = None) -> Path:
    key = f"user_{user_id}"
    if suffix:
        key = f"{key}_{suffix}"
    if fmt:
        return settings.WORKSPACES_DIR / f"{key}.{fmt}"
    return settings.WORKSPACES_DIR / key


def build_prompt_settings_path(user_id: int) -> Path:
    return build_workspace_path(user_id, fmt="yaml", suffix="prompt")


def build_settings_path(user_id: int) -> Path:
    return build_workspace_path(user_id, fmt="yaml")


def build_log_path(user_id: int) -> Path:
    return build_workspace_path(user_id, fmt="log")


def clear_workspace(user_id: int) -> None:
    shutil.rmtree(str(settings.WORKSPACES_DIR / f"user_{user_id}"), ignore_errors=True)


def clear_workspace_cache(user_id: int) -> None:
    shutil.rmtree(str(settings.WORKSPACES_DIR / f"user_{user_id}" / GPT_CACHE), ignore_errors=True)
