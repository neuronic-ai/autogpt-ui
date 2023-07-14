import magic
import os
import shutil
from pathlib import Path
from tempfile import TemporaryFile, mktemp
from zipfile import ZIP_DEFLATED, ZipFile

import anyio
import yaml
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse, ORJSONResponse
from humanize import filesize
from prisma import Json
from prisma.models import Bot, User
from pydantic import ValidationError

from app.api.helpers import security, bots, responses
from app.auto_gpt.api_manager import GPT_CACHE
from app.core import globals, settings
from app.helpers.system import remove_by_path
from app.schemas.bot import AiSettingsSchema, BotInCreateSchema, BotSchema, WorkspaceFileSchema
from app.schemas.enums import YesCount


CHUNK_SIZE = 1024 * 1024
router = APIRouter(dependencies=[Depends(security.check_user)])


@router.post("/", response_model=BotSchema)
async def save_bot(*, bot_in: BotInCreateSchema, user: User = Depends(security.check_user)):
    existing_bot = await Bot.prisma().find_unique(where={"user_id": user.id})
    if existing_bot:
        if existing_bot.is_active:
            raise HTTPException(status_code=400, detail=f"Bot already exists, wait for it to finish or cancel")
        await Bot.prisma().delete(where={"id": existing_bot.id})
    bot = await Bot.prisma().create(
        data={
            "fast_engine": bot_in.fast_engine,
            "smart_engine": bot_in.smart_engine,
            "fast_tokens": bot_in.fast_tokens,
            "smart_tokens": bot_in.smart_tokens,
            "image_size": bot_in.image_size,
            "ai_settings": Json(bot_in.ai_settings.dict()),
            "user_id": user.id,
            "runs_left": 1,
        }
    )
    bots.clear_workspace_cache(user.id)
    bots.build_log_path(user.id).unlink(missing_ok=True)
    job = await globals.arq_redis.enqueue_job("run_auto_gpt", bot_id=bot.id)
    await Bot.prisma().update(data={"worker_message_id": job.job_id}, where={"id": bot.id})
    return bot.dict()


@router.get("/", response_model=BotSchema)
async def get_bot(bot: Bot = Depends(bots.get_bot)):
    return bot.dict()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(bot: Bot = Depends(bots.get_bot)):
    await bots.delete_bot(bot)


@router.get("/enabled-plugins", response_class=ORJSONResponse, response_model=list[str])
async def get_enabled_plugins():
    return settings.ALLOWLISTED_PLUGINS


@router.post("/parse-settings", response_class=ORJSONResponse, response_model=AiSettingsSchema)
async def parse_ai_settings(*, file: UploadFile):
    real_file_size = 0
    settings_content = b""
    while content := await file.read(CHUNK_SIZE):
        real_file_size += len(content)
        if real_file_size > settings.MAX_WORKSPACE_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workspace file size can not be larger than "
                f"{filesize.naturalsize(settings.MAX_WORKSPACE_FILE_SIZE, binary=True)}",
            )
        settings_content += content
    try:
        return AiSettingsSchema(**yaml.safe_load(settings_content))
    except (ValueError, yaml.YAMLError) as e:
        if isinstance(e, ValidationError):
            raise HTTPException(status_code=400, detail=f"Invalid AI settings format: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid AI settings format")


@router.get("/log", response_class=ORJSONResponse)
async def get_bot_log(*, bot: Bot = Depends(bots.get_bot)):
    return await responses.build_read_log_response(bots.build_log_path(bot.user_id))


@router.get("/continue", status_code=status.HTTP_204_NO_CONTENT)
async def continue_bot(count: YesCount, bot: Bot = Depends(bots.get_bot)):
    if bot.runs_left:
        raise HTTPException(status_code=400, detail="Bot is already running")
    await Bot.prisma().update(
        data={"runs_left": count.value},
        where={"id": bot.id},
    )
    job = await globals.arq_redis.enqueue_job("run_auto_gpt", bot_id=bot.id)
    await Bot.prisma().update(data={"worker_message_id": job.job_id}, where={"id": bot.id})


@router.get("/stop", status_code=status.HTTP_204_NO_CONTENT)
async def stop_bot(bot: Bot = Depends(bots.get_bot)):
    await bots.stop_bot(bot)


