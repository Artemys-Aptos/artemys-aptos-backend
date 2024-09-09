from enum import Enum


class PromptTagEnum(str, Enum):
    ART_3D = "3D Art"
    ANIME = "Anime"
    PHOTOGRAPHY = "Photography"
    VECTOR = "Vector"
    OTHER = "Other"
    
    

class PromptTypeEnum(str, Enum):
    PUBLIC = "public"
    PREMIUM = "premium"