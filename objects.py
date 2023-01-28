from utils import tojson

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
