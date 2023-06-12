from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from prisma.models import User
from starlette.status import HTTP_204_NO_CONTENT

from app.api.helpers import security


router = APIRouter()


@router.get("/check", status_code=HTTP_204_NO_CONTENT, response_class=ORJSONResponse)
async def check_session(*, _: User = Depends(security.check_user)):
    pass
