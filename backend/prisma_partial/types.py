from prisma.models import Bot


Bot.create_partial(
    "BotSchema",
    include={
        "fast_engine",
        "smart_engine",
        "image_size",
        "fast_tokens",
        "smart_tokens",
        "ai_settings",
        "is_active",
        "is_failed",
        "runs_left",
    },
)
Bot.create_partial(
    "BotInCreateSchema",
    include={
        "fast_engine",
        "smart_engine",
        "image_size",
        "fast_tokens",
        "smart_tokens",
        "ai_settings",
    },
)
