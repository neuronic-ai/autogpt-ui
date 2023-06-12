from arq.connections import ArqRedis

from app.core import settings

__all__ = [
    "arq_redis",
]

arq_redis = ArqRedis.from_url(settings.REDIS_URL)
