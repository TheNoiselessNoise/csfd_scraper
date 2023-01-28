from utils import tojson
from enum import Enum

class CreatorFilmographySort(Enum):
    BEST   = "sort_average"
    NEWEST = "year"
    RATING = "rating_count"

class Movie:
    def __init__(self, args):
        self.args = args
        self.id = args.get("id", None)
        self.url = args.get("url", None)
        self.type = args.get("type", None)
        self.title = args.get("title", None)
        self.year = args.get("year", None)
        self.duration = args.get("duration", None)
        self.genres = args.get("genres", None)
        self.origins = args.get("origins", None)
        self.rating = args.get("rating", None)
        self.ranks = args.get("ranks", None)
        self.otherNames = args.get("otherNames", None)
        self.creators = args.get("creators", None)
        self.vods = args.get("vods", None)
        self.tags = args.get("tags", None)
        self.reviews = args.get("reviews", None)
        self.gallery = args.get("gallery", None)
        self.trivia = args.get("trivia", None)
        self.premieres = args.get("premieres", None)
        self.plot = args.get("plot", None)
        self.cover = args.get("cover", None)

    def __str__(self):
        return tojson(self.args)

class Creator:
    def __init__(self, args):
        self.args = args
        self.id = args.get("id", None)
        self.url = args.get("url", None)
        self.type = args.get("type", None)
        self.name = args.get("name", None)
        self.age = args.get("age", None)
        self.birth = args.get("birth", None)
        self.bio = args.get("bio", None)
        self.ranks = args.get("ranks", None)
        self.trivia = args.get("trivia", None)
        self.gallery = args.get("gallery", None)
        self.filmography = args.get("filmography", None)
        self.image = args.get("image", None)

    def __str__(self):
        return tojson(self.args)
