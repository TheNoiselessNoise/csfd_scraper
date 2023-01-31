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
        return -1 if count is None else toint(text(count))

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
        return -1 if count is None else toint(text(count))

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
        return -1 if count is None else toint(text(count))

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
        return -1 if count is None else toint(text(count))

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
        return -1 if count is None else toint(text(count))

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
            "other_names": self.parse_movie_other_names(s),
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

class UserParser:

    @staticmethod
    def parse_user_name(s):
        return text(s, ".user-profile h1")

    @staticmethod
    def parse_user_real_name(s):
        return text(s, ".user-profile-content > p > strong")

    @staticmethod
    def parse_user_origin(s):
        p = sel(s, ".user-profile-content > p")
        return clean(p.contents[3]).split(", ")

    @staticmethod
    def parse_user_about(s):
        p = sel(s, ".user-profile-content > p")
        return clean(p.contents[5])

    @staticmethod
    def parse_user_registered(s):
        user_footer = sel(s, ".user-profile-footer-left")
        return clean(text(user_footer)).split(" ")[3]

    @staticmethod
    def parse_user_last_login(s):
        user_footer = sel(s, ".user-profile-footer-left")
        parts = clean(text(user_footer)).split(" ")
        return f"{parts[6]} {parts[7]}"

    @staticmethod
    def parse_user_points(s):
        points_a = sel(s, ".ranking-points a")
        return None if points_a is None else int("".join(clean(text(points_a)).split(" ")[:-1]))

    @staticmethod
    def parse_user_awards(s):
        awards = {}
        for a in asel(s, ".ranking:not(.ranking-points) a"):
            awards[text(a)] = a.get("href")
        return awards

    @staticmethod
    def parse_user_most_watched_genres(s):
        most_watched_genres = {}
        for li in asel(s, ".genres-switch li"):
            meter = int(sel(li, ".meter").get("style").split(" ")[1][:-1])
            most_watched_genres[text(li)] = meter
        return most_watched_genres

    @staticmethod
    def parse_user_most_watched_types(s):
        most_watched_types = {}
        for li in asel(s, ".types-switch li"):
            span_text = sel(li, "span").get("title")
            meter = int(sel(li, ".meter").get("style").split(" ")[1][:-1])
            most_watched_types[span_text] = meter
        return most_watched_types

    @staticmethod
    def parse_user_most_watched_origins(s):
        most_watched_origins = {}
        for li in asel(s, ".origins-switch li"):
            span_text = sel(li, "span").get("title")
            meter = int(sel(li, ".meter").get("style").split(" ")[1][:-1])
            most_watched_origins[span_text] = meter
        return most_watched_origins

    @staticmethod
    def parse_user_reviews_count(s):
        section = sel(s, ".user-reviews")
        return -1 if section is None else toint(clean(text(section, ".count")))

    def parse_user_reviews(self, s):
        reviews = {
            "total": self.parse_user_reviews_count(s),
            "last": []
        }
        for article in asel(s, ".user-reviews article.article"):
            article_a = sel(article, "header a")
            img_href = sel(article, "img").get("src")
            stars = sel(article, ".stars").get("class")
            reviews["last"].append({
                "id": extract_id(article_a.get("href")),
                "name": text(article_a),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(article, "time"),
                "text": text(article, ".user-reviews-text p", rec_tags=["a", "em"]),
                "image": None if img_href.startswith("data:image") else url(img_href)
            })
        return reviews

    @staticmethod
    def parse_user_ratings_count(s):
        section = sel(s, ".last-ratings section")
        return -1 if section is None else toint(clean(text(section, ".count")))

    def parse_user_ratings(self, s):
        ratings = {
            "total": self.parse_user_ratings_count(s),
            "last": []
        }
        for tr in asel(s, ".last-ratings tr"):
            tr_a = sel(tr, "a")
            stars = sel(tr, ".stars").get("class")
            ratings["last"].append({
                "id": extract_id(tr_a.get("href")),
                "name": text(tr_a),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(tr, ".date-only")
            })
        return ratings

    @staticmethod
    def parse_user_is_currently_online(s):
        return sel(s, ".user-profile-status") is not None

    @staticmethod
    def parse_user_image(s):
        img_href = sel(s, ".user-profile-content img").get("src")
        return None if img_href.startswith("data:image") else url(img_href)

    def parse_user(self, s, uid):
        return User({
            "id": uid,
            "url": Globals.USERS_URL + str(uid),
            "name": self.parse_user_name(s),
            "real_name": self.parse_user_real_name(s),
            "origin": self.parse_user_origin(s),
            "about": self.parse_user_about(s),
            "registered": self.parse_user_registered(s),
            "last_login": self.parse_user_last_login(s),
            "points": self.parse_user_points(s),
            "awards": self.parse_user_awards(s),
            "most_watched_genres": self.parse_user_most_watched_genres(s),
            "most_watched_types": self.parse_user_most_watched_types(s),
            "most_watched_origins": self.parse_user_most_watched_origins(s),
            "reviews": self.parse_user_reviews(s),
            "ratings": self.parse_user_ratings(s),
            "is_currently_online": self.parse_user_is_currently_online(s),
            "image": self.parse_user_image(s),
        })

