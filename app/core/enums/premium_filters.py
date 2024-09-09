from enum import Enum

class PremiumPromptFilterType(str, Enum):
    RECENT = "recent"
    POPULAR = "popular"
    TRENDING = "trending"