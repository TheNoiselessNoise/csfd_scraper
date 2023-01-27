import json
from utils import *
from urllib.parse import urlsplit

class MovieParser:
    __MOVIE_LD_JSON = None
    __VOD_BLOCKED_HOSTS = [
        "www.facebook.com",
        "twitter.com"
    ]

    def reset(self):
        self.__MOVIE_LD_JSON = None

    def parse_movie_ld_json(self, s):
        if not self.__MOVIE_LD_JSON:
            self.__MOVIE_LD_JSON = json.loads(text(s, ".main-movie > script"))
        return self.__MOVIE_LD_JSON

    def parse_movie_type(self, s):
        return self.parse_movie_ld_json(s)["@type"]

    def parse_movie_title(self, s):
        return self.parse_movie_ld_json(s)["name"]

    def parse_movie_year(self, s):
        return self.parse_movie_ld_json(s)["dateCreated"]

    def parse_movie_duration(self, s):
        return self.parse_movie_ld_json(s)["duration"]

    @staticmethod
    def parse_movie_genres(s):
        return text(s, ".genres").split(" / ")

    @staticmethod
    def parse_movie_origins(s):
        return text(s, ".origin").split(", ")[0].split(" / ")

    def parse_movie_rating(self, s):
        ld_json = self.parse_movie_ld_json(s)
        return {
            "value": ld_json["aggregateRating"]["ratingValue"],
            "count": ld_json["aggregateRating"]["ratingCount"]
        }

    @staticmethod
    def parse_movie_other_names(s):
        return {
            sel(li, "img").get("title"): text(li)
            for li in asel(s, ".film-names li")
        }

    @staticmethod
    def parse_movie_creators(s):
        creators = {}
        for div in asel(s, ".creators > div"):
            name = text(div, "h4").split(":")[0]
            creators_by_type = []

            for link in asel(div, "a"):
                href = link.get("href")
                if href.startswith("/tvurce/") and href.endswith("/"):
                    creators_by_type.append({
                        "id": extract_id(link.get("href")),
                        "name": text(link),
                        "url": Globals.CSFD_URL + href,
                    })
            creators[name] = creators_by_type
        return creators

    def parse_movie_vods(self, s):
        vods = {}
        for a in asel(s, ".box-buttons > a"):
            parsed_url = urlsplit(a.get("href"))
            if parsed_url.hostname not in self.__VOD_BLOCKED_HOSTS:
                vods[text(a)] = a.get("href")
        return vods

    @staticmethod
    def parse_movie_tags(s):
        tags = {}
        for a in asel(s, "aside > section:last-child > .box-content > a"):
            tags[text(a)] = {
                "id": a.get("href").split("=")[1],
                "url": Globals.CSFD_URL + a.get("href"),
            }
        return tags

    @staticmethod
    def parse_movie_reviews(s):
        reviews = {
            "count": int(text(s, ".box-reviews .count")[1:-1]),
            "items": []
        }
        for article in asel(s, ".box-reviews .box-content article"):
            user_a = sel(article, ".user-title a")
            stars = sel(article, ".user-title .stars").get("class")
            reviews["items"].append({
                "user_id": extract_id(user_a.get("href")),
                "author": text(user_a),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(article, ".comment-date time"),
                "text": clean(text(article, ".article-content p", rec_tags=["a", "em"])),
            })
        return reviews

    @staticmethod
    def parse_movie_gallery(s):
        section = sel(s, ".tab-content section:nth-child(3)")
        return {
            "count": int(text(section, ".count")[1:-1]),
            "initial": url(sel(section, "img").get("src"))
        }

    @staticmethod
    def parse_movie_trivia(s):
        trivia = {
            "count": int(text(s, ".tab-content section:last-child .count")[1:-1]),
            "items": []
        }
        for article in asel(s, ".tab-content section:last-child article"):
            user_a = sel(article, ".span-more-small a")
            user_id = -1 if user_a is None else extract_id(user_a.get("href"))
            user_a = user_a or sel(article, ".span-more-small")
            trivia["items"].append({
                "user_id": user_id,
                "author": text(user_a),
                "text": clean(text(article, "li", rec_tags=["a", "em"]))
            })
        return trivia

    @staticmethod
    def parse_movie_premieres(s):
        premieres = []
        for li in asel(s, ".box-premieres li"):
            where = text(li, "p")
            when_tag = asel(li, "span")[1]
            when = clean(text(when_tag))
            premieres.append({
                "country": sel(li, ".item-img img").get("title"),
                "where": where[:where.rindex(" ")],
                "when": when[:when.index(" ")],
                "by": when[when.index(" ") + 1:],
            })
        return premieres

    @staticmethod
    def parse_movie_description(s):
        return text(s, ".plot-preview > p", rec_tags=["a"])

    def parse_movie_cover(self, s):
        return self.parse_movie_ld_json(s)["image"]

    def parse_movie(self, s, mid):
        return {
            "id": mid,
            "url": Globals.MOVIES_URL + str(mid),
            "type": self.parse_movie_type(s),
            "title": self.parse_movie_title(s),
            "year": self.parse_movie_year(s),
            "duration": self.parse_movie_duration(s),
            "genres": self.parse_movie_genres(s),
            "origins": self.parse_movie_origins(s),
            "rating": self.parse_movie_rating(s),
            "otherNames": self.parse_movie_other_names(s),
            "creators": self.parse_movie_creators(s),
            "vods": self.parse_movie_vods(s),
            "tags": self.parse_movie_tags(s),
            "reviews": self.parse_movie_reviews(s),
            "gallery": self.parse_movie_gallery(s),
            "trivia": self.parse_movie_trivia(s),
            "premieres": self.parse_movie_premieres(s),
            "description": self.parse_movie_description(s),
            "cover": self.parse_movie_cover(s),
        }
