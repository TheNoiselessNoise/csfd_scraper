from urllib.parse import urlsplit
from src.csfd_utils import *
from src.csfd_objects import *

class CreatorParser:
    __CREATOR_LD_JSON = None

    def reset(self):
        self.__CREATOR_LD_JSON = None

    def parse_movie_ld_json(self, s):
        if not self.__CREATOR_LD_JSON:
            ld_json = sel(s, ".creator-main > script")
            self.__CREATOR_LD_JSON = {} if ld_json is None else json.loads(text(ld_json))
        return self.__CREATOR_LD_JSON

    def parse_creator_type(self, s):
        return self.parse_movie_ld_json(s).get("@type", None)

    def parse_creator_name(self, s):
        return self.parse_movie_ld_json(s).get("name", None)

    @staticmethod
    def parse_creator_age(s):
        content = sel(s, ".creator-profile-content-desc > p")
        age = None if content is None else clean(text(content))
        return None if not age else int(age.split(" ")[2][1:])

    def parse_creator_birth_date(self, s):
        return self.parse_movie_ld_json(s).get("birthDate", None)

    def parse_creator_birth_place(self, s):
        place = self.parse_movie_ld_json(s).get("birthPlace", None)
        return None if place is None else place.get("name", None)

    @staticmethod
    def parse_creator_bio(s):
        bio = sel(s, ".article-content p")
        return None if bio is None else clean(text(bio))

    @staticmethod
    def parse_creator_trivia_count(s):
        article = sel(s, ".article-trivia")
        section = None if article is None else article.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_creator_trivia(self, s):
        trivia = {
            "total": self.parse_creator_trivia_count(s),
            "items": []
        }
        for article in asel(s, ".article-trivia"):
            a = sel(article, "header a")
            user_a = sel(article, ".span-more-small a")
            user_id = -1 if user_a is None else extract_id(user_a.get("href"))
            user_a = user_a or sel(article, ".span-more-small")
            trivia["items"].append({
                "movie_id": extract_id(a.get("href")),
                "movie": text(a),
                "author_id": user_id,
                "author": text(user_a),
                "text": clean(text(article, "li", rec_tags=["a", "em"]))
            })
        return trivia

    @staticmethod
    def parse_creator_ranks(s):
        ranks = {}
        for div in asel(s, ".ranking"):
            div_a = sel(div, "a")
            ranks[text(div_a)] = Globals.CSFD_URL + div_a.get("href")
        return ranks

    @staticmethod
    def parse_creator_gallery_count(s):
        gallery_item = sel(s, ".gallery-item")
        section = None if gallery_item is None else gallery_item.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_creator_gallery(self, s):
        img = sel(s, ".gallery-item picture img")
        return {
            "total": self.parse_creator_gallery_count(s),
            "image": None if img is None else url(img.get("src"))
        }

    @staticmethod
    def parse_creator_filmography(s):
        div = sel(s, ".creator-filmography")

        if div is None:
            return None

        filmography = {}

        for section in asel(div, "section"):
            section_name = text(section, "header h2")
            year = None

            filmography[section_name] = {}
            for table in asel(section, "table"):
                table_name = text(table, "th")

                filmography[section_name][table_name] = {}
                for tr in asel(table, "tr:not(:first-child)"):
                    tr_year = clean(text(tr, "td.year"))
                    if tr_year.isnumeric():
                        year = int(tr_year)

                    if year not in filmography[section_name][table_name]:
                        filmography[section_name][table_name][year] = []

                    td_name = sel(tr, "td.name")
                    td_a = sel(td_name, "a")
                    filmography[section_name][table_name][year].append({
                        "id": extract_id(td_a.get("href")),
                        "name": text(td_a)
                    })

        return filmography

    def parse_creator_image(self, s):
        return url(self.parse_movie_ld_json(s).get("image", None))

    def parse_creator(self, s, cid):
        return Creator({
            "id": cid,
            "url": Globals.CREATORS_URL + str(cid),
            "type": self.parse_creator_type(s),
            "name": self.parse_creator_name(s),
            "age": self.parse_creator_age(s),
            "birth": {
                "date": self.parse_creator_birth_date(s),
                "place": self.parse_creator_birth_place(s)
            },
            "bio": self.parse_creator_bio(s),
            "trivia": self.parse_creator_trivia(s),
            "ranks": self.parse_creator_ranks(s),
            "gallery": self.parse_creator_gallery(s),
            "filmography": self.parse_creator_filmography(s),
            "image": self.parse_creator_image(s),
        })

