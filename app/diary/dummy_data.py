from enum import Enum


class ModelName(str, Enum):
    KIM = "KIM"
    YONGKI = "YONGKI"


class EmotionColor(str, Enum):
    blue = "backgroundColor2"
    unknown = "backgroundColor3"
    happy = "backgroundColor4"
    mood = "backgroundColor5"
    angry = "backgroundColor6"