class NewsParser:

    # NEWS

    @staticmethod
    def __parse_news_article(s):
        section_a = sel(s, "header a")
        return {
            "id": extract_id(section_a.get("href")),
            "title": text(section_a),
            "text": text(s, ".article-news-textshort p"),
            "date": text(s, ".info .date"),
            "image": url(sel(s, "img").get("src")),
        }

    @staticmethod
    def parse_news_title(s):
        header = sel(s, ".box-news-detail header")
        return None if header is None else text(header, "h1")

    @staticmethod
    def parse_news_text(s):
        contents = asel(s, ".article-news-content-detail > p")
        content = []
        for p in contents:
            txt = clean(text(p, rec_tags=["a", "em"]))
            if txt:
                content.append(txt)
        return " ".join(content)

    @staticmethod
    def parse_news_date(s):
        header = sel(s, ".box-news-detail header")
        return None if header is None else text(header, ".info .date")

    @staticmethod
    def parse_news_author_id(s):
        header = sel(s, ".box-news-detail header")
        author_a = None if header is None else sel(header, ".info a")
        return None if author_a is None else extract_id(author_a.get("href"))

    @staticmethod
    def parse_news_author_name(s):
        header = sel(s, ".box-news-detail header")
        author_a = None if header is None else sel(header, ".info a")
        return None if author_a is None else text(author_a)

    def parse_news_most_read_news(self, s):
        most_read_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 0:
            for article in asel(contents[0], "article"):
                most_read_news.append(self.__parse_news_list_article(article))
        return most_read_news

    def parse_news_most_latest_news(self, s):
        most_latest_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 1:
            for article in asel(contents[1], "article"):
                most_latest_news.append(self.__parse_news_list_article(article))
        return most_latest_news

    def parse_news_related_news(self, s):
        related_news = []
        for article in asel(s, ".newslist article"):
            related_news.append(self.__parse_news_list_article(article))
        return related_news

    @staticmethod
    def parse_news_image(s):
        image = sel(s, ".box-news-detail img")
        return None if image is None else url(image.get("src"))

    @staticmethod
    def parse_news_prev_news_id(s):
        prev_news = sel(s, "a.prev-news")
        return None if prev_news is None else extract_id(prev_news.get("href"))

    @staticmethod
    def parse_news_next_news_id(s):
        next_news = sel(s, "a.next-news")
        return None if next_news is None else extract_id(next_news.get("href"))

    def parse_news(self, s, nid):
        return News({
            "id": nid,
            "title": self.parse_news_title(s),
            "text": self.parse_news_text(s),
            "date": self.parse_news_date(s),
            "author_id": self.parse_news_author_id(s),
            "author_name": self.parse_news_author_name(s),
            "most_read_news": self.parse_news_most_read_news(s),
            "most_latest_news": self.parse_news_most_latest_news(s),
            "related_news": self.parse_news_related_news(s),
            "image": self.parse_news_image(s),
            "prev_news_id": self.parse_news_prev_news_id(s),
            "next_news_id": self.parse_news_next_news_id(s),
        })

    # NEWS LIST

    @staticmethod
    def __parse_news_list_article(s):
        section_a = sel(s, "header a")
        return {
            "id": extract_id(section_a.get("href")),
            "title": text(section_a),
            "text": text(s, ".article-news-textshort p"),
            "date": text(s, ".info .date"),
            "image": url(sel(s, "img").get("src")),
        }

    @staticmethod
    def parse_news_list_main_news(s):
        first = sel(s, ".box-firstnews")
        first_a = sel(first, "header a")
        first_info = sel(first, ".info")
        first_info_a = sel(first_info, "a")
        return {
            "id": extract_id(first_a.get("href")),
            "title": text(first_a),
            "text": text(first, ".article-news-textshort p"),
            "date": text(first_info, ".date"),
            "image": url(sel(first, "img").get("src")),
            "author_id": extract_id(first_info_a.get("href")),
            "author_name": text(first_info_a),
        }

    def parse_news_list_news_list(self, s):
        news_list = []
        for article in asel(s, ".newslist article"):
            news_list.append(self.__parse_news_list_article(article))
        return news_list

    def parse_news_list_most_read_news(self, s):
        most_read_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 0:
            for article in asel(contents[0], "article"):
                most_read_news.append(self.__parse_news_list_article(article))
        return most_read_news

    def parse_news_list_most_latest_news(self, s):
        most_latest_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 1:
            for article in asel(contents[1], "article"):
                most_latest_news.append(self.__parse_news_list_article(article))
        return most_latest_news

    @staticmethod
    def parse_news_list_has_prev_page(s):
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_news_list_has_next_page(s):
        return sel(s, ".page-next") is not None

    def parse_news_list(self, s, page):
        return NewsList({
            "page": page,
            "main_news": self.parse_news_list_main_news(s),
            "news": self.parse_news_list_news_list(s),
            "most_read_news": self.parse_news_list_most_read_news(s),
            "most_latest_news": self.parse_news_list_most_latest_news(s),
            "has_prev_page": self.parse_news_list_has_prev_page(s),
            "has_next_page": self.parse_news_list_has_next_page(s)
        })

