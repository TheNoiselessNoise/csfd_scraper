import json
from utils import *
from urllib.parse import urlsplit
from objects import Movie

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
            ld_json = sel(s, ".main-movie > script")
            self.__MOVIE_LD_JSON = {} if ld_json is None else json.loads(text(ld_json))
        return self.__MOVIE_LD_JSON

    def parse_movie_type(self, s):
        return self.parse_movie_ld_json(s).get("@type", None)

    def parse_movie_title(self, s):
        return self.parse_movie_ld_json(s).get("name", None)

    def parse_movie_year(self, s):
        return self.parse_movie_ld_json(s).get("dateCreated", None)

    def parse_movie_duration(self, s):
        return self.parse_movie_ld_json(s).get("duration", None)

    @staticmethod
    def parse_movie_genres(s):
        genres = sel(s, ".genres")
        return None if genres is None else text(genres).split(" / ")

    @staticmethod
    def parse_movie_origins(s):
        origin = sel(s, ".origin")
        return None if origin is None else text(origin).split(", ")[0].split(" / ")

    def parse_movie_rating(self, s):
        ld_json = self.parse_movie_ld_json(s)
        rating = ld_json.get("aggregateRating", None)
        return {
            "value": rating["ratingValue"] if rating else -1,
            "count": rating["ratingCount"] if rating else -1
        }

    @staticmethod
    def parse_movie_ranks(s):
        ranks = {}
        for div in asel(s, ".film-ranking"):
            div_a = sel(div, "a")
            ranks[text(div_a)] = Globals.CSFD_URL + div_a.get("href")
        return ranks

    @staticmethod
    def parse_movie_other_names(s):
        other_names = {}
        for li in asel(s, ".film-names li"):
            other_names[sel(li, "img").get("title")] = text(li)
        return other_names

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
    def parse_movie_reviews_count(s):
        count = sel(s, ".box-reviews .count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_movie_reviews(self, s):
        reviews = {
            "count": self.parse_movie_reviews_count(s),
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
    def parse_movie_gallery_count(s):
        count = sel(s, ".tab-content section:nth-child(3) .count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_movie_gallery(self, s):
        img = sel(s, ".gallery-item picture img")
        return {
            "count": self.parse_movie_gallery_count(s),
            "image": None if img is None else url(img.get("src"))
        }

    @staticmethod
    def parse_movie_trivia_count(s):
        count = sel(s, ".tab-content section:nth-child(4) .count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_movie_trivia(self, s):
        trivia = {
            "count": self.parse_movie_trivia_count(s),
            "items": []
        }
        for article in asel(s, ".tab-content section:nth-child(4) article"):
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
    def parse_movie_plot(s):
        plot = sel(s, ".plot-full > p")
        return None if plot is None else text(plot, rec_tags=["a"])

    def parse_movie_cover(self, s):
        return self.parse_movie_ld_json(s).get("image", None)

    def parse_movie(self, s, mid):
        return Movie({
            "id": mid,
            "url": Globals.MOVIES_URL + str(mid),
            "type": self.parse_movie_type(s),
            "title": self.parse_movie_title(s),
            "year": self.parse_movie_year(s),
            "duration": self.parse_movie_duration(s),
            "genres": self.parse_movie_genres(s),
            "origins": self.parse_movie_origins(s),
            "rating": self.parse_movie_rating(s),
            "ranks": self.parse_movie_ranks(s),
            "otherNames": self.parse_movie_other_names(s),
            "creators": self.parse_movie_creators(s),
            "vods": self.parse_movie_vods(s),
            "tags": self.parse_movie_tags(s),
            "reviews": self.parse_movie_reviews(s),
            "gallery": self.parse_movie_gallery(s),
            "trivia": self.parse_movie_trivia(s),
            "premieres": self.parse_movie_premieres(s),
            "plot": self.parse_movie_plot(s),
            "cover": self.parse_movie_cover(s)
        })