@router.post("/workspace", status_code=status.HTTP_204_NO_CONTENT)
async def upload_to_workspace(*, file: UploadFile, path: str | None = None, user: User = Depends(security.check_user)):
    workspace_path = bots.build_workspace_path(user_id=user.id)
    if "/" in file.filename:
        raise HTTPException(status_code=400, detail="Name should be a path to a file, not a directory")
    if not workspace_path.exists():
        workspace_path.mkdir()
    workspace_path = bots.build_workspace_path(user_id=user.id)
    if path:
        sub_path = workspace_path / path
        if not sub_path.is_relative_to(workspace_path) or not sub_path.exists() or not sub_path.is_dir():
            raise HTTPException(status_code=400, detail="Invalid path")
    else:
        sub_path = workspace_path
    with TemporaryFile() as temp_file:
        real_file_size = 0
        while content := await file.read(CHUNK_SIZE):
            real_file_size += len(content)
            if real_file_size > settings.MAX_WORKSPACE_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Workspace file size can not be larger than "
                    f"{filesize.naturalsize(settings.MAX_WORKSPACE_FILE_SIZE, binary=True)}",
                )
            temp_file.write(content)
        temp_file.seek(0)
        async with (await anyio.open_file(sub_path / file.filename, "wb")) as w:
            await w.write(temp_file.read())


@router.get("/workspace", response_class=ORJSONResponse, response_model=list[WorkspaceFileSchema])
async def list_workspace_files(*, path: str | None = None, user: User = Depends(security.check_user)):
    workspace_path = bots.build_workspace_path(user_id=user.id)
    if path:
        sub_path = workspace_path / path
        if not sub_path.is_relative_to(workspace_path) or not sub_path.exists() or not sub_path.is_dir():
            raise HTTPException(status_code=400, detail="Invalid path")
    else:
        sub_path = workspace_path
    files = []
    for f in sub_path.glob("*"):
        if GPT_CACHE in f.parts:
            continue
        is_dir = f.is_dir()
        st_size = f.stat().st_size
        if st_size:
            size = filesize.naturalsize(st_size)
        else:
            size = None
        files.append(
            WorkspaceFileSchema(
                name=str(f.name),
                path=str(f.relative_to(workspace_path)),
                is_dir=is_dir,
                mime_type=magic.from_file(f, mime=True) if not is_dir else None,
                size=size,
            )
        )
    return files


@router.delete("/workspace", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace_file(*, name: str, user: User = Depends(security.check_user)):
    workspace_path = bots.build_workspace_path(user_id=user.id)
    file_path = workspace_path / name
    if not file_path.is_relative_to(workspace_path) or not file_path.exists():
        raise HTTPException(status_code=400, detail="Invalid file")
    if file_path.is_dir():
        shutil.rmtree(str(file_path), ignore_errors=True)
    else:
        file_path.unlink(missing_ok=True)


@router.get("/workspace/get", response_class=FileResponse)
async def get_workspace_file(
    *, name: str | None = None, user: User = Depends(security.check_user), background_tasks: BackgroundTasks
):
    workspace_path = bots.build_workspace_path(user_id=user.id)
    if name:
        if GPT_CACHE in name:
            raise HTTPException(status_code=400, detail=f"Can't list a file from `{GPT_CACHE} directory`")
        path = workspace_path / name
        if not path.exists() or not path.is_relative_to(workspace_path):
            raise HTTPException(status_code=400, detail="File does not exist in Workspace")
        if path.is_dir():
            workspace_path = path
        else:
            return FileResponse(path, filename=path.name)
    zip_path = Path(mktemp(".zip"))
    background_tasks.add_task(remove_by_path, zip_path)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zip_file:
        for path in filter(lambda f: not os.path.isdir(f) and GPT_CACHE not in f.parts, workspace_path.rglob("*")):
            zip_file.write(path, str(path.relative_to(workspace_path)))
    return FileResponse(zip_path, filename="workspace.zip")


@router.get("/workspace/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_workspace(*, user: User = Depends(security.check_user)):
    bots.clear_workspace(user.id)