class UsersParser:

    @staticmethod
    def __parse_favorite_users_article(s):
        img = sel(s, "img")
        left_content = sel(s, ".article-user-content-left")
        right_content = sel(s, ".article-user-content-right")
        article_a = sel(left_content, "h3 a")
        real_name = sel(left_content, ".info")
        return OtherFavoriteUser({
            "id": extract_id(article_a.get("href")),
            "name": text(article_a),
            "real_name": None if real_name is None else text(real_name),
            "points": toint(text(right_content, "p")),
            "image": None if img is None else url(img.get("src")),
        })

    @staticmethod
    def parse_favorite_users_most_favorite_users(s):
        section = sel(s, ".row .column:nth-child(1) section")
        most_favorite_users = []
        for article in asel(section, "article"):
            img = sel(article, "img")
            left_content = sel(article, ".article-user-content-left")
            right_content = sel(article, ".article-user-content-right")
            article_a = sel(left_content, "h3 a")
            real_name = sel(left_content, ".info")
            about = sel(left_content, "p:last-child")
            most_favorite_users.append(FavoriteUser({
                "position": int(text(left_content, ".user-title-position")[:-1]),
                "id": extract_id(article_a.get("href")),
                "name": text(article_a),
                "real_name": None if real_name is None else text(real_name),
                "about": None if about is None else text(about),
                "points": toint(text(right_content, "p:nth-child(1)")),
                "ratings": toint(text(right_content, "p:nth-child(2) a")),
                "reviews": toint(text(right_content, "p:nth-child(3) a")),
                "image": None if img is None else url(img.get("src")),
            }))
        return most_favorite_users

    def parse_favorite_users_by_regions(self, s):
        section = sel(s, ".row .column:nth-child(2) section")
        by_regions = {}
        current_region = None
        for tag in asel(section, ".box-content > div, .box-content > article"):
            if tag.name == "div":
                current_region = clean(text(tag))
                by_regions[current_region] = []
                continue

            user = self.__parse_favorite_users_article(tag)
            by_regions[current_region].append(user)
        return by_regions

    def parse_favorite_users_by_country(self, s):
        section = sel(s, ".row .column:nth-child(3) section")
        by_country = {}
        current_country = None
        for tag in asel(section, ".box-content > div, .box-content > article"):
            if tag.name == "div":
                current_country = Origins.get_by_czech_name(clean(text(tag)))
                by_country[current_country] = []
                continue

            user = self.__parse_favorite_users_article(tag)
            by_country[current_country].append(user)
        return by_country

    def parse_favorite_users(self, s) -> FavoriteUsers:
        return FavoriteUsers({
            "most_favorite_users": self.parse_favorite_users_most_favorite_users(s),
            "by_regions": self.parse_favorite_users_by_regions(s),
            "by_country": self.parse_favorite_users_by_country(s)
        })

    # def parse_active_users(self, s):
    #     return ActiveUsers({
    #
    #     })
