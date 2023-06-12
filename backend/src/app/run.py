import uvicorn

from app import create_app
from core import init_logging

if __name__ == "__main__":
    init_logging.init_logging()
    uvicorn.run(create_app(), host="0.0.0.0", port=8040)
