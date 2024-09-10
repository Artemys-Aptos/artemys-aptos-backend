from enum import Enum


class PromptTagEnum(str, Enum):
    ART_3D = "3D Art"
    ANIME = "Anime"
    PHOTOGRAPHY = "Photography"
    VECTOR = "Vector"
    OTHER = "Other"
    SCIFI = "Sci-Fi"
    FANTASY = "Fantasy"
    MYSTERY = "Mystery"
    THRILLER = "Thriller"
    ROMANCE = "Romance"
    WESTERN = "Western"
    ACTION = "Action"
    ADVENTURE = "Adventure"
    COMEDY = "Comedy"
    

class PromptTypeEnum(str, Enum):
    PUBLIC = "public"
    PREMIUM = "premium"