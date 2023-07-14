from enum import Enum, IntEnum


class LLMEngine(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"


class ImageSize(IntEnum):
    s512 = 512
    s1024 = 1024


class EngineTokens(IntEnum):
    t1000 = 1000
    t2000 = 2000
    t3000 = 3000
    t4000 = 4000
    t8000 = 8000
    t32000 = 32000


class YesCount(IntEnum):
    c1 = 1
    c5 = 5
    c10 = 10
    c20 = 20
    c50 = 50
    c100 = 100
    c200 = 200