class SearchParser:

    # MOVIES

    @staticmethod
    def parse_movies_search_movies(s):
        movies = []
        for tr in asel(s, "table tbody tr"):
            movie_a = sel(tr, "a")
            movies.append(SearchedMovie({
                "id": extract_id(movie_a.get("href")),
                "name": text(movie_a),
                "year": int(text(tr, "span.info")[1:-1]),
                "origins": text(tr, "td.origin").split(" / "),
                "genres": text(tr, "td.genre").split(" / "),
            }))
        return movies

    @staticmethod
    def parse_movies_search_has_prev_page(s):
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_movies_search_has_next_page(s):
        return sel(s, ".page-next") is not None

    def parse_movies_search(self, s, page) -> SearchMoviesResult:
        return SearchMoviesResult({
            "page": page,
            "movies": self.parse_movies_search_movies(s),
            "has_prev_page": self.parse_movies_search_has_prev_page(s),
            "has_next_page": self.parse_movies_search_has_next_page(s),
        })

    # CREATORS

    @staticmethod
    def parse_creators_search_creators(s):
        movies = []
        for tr in asel(s, "table tbody tr"):
            movie_a = sel(tr, "a")
            birth_year = text(tr, ".author-birthday").split(" ")
            movies.append(SearchedCreator({
                "id": extract_id(movie_a.get("href")),
                "name": text(movie_a),
                "birth_year": None if len(birth_year) == 1 else int(birth_year[1]),
                "types": text(tr, ".author-dos").split(" / "),
            }))
        return movies

    @staticmethod
    def parse_creators_search_has_prev_page(s):
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_creators_search_has_next_page(s):
        return sel(s, ".page-next") is not None

    def parse_creators_search(self, s, page):
        return SearchCreatorsResult({
            "page": page,
            "creators": self.parse_creators_search_creators(s),
            "has_prev_page": self.parse_creators_search_has_prev_page(s),
            "has_next_page": self.parse_creators_search_has_next_page(s),
        })

    # TEXT SEARCH

    @staticmethod
    def __parse_text_search_parse_creators(s, name):
        creators = []
        for p in asel(s, ".film-creators"):
            if text(p).split(":")[0] == name:
                for a in asel(p, "a"):
                    creators.append({
                        "id": extract_id(a.get("href")),
                        "name": text(a),
                    })
        return creators

    def parse_text_search_movies(self, s) -> List[TextSearchedMovie]:
        movies = []
        for article in asel(s, ".main-movies article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            origins_genres = text(article, ".film-origins-genres .info").split(", ")
            movies.append(TextSearchedMovie({
                "id": extract_id(articla_a.get("href")),
                "name": text(articla_a),
                "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
                "origins": origins_genres[:-1],
                "directors": self.__parse_text_search_parse_creators(article, "Režie"),
                "actors": self.__parse_text_search_parse_creators(article, "Hrají"),
                "performers": self.__parse_text_search_parse_creators(article, "Účinkují"),
                "image": None if img_url.startswith("data:image") else url(img_url)
            }))
        return movies

    @staticmethod
    def parse_text_search_creators(s) -> List[TextSearchedCreator]:
        creators = []
        for article in asel(s, ".main-authors article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            creators.append(TextSearchedCreator({
                "id": extract_id(articla_a.get("href")),
                "name": text(articla_a),
                "types": text(article, ".article-content .info").split(" / "),
                "image": None if img_url.startswith("data:image") else url(img_url)
            }))
        return creators

    def parse_text_search_series(self, s) -> List[TextSearchedSeries]:
        series = []
        for article in asel(s, ".main-series article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            origins_genres = text(article, ".film-origins-genres .info").split(", ")
            series.append(TextSearchedSeries({
                "id": extract_id(articla_a.get("href")),
                "name": text(articla_a),
                "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
                "origins": origins_genres[:-1],
                "directors": self.__parse_text_search_parse_creators(article, "Režie"),
                "actors": self.__parse_text_search_parse_creators(article, "Hrají"),
                "performers": self.__parse_text_search_parse_creators(article, "Účinkují"),
                "image": None if img_url.startswith("data:image") else url(img_url)
            }))
        return series

    @staticmethod
    def parse_text_search_users(s) -> List[TextSearchedUser]:
        users = []
        for article in asel(s, ".main-users article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            users.append(TextSearchedUser({
                "id": extract_id(articla_a.get("href")),
                "name": text(articla_a),
                "real_name": text(article, ".article-content .user-real-name"),
                "points": int(text(article, ".article-content p:last-child").split(" ")[0]),
                "image": None if img_url.startswith("data:image") else url(img_url)
            }))
        return users

    def parse_text_search(self, s) -> TextSearchResult:
        return TextSearchResult({
            "movies": self.parse_text_search_movies(s),
            "creators": self.parse_text_search_creators(s),
            "series": self.parse_text_search_series(s),
            "users": self.parse_text_search_users(s)
        })

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
                        "name": text(link)
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
            tags[text(a)] = a.get("href").split("=")[1]
        return tags

    @staticmethod
    def parse_movie_reviews_count(s):
        count = sel(s, ".box-reviews .count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_movie_reviews(self, s):
        reviews = {
            "total": self.parse_movie_reviews_count(s),
            "items": []
        }
        for article in asel(s, ".box-reviews article"):
            user_a = sel(article, ".user-title a")
            stars = sel(article, ".user-title .stars").get("class")
            reviews["items"].append({
                "author_id": extract_id(user_a.get("href")),
                "author": text(user_a),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(article, ".comment-date time"),
                "text": clean(text(article, ".article-content p", rec_tags=["a", "em"])),
            })
        return reviews

    @staticmethod
    def parse_movie_gallery_count(s):
        gallery_item = sel(s, ".gallery-item")
        section = None if gallery_item is None else gallery_item.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_movie_gallery(self, s):
        img = sel(s, ".gallery-item picture img")
        return {
            "total": self.parse_movie_gallery_count(s),
            "image": None if img is None else url(img.get("src"))
        }

    @staticmethod
    def parse_movie_trivia_count(s):
        article = sel(s, ".article-trivia")
        section = None if article is None else article.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else int(text(count)[1:-1])

    def parse_movie_trivia(self, s):
        trivia = {
            "total": self.parse_movie_trivia_count(s),
            "items": []
        }
        for article in asel(s, ".article-trivia"):
            user_a = sel(article, ".span-more-small a")
            user_id = -1 if user_a is None else extract_id(user_a.get("href"))
            user_a = user_a or sel(article, ".span-more-small")
            trivia["items"].append({
                "author_id": user_id,
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
