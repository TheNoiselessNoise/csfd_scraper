from typing import Type
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from src.csfd_objects import *
from src.csfd_utils import *


class CreatorParser:
    __CREATOR_LD_JSON: Optional[dict] = None

    def reset(self) -> None:
        self.__CREATOR_LD_JSON = None

    def parse_movie_ld_json(self, s: BeautifulSoup) -> Optional[dict]:
        if not self.__CREATOR_LD_JSON:
            ld_json = sel(s, ".creator-main > script")
            self.__CREATOR_LD_JSON = {} if ld_json is None else json.loads(text(ld_json))
        return self.__CREATOR_LD_JSON

    def parse_creator_type(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("@type", None)

    def parse_creator_name(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("name", None)

    @staticmethod
    def parse_creator_age(s: BeautifulSoup) -> int:
        content = sel(s, ".creator-profile-content-desc > p")
        age = None if content is None else clean(text(content))
        return -1 if not age else int(age.split(" ")[2][1:])

    def parse_creator_birth_date(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("birthDate", None)

    def parse_creator_birth_place(self, s: BeautifulSoup) -> Optional[str]:
        place = self.parse_movie_ld_json(s).get("birthPlace", None)
        return None if place is None else place.get("name", None)

    @staticmethod
    def parse_creator_bio(s: BeautifulSoup) -> Optional[str]:
        bio = sel(s, ".article-content p")
        return None if bio is None else clean(text(bio))

    @staticmethod
    def parse_creator_trivia_count(s: BeautifulSoup) -> int:
        article = sel(s, ".article-trivia")
        section = None if article is None else article.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else toint(text(count))

    def parse_creator_trivia(self, s: BeautifulSoup) -> dict:
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
                "movie_id": extract_id(a.get("href")) if a else None,
                "movie": text(a) if a else None,
                "author_id": user_id,
                "author": text(user_a),
                "text": clean(text(article, "li", rec_tags=["a", "em"]))
            })
        return trivia

    @staticmethod
    def parse_creator_ranks(s: BeautifulSoup) -> dict:
        ranks = {}
        for div in asel(s, ".ranking"):
            div_a = sel(div, "a")
            ranks[text(div_a)] = Globals.CSFD_URL + div_a.get("href")
        return ranks

    @staticmethod
    def parse_creator_gallery_count(s: BeautifulSoup) -> int:
        gallery_item = sel(s, ".gallery-item")
        section = None if gallery_item is None else gallery_item.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else toint(text(count))

    def parse_creator_gallery(self, s: BeautifulSoup) -> dict:
        img = sel(s, ".gallery-item picture img")
        return {
            "total": self.parse_creator_gallery_count(s),
            "image": url(img.get("src")) if img else None
        }

    @staticmethod
    def parse_creator_filmography(s: BeautifulSoup) -> dict:
        div = sel(s, ".creator-filmography")

        filmography = {}
        if div is not None:
            for section in asel(div, "section"):
                section_name = text(section, "header h2")
                year = None

                filmography[section_name] = {}
                for table in asel(section, "table"):
                    table_name = text(table, "th")

                    filmography[section_name][table_name] = {}
                    for tr in asel(table, "tr"):
                        td_year = sel(tr, "td.year")
                        td_name = sel(tr, "td.name")
                        td_name_a = sel(td_name, "a") if td_name else None
                        td_episode = sel(tr, "td.episode")
                        td_episode_a = sel(td_episode, "a") if td_episode else None
                        td_more_episode = sel(tr, ".more-episode")

                        if td_more_episode:
                            continue

                        if not td_year and not td_name and not td_episode: # probably ad
                            continue

                        td_year_content = clean(text(td_year))
                        if td_year_content.isnumeric():
                            year = int(td_year_content)

                        if year not in filmography[section_name][table_name]:
                            filmography[section_name][table_name][year] = []

                        if td_episode:
                            if "episodes" not in filmography[section_name][table_name][year][-1]:
                                filmography[section_name][table_name][year][-1]["episodes"] = []

                            filmography[section_name][table_name][year][-1]["episodes"].append({
                                "id": extract_id(td_episode_a.get("href")),
                                "name": text(td_episode_a),
                                "number": text(td_episode, ".film-title-info .info")[1:-1]
                            })
                        else:
                            filmography[section_name][table_name][year].append({
                                "id": extract_id(td_name_a.get("href")),
                                "name": text(td_name_a)
                            })

        return filmography

    def parse_creator_image(self, s: BeautifulSoup) -> Optional[str]:
        img = sel(s, ".creator-profile-content img")
        return url(img.get("src")) if img else None

    def parse_creator(self, s: BeautifulSoup, cid: int) -> Creator:
        return Creator({
            "id": cid,
            "url": Globals.CREATORS_URL + str(cid),
            "type": self.parse_creator_type(s),
            "name": self.parse_creator_name(s),
            "age": self.parse_creator_age(s),
            "birth_date": self.parse_creator_birth_date(s),
            "birth_place": self.parse_creator_birth_place(s),
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
    def parse_movies_search_movies(s: BeautifulSoup) -> List[SearchedMovie]:
        movies = []
        for tr in asel(s, "table tbody tr"):
            movie_a = sel(tr, "a")
            movies.append(SearchedMovie({
                "id": extract_id(movie_a.get("href")),
                "title": text(movie_a),
                "year": int(text(tr, "span.info")[1:-1]),
                "origins": text(tr, "td.origin").split(" / "),
                "genres": text(tr, "td.genre").split(" / "),
            }))
        return movies

    @staticmethod
    def parse_movies_search_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_movies_search_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-next") is not None

    def parse_movies_search(self, s: BeautifulSoup, page: int) -> SearchMoviesResult:
        return SearchMoviesResult({
            "page": page,
            "movies": self.parse_movies_search_movies(s),
            "has_prev_page": self.parse_movies_search_has_prev_page(s),
            "has_next_page": self.parse_movies_search_has_next_page(s),
        })

    # CREATORS

    @staticmethod
    def parse_creators_search_creators(s: BeautifulSoup) -> List[SearchedCreator]:
        creators = []
        for tr in asel(s, "table tbody tr"):
            creator_a = sel(tr, "a")
            birth_year = text(tr, ".author-birthday").split(" ")
            creators.append(SearchedCreator({
                "id": extract_id(creator_a.get("href")),
                "name": text(creator_a),
                "birth_year": -1 if len(birth_year) == 1 else int(birth_year[1]),
                "types": text(tr, ".author-dos").split(" / "),
            }))
        return creators

    @staticmethod
    def parse_creators_search_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_creators_search_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-next") is not None

    def parse_creators_search(self, s: BeautifulSoup, page: int) -> SearchCreatorsResult:
        return SearchCreatorsResult({
            "page": page,
            "creators": self.parse_creators_search_creators(s),
            "has_prev_page": self.parse_creators_search_has_prev_page(s),
            "has_next_page": self.parse_creators_search_has_next_page(s),
        })

    # TEXT SEARCH

    @staticmethod
    def __parse_text_search_parse_creators(s: BeautifulSoup, name: str) -> List[dict]:
        creators = []
        for p in asel(s, ".film-creators"):
            if text(p).split(":")[0] == name:
                for a in asel(p, "a"):
                    creators.append({
                        "id": extract_id(a.get("href")),
                        "name": text(a),
                    })
        return creators

    def parse_text_search_movies(self, s: BeautifulSoup) -> List[TextSearchedMovie]:
        movies = []
        for article in asel(s, ".main-movies article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            origins_genres = text(article, ".film-origins-genres .info").split(", ")
            movies.append(TextSearchedMovie({
                "id": extract_id(articla_a.get("href")),
                "title": text(articla_a),
                "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
                "origins": origins_genres[0].split(" / ") if len(origins_genres) > 1 else [],
                "directors": self.__parse_text_search_parse_creators(article, "Režie"),
                "actors": self.__parse_text_search_parse_creators(article, "Hrají"),
                "performers": self.__parse_text_search_parse_creators(article, "Účinkují"),
                "image": url(img_url)
            }))
        return movies

    @staticmethod
    def parse_text_search_creators(s: BeautifulSoup) -> List[TextSearchedCreator]:
        creators = []
        for article in asel(s, ".main-authors article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            creators.append(TextSearchedCreator({
                "id": extract_id(articla_a.get("href")),
                "name": text(articla_a),
                "types": text(article, ".article-content .info").split(" / "),
                "image": url(img_url)
            }))
        return creators

    def parse_text_search_series(self, s: BeautifulSoup) -> List[TextSearchedSeries]:
        series = []
        for article in asel(s, ".main-series article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            origins_genres = text(article, ".film-origins-genres .info").split(", ")
            series.append(TextSearchedSeries({
                "id": extract_id(articla_a.get("href")),
                "title": text(articla_a),
                "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
                "origins": origins_genres[:-1],
                "directors": self.__parse_text_search_parse_creators(article, "Režie"),
                "actors": self.__parse_text_search_parse_creators(article, "Hrají"),
                "performers": self.__parse_text_search_parse_creators(article, "Účinkují"),
                "image": url(img_url)
            }))
        return series

    @staticmethod
    def parse_text_search_users(s: BeautifulSoup) -> List[TextSearchedUser]:
        users = []
        for article in asel(s, ".main-users article.article"):
            img_url = sel(article, "img").get("src")
            articla_a = sel(article, ".article-content a")
            points_p = sel(article, ".article-content p:last-child")
            points = text(points_p)
            users.append(TextSearchedUser({
                "id": extract_id(articla_a.get("href")),
                "name": text(articla_a),
                "real_name": text(article, ".article-content p:first-of-type"),
                "points": int(points.split(" ")[0]) if points else 0,
                "image": url(img_url)
            }))
        return users

    def parse_text_search(self, s: BeautifulSoup) -> TextSearchResult:
        return TextSearchResult({
            "movies": self.parse_text_search_movies(s),
            "creators": self.parse_text_search_creators(s),
            "series": self.parse_text_search_series(s),
            "users": self.parse_text_search_users(s)
        })

class MovieParser:
    __MOVIE_LD_JSON: Optional[dict] = None
    __VOD_BLOCKED_HOSTS: List[str] = [
        "www.facebook.com",
        "twitter.com"
    ]

    def reset(self) -> None:
        self.__MOVIE_LD_JSON = None

    def parse_movie_ld_json(self, s: BeautifulSoup) -> dict:
        if not self.__MOVIE_LD_JSON:
            ld_json = sel(s, ".main-movie > script")
            self.__MOVIE_LD_JSON = {} if ld_json is None else json.loads(text(ld_json))
        return self.__MOVIE_LD_JSON

    def parse_movie_type(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("@type", None)

    def parse_movie_title(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("name", None)

    def parse_movie_year(self, s: BeautifulSoup) -> int:
        return toint(self.parse_movie_ld_json(s).get("dateCreated", -1))

    def parse_movie_duration(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("duration", None)

    @staticmethod
    def parse_movie_genres(s: BeautifulSoup) -> List[str]:
        genres = sel(s, ".genres")
        return [] if genres is None else genres.get_text().split(" / ")

    @staticmethod
    def parse_movie_origins(s: BeautifulSoup) -> List[str]:
        origin = sel(s, ".origin")
        return [] if origin is None else text(origin).split(", ")[0].split(" / ")

    def parse_movie_rating(self, s: BeautifulSoup) -> dict:
        ld_json = self.parse_movie_ld_json(s)
        rating = ld_json.get("aggregateRating", None)
        return {
            "value": rating["ratingValue"] if rating else -1,
            "count": rating["ratingCount"] if rating else -1
        }

    @staticmethod
    def parse_movie_ranks(s: BeautifulSoup) -> dict:
        ranks = {}
        for div in asel(s, ".film-ranking"):
            div_a = sel(div, "a")
            ranks[text(div_a)] = Globals.CSFD_URL + div_a.get("href")
        return ranks

    @staticmethod
    def parse_movie_other_names(s: BeautifulSoup) -> dict:
        other_names = {}
        for li in asel(s, ".film-names li"):
            other_names[sel(li, "img").get("title")] = text(li)
        return other_names

    @staticmethod
    def parse_movie_creators(s: BeautifulSoup) -> dict:
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

    def parse_movie_vods(self, s: BeautifulSoup) -> dict:
        vods = {}
        for a in asel(s, ".box-buttons > a"):
            parsed_url = urlsplit(a.get("href"))
            if parsed_url.hostname not in self.__VOD_BLOCKED_HOSTS:
                vods[text(a)] = a.get("href")
        return vods

    @staticmethod
    def parse_movie_tags(s: BeautifulSoup) -> dict:
        tags = {}
        for a in asel(s, "aside > section:last-child > .box-content > a"):
            tags[text(a)] = toint(a.get("href").split("=")[1])
        return tags

    @staticmethod
    def parse_movie_reviews_count(s: BeautifulSoup) -> int:
        count = sel(s, ".box-reviews .count")
        return -1 if count is None else toint(text(count))

    def parse_movie_reviews(self, s: BeautifulSoup) -> dict:
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
                "text": clean(text(article, ".article-content .comment", rec_tags=["a", "em", "span"])),
            })
        return reviews

    @staticmethod
    def parse_movie_gallery_count(s: BeautifulSoup) -> int:
        gallery_item = sel(s, ".gallery-item")
        section = None if gallery_item is None else gallery_item.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else toint(text(count))

    def parse_movie_gallery(self, s: BeautifulSoup) -> dict:
        img = sel(s, ".gallery-item picture img")
        return {
            "total": self.parse_movie_gallery_count(s),
            "image": url(img.get("src")) if img else None
        }

    @staticmethod
    def parse_movie_trivia_count(s: BeautifulSoup) -> int:
        article = sel(s, ".article-trivia")
        section = None if article is None else article.find_parent("section")
        count = None if section is None else sel(section, ".count")
        return -1 if count is None else toint(text(count))

    def parse_movie_trivia(self, s: BeautifulSoup) -> dict:
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
    def parse_movie_premieres(s: BeautifulSoup) -> List[dict]:
        premieres = []
        for li in asel(s, ".box-premieres li"):
            where = text(li, "p")
            when_tag = asel(li, "span")[1]
            when = clean(text(when_tag))

            xwhen = when
            if " " in when:
                xwhen = when[:when.index(" ")]

            xby = None
            if " " in when:
                xby = when[when.index(" ") + 1:]

            premieres.append({
                "country": sel(li, ".item-img img").get("title"),
                "where": where[:where.rindex(" ")],
                "when": xwhen,
                "by": xby,
            })
        return premieres

    @staticmethod
    def parse_movie_plot(s: BeautifulSoup) -> dict:
        main_plot_tag = sel(s, ".plot-full > p")
        main_plot_source_tag = sel(main_plot_tag, ".span-more-small a")
        other_plots_tags = asel(s, ".plots > .plots-item > p")
        other_plots = []
        for other_plot_tag in other_plots_tags:
            main_plot_author_tag = sel(other_plot_tag, ".span-more-small a")
            other_plots.append({
                "author_id": extract_id(main_plot_author_tag.get('href')),
                "author": text(main_plot_author_tag),
                "text": text(other_plot_tag, rec_tags=["a", "em"], is_not=["em.span-more-small"])
            })
        return {
            "main_plot": {
                "source_name": text(main_plot_source_tag),
                "source_url": main_plot_source_tag.get("href"),
                "text": text(main_plot_tag, rec_tags=["a", "em"], is_not=["em.span-more-small"])
            },
            "other_plots": other_plots
        }

    def parse_movie_cover(self, s: BeautifulSoup) -> Optional[str]:
        return self.parse_movie_ld_json(s).get("image", None)

    def parse_movie(self, s: BeautifulSoup, mid: int) -> Movie:
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

    # USER OVERVIEW

    @staticmethod
    def parse_user_name(s: BeautifulSoup) -> Optional[str]:
        return text(s, ".user-profile h1")

    @staticmethod
    def parse_user_real_name(s: BeautifulSoup) -> Optional[str]:
        return text(s, ".user-profile-content > p > strong")

    @staticmethod
    def parse_user_origin(s: BeautifulSoup) -> Optional[str]:
        p = sel(s, ".user-profile-content > p")
        return clean(p.contents[3]).split(", ")

    @staticmethod
    def parse_user_about(s: BeautifulSoup) -> Optional[str]:
        p = sel(s, ".user-profile-content > p")
        return clean(p.contents[5])

    @staticmethod
    def parse_user_registered(s: BeautifulSoup) -> Optional[str]:
        user_footer = sel(s, ".user-profile-footer-left")
        return clean(text(user_footer)).split(" ")[3]

    @staticmethod
    def parse_user_last_login(s: BeautifulSoup) -> Optional[str]:
        user_footer = sel(s, ".user-profile-footer-left")
        parts = clean(text(user_footer)).split(" ")
        return f"{parts[6]} {parts[7]}" if len(parts) >= 8 else None

    @staticmethod
    def parse_user_points(s: BeautifulSoup) -> int:
        points = sel(s, ".ranking-points")
        return -1 if points is None else toint(clean(text(points, rec_tags=["a"])))

    @staticmethod
    def parse_user_fans(s: BeautifulSoup) -> int:
        content_span = sel(s, ".fan-club-content > span")
        return -1 if content_span is None else toint(text(content_span))

    @staticmethod
    def parse_user_awards(s: BeautifulSoup) -> dict:
        awards = {}
        for a in asel(s, ".ranking:not(.ranking-points) a"):
            awards[text(a)] = a.get("href")
        return awards

    @staticmethod
    def parse_user_most_watched_genres(s: BeautifulSoup) -> dict:
        most_watched_genres = {}
        for li in asel(s, ".genres-switch li"):
            meter = int(sel(li, ".meter").get("style").split(" ")[1][:-1])
            most_watched_genres[text(li)] = meter
        return most_watched_genres

    @staticmethod
    def parse_user_most_watched_types(s: BeautifulSoup) -> dict:
        most_watched_types = {}
        for li in asel(s, ".types-switch li"):
            span_text = sel(li, "span").get("title")
            meter = int(sel(li, ".meter").get("style").split(" ")[1][:-1])
            most_watched_types[span_text] = meter
        return most_watched_types

    @staticmethod
    def parse_user_most_watched_origins(s: BeautifulSoup) -> dict:
        most_watched_origins = {}
        for li in asel(s, ".origins-switch li"):
            span_text = sel(li, "span").get("title")
            meter = int(sel(li, ".meter").get("style").split(" ")[1][:-1])
            most_watched_origins[span_text] = meter
        return most_watched_origins

    @staticmethod
    def parse_user_reviews_count(s: BeautifulSoup) -> int:
        section = sel(s, ".user-reviews")
        return -1 if section is None else toint(clean(text(section, ".count")))

    def parse_user_reviews(self, s: BeautifulSoup) -> dict:
        reviews = {
            "total": self.parse_user_reviews_count(s),
            "last": []
        }
        for article in asel(s, ".user-reviews article.article"):
            img = sel(article, "img")
            article_a = sel(article, "header a")
            stars = sel(article, ".stars").get("class")
            reviews["last"].append({
                "id": extract_id(article_a.get("href")),
                "name": text(article_a),
                "year": toint(text(article, ".film-title-info .info:first-child")),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(article, "time"),
                "text": text(article, ".user-reviews-text p", rec_tags=["a", "em", "span"]),
                "image": url(img.get("src")) if img else None
            })
        return reviews

    @staticmethod
    def parse_user_ratings_count(s: BeautifulSoup) -> int:
        section = sel(s, ".last-ratings section")
        return -1 if section is None else toint(clean(text(section, ".count")))

    def parse_user_ratings(self, s: BeautifulSoup) -> dict:
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
    def parse_user_is_currently_online(s: BeautifulSoup) -> bool:
        return sel(s, ".user-profile-status") is not None

    @staticmethod
    def parse_user_image(s: BeautifulSoup) -> Optional[str]:
        img = sel(s, ".user-profile-content img")
        return url(img.get("src")) if img else None

    def parse_user(self, s: BeautifulSoup, uid: int):
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
            "fans": self.parse_user_fans(s),
            "awards": self.parse_user_awards(s),
            "most_watched_genres": self.parse_user_most_watched_genres(s),
            "most_watched_types": self.parse_user_most_watched_types(s),
            "most_watched_origins": self.parse_user_most_watched_origins(s),
            "reviews": self.parse_user_reviews(s),
            "ratings": self.parse_user_ratings(s),
            "is_currently_online": self.parse_user_is_currently_online(s),
            "image": self.parse_user_image(s),
        })

    # USER RATINGS

    @staticmethod
    def parse_user_ratings_ratings_count(s: BeautifulSoup) -> int:
        return toint(text(s, ".count"))

    @staticmethod
    def parse_user_ratings_ratings_list(s: BeautifulSoup) -> List[UserRating]:
        ratings = []
        for tr in asel(s, ".user-tab-rating table tr"):
            td_a = sel(tr, ".name a")
            stars = sel(tr, ".star-rating-only .stars").get("class")

            ratings.append(UserRating({
                "id": extract_id(td_a.get("href")),
                "name": text(td_a),
                "year": toint(text(tr, ".film-title-info .info:first-child")),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(tr, ".date-only")
            }))
        return ratings

    @staticmethod
    def parse_user_ratings_ratings_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".user-tab-rating .page-prev") is not None

    @staticmethod
    def parse_user_ratings_ratings_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".user-tab-rating .page-next") is not None

    def parse_user_ratings_ratings(self, s: BeautifulSoup) -> UserRatings:
        return UserRatings({
            "total": self.parse_user_ratings_ratings_count(s),
            "ratings": self.parse_user_ratings_ratings_list(s),
            "has_prev_page": self.parse_user_ratings_ratings_has_prev_page(s),
            "has_next_page": self.parse_user_ratings_ratings_has_next_page(s),
        })

    # USER REVIEWS

    @staticmethod
    def parse_user_reviews_reviews_count(s: BeautifulSoup) -> int:
        return toint(text(s, ".count"))

    @staticmethod
    def parse_user_reviews_reviews_list(s: BeautifulSoup) -> List[UserReview]:
        reviews = []
        for article in asel(s, ".user-reviews article.article"):
            img = sel(article, "img")
            article_a = sel(article, "header a")
            stars = sel(article, ".stars").get("class")
            reviews.append(UserReview({
                "id": extract_id(article_a.get("href")),
                "name": text(article_a),
                "year": toint(text(article, ".film-title-info .info:first-child")),
                "rating": 0 if stars[1] == "trash" else int(stars[1][-1]),
                "date": text(article, "time"),
                "text": text(article, ".user-reviews-text p", rec_tags=["a", "em", "span"]),
                "image": url(img.get("src")) if img else None
            }))
        return reviews

    @staticmethod
    def parse_user_reviews_reviews_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".user-reviews .page-prev") is not None

    @staticmethod
    def parse_user_reviews_reviews_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".user-reviews .page-next") is not None

    def parse_user_reviews_reviews(self, s: BeautifulSoup) -> UserReviews:
        return UserReviews({
            "total": self.parse_user_reviews_reviews_count(s),
            "reviews": self.parse_user_reviews_reviews_list(s),
            "has_prev_page": self.parse_user_reviews_reviews_has_prev_page(s),
            "has_next_page": self.parse_user_reviews_reviews_has_next_page(s),
        })

class NewsParser:

    # NEWS

    @staticmethod
    def __parse_news_article(s: BeautifulSoup) -> dict:
        section_a = sel(s, "header a")
        return {
            "id": extract_id(section_a.get("href")),
            "title": text(section_a),
            "text": text(s, ".article-news-textshort p"),
            "date": text(s, ".info .date"),
            "image": url(sel(s, "img").get("src")),
        }

    @staticmethod
    def parse_news_title(s: BeautifulSoup) -> Optional[str]:
        header = sel(s, ".box-news-detail header")
        return None if header is None else text(header, "h1")

    @staticmethod
    def parse_news_text(s: BeautifulSoup) -> Optional[str]:
        contents = asel(s, ".article-news-content-detail > p")
        content = []
        for p in contents:
            txt = clean(text(p, rec_tags=["a", "em"]))
            if txt:
                content.append(txt)
        return " ".join(content)

    @staticmethod
    def parse_news_date(s: BeautifulSoup) -> Optional[str]:
        header = sel(s, ".box-news-detail header")
        return None if header is None else text(header, ".info .date")

    @staticmethod
    def parse_news_author_id(s: BeautifulSoup) -> int:
        header = sel(s, ".box-news-detail header")
        author_a = None if header is None else sel(header, ".info a")
        return -1 if author_a is None else extract_id(author_a.get("href"))

    @staticmethod
    def parse_news_author_name(s: BeautifulSoup) -> Optional[str]:
        header = sel(s, ".box-news-detail header")
        author_a = None if header is None else sel(header, ".info a")
        return None if author_a is None else text(author_a)

    def parse_news_most_read_news(self, s: BeautifulSoup) -> List[dict]:
        most_read_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 0:
            for article in asel(contents[0], "article"):
                most_read_news.append(self.__parse_news_list_article(article))
        return most_read_news

    def parse_news_most_latest_news(self, s: BeautifulSoup) -> List[dict]:
        most_latest_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 1:
            for article in asel(contents[1], "article"):
                most_latest_news.append(self.__parse_news_list_article(article))
        return most_latest_news

    def parse_news_related_news(self, s: BeautifulSoup) -> List[dict]:
        related_news = []
        for article in asel(s, ".newslist article"):
            related_news.append(self.__parse_news_list_article(article))
        return related_news

    @staticmethod
    def parse_news_image(s: BeautifulSoup) -> Optional[str]:
        img = sel(s, ".box-news-detail img")
        return url(img.get("src")) if img else None

    @staticmethod
    def parse_news_prev_news_id(s: BeautifulSoup) -> int:
        prev_news = sel(s, "a.prev-news")
        return -1 if prev_news is None else extract_id(prev_news.get("href"))

    @staticmethod
    def parse_news_next_news_id(s: BeautifulSoup) -> int:
        next_news = sel(s, "a.next-news")
        return -1 if next_news is None else extract_id(next_news.get("href"))

    def parse_news(self, s: BeautifulSoup, nid: int):
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
    def __parse_news_list_article(s: BeautifulSoup) -> dict:
        section_a = sel(s, "header a")
        return {
            "id": extract_id(section_a.get("href")),
            "title": text(section_a),
            "text": text(s, ".article-news-textshort p"),
            "date": text(s, ".info .date"),
            "image": url(sel(s, "img").get("src")),
        }

    @staticmethod
    def parse_news_list_main_news(s: BeautifulSoup) -> dict:
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

    def parse_news_list_news_list(self, s: BeautifulSoup) -> List[dict]:
        news_list = []
        for article in asel(s, ".newslist article"):
            news_list.append(self.__parse_news_list_article(article))
        return news_list

    def parse_news_list_most_read_news(self, s: BeautifulSoup) -> List[dict]:
        most_read_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 0:
            for article in asel(contents[0], "article"):
                most_read_news.append(self.__parse_news_list_article(article))
        return most_read_news

    def parse_news_list_most_latest_news(self, s: BeautifulSoup) -> List[dict]:
        most_latest_news = []
        contents = asel(s, ".box-content-news-right")
        if len(contents) > 1:
            for article in asel(contents[1], "article"):
                most_latest_news.append(self.__parse_news_list_article(article))
        return most_latest_news

    @staticmethod
    def parse_news_list_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_news_list_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-next") is not None

    def parse_news_list(self, s: BeautifulSoup, page: int) -> NewsList:
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

    # MOST FAVORITE USERS

    @staticmethod
    def __parse_favorite_users_article(s: BeautifulSoup) -> OtherFavoriteUser:
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
            "image": url(img.get("src")) if img else None,
        })

    @staticmethod
    def parse_favorite_users_most_favorite_users(s: BeautifulSoup) -> List[FavoriteUser]:
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
                "image": url(img.get("src")) if img else None,
            }))
        return most_favorite_users

    def parse_favorite_users_by_regions(self, s: BeautifulSoup) -> Dict[Origins, List[OtherFavoriteUser]]:
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

    def parse_favorite_users_by_country(self, s: BeautifulSoup) -> Dict[Origins, List[OtherFavoriteUser]]:
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

    def parse_favorite_users(self, s: BeautifulSoup) -> FavoriteUsers:
        return FavoriteUsers({
            "most_favorite_users": self.parse_favorite_users_most_favorite_users(s),
            "by_regions": self.parse_favorite_users_by_regions(s),
            "by_country": self.parse_favorite_users_by_country(s)
        })

    # MOST ACTIVE USERS

    @staticmethod
    def __parse_active_users_article(s: BeautifulSoup, cls: Type, prop: str):
        img = sel(s, "img")
        article_a = sel(s, ".user-title a")
        return cls({
            "id": extract_id(article_a.get("href")),
            "name": text(article_a),
            prop: toint(text(s, ".article-content > p")),
            "image": url(img.get("src")) if img else None,
        })

    def parse_active_users_by_reviews(self, s: BeautifulSoup) -> List[ActiveUserByReviews]:
        section = sel(s, ".row .column:nth-child(1) section")
        by_reviews = []
        for article in asel(section, "article"):
            user = self.__parse_active_users_article(article, ActiveUserByReviews, "reviews")
            by_reviews.append(user)
        return by_reviews

    def parse_active_users_by_diaries(self, s: BeautifulSoup) -> List[ActiveUserByDiaries]:
        section = sel(s, ".row .column:nth-child(2) section")
        by_diaries = []
        for article in asel(section, "article"):
            user = self.__parse_active_users_article(article, ActiveUserByDiaries, "diaries")
            by_diaries.append(user)
        return by_diaries

    def parse_active_users_by_content(self, s: BeautifulSoup) -> List[ActiveUserByContent]:
        section = sel(s, ".row .column:nth-child(3) section")
        by_content = []
        for article in asel(section, "article"):
            user = self.__parse_active_users_article(article, ActiveUserByContent, "content")
            by_content.append(user)
        return by_content

    def parse_active_users_by_trivia(self, s: BeautifulSoup) -> List[ActiveUserByTrivia]:
        section = sel(s, ".row .column:nth-child(4) section")
        by_trivia = []
        for article in asel(section, "article"):
            user = self.__parse_active_users_article(article, ActiveUserByTrivia, "trivia")
            by_trivia.append(user)
        return by_trivia

    def parse_active_users_by_biography(self, s: BeautifulSoup) -> List[ActiveUserByBiography]:
        section = sel(s, ".row .column:nth-child(5) section")
        by_biography = []
        for article in asel(section, "article"):
            user = self.__parse_active_users_article(article, ActiveUserByBiography, "biography")
            by_biography.append(user)
        return by_biography

    def parse_active_users(self, s: BeautifulSoup) -> ActiveUsers:
        return ActiveUsers({
            "by_reviews": self.parse_active_users_by_reviews(s),
            "by_diaries": self.parse_active_users_by_diaries(s),
            "by_content": self.parse_active_users_by_content(s),
            "by_trivia": self.parse_active_users_by_trivia(s),
            "by_biography": self.parse_active_users_by_biography(s),
        })

class DvdsParser:

    # DVDS MONTHLY

    @staticmethod
    def __parse_dvds_monthly_parse_creators(s: BeautifulSoup, name: str) -> List[dict]:
        creators = []
        for p in asel(s, ".film-creators"):
            if text(p).split(":")[0] == name:
                for a in asel(p, "a"):
                    creators.append({
                        "id": extract_id(a.get("href")),
                        "name": text(a),
                    })
        return creators

    def __parse_dvds_monthly_article(self, s: BeautifulSoup) -> DVDMonthly:
        img = sel(s, "img")
        header = sel(s, ".article-header")
        header_a = sel(header, "a")
        origins_genres = text(s, ".film-origins-genres .info").split(", ")

        return DVDMonthly({
            "id": extract_id(header_a.get("href")),
            "name": text(header_a),
            "year": int(text(header, ".info")[1:-1]),
            "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
            "origins": origins_genres[0].split(" / ") if len(origins_genres) > 1 else [],
            "directors": self.__parse_dvds_monthly_parse_creators(s, "Režie"),
            "actors": self.__parse_dvds_monthly_parse_creators(s, "Hrají"),
            "distributor": clean(text(s, ".article-content > p:last-of-type")).split(": ")[-1],
            "image": url(img.get("src")) if img else None,
        })

    @staticmethod
    def parse_dvds_monthly_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_dvds_monthly_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-next") is not None

    def parse_dvds_monthly_by_release_date(self, s: BeautifulSoup) -> DVDSMonthlyByReleaseDate:
        content = sel(s, ".box-content.box-content-striped-articles")
        dvds = {}
        current_date = None

        for tag in content.children:
            if tag.name not in ["div", "article"]:
                continue

            if tag.name == "div":
                if tag.get("class") != ["box-sub-header"]:
                    continue
                current_date = text(tag).split(" ")[-1]
                dvds[current_date] = []
                continue

            dvd = self.__parse_dvds_monthly_article(tag)
            dvds[current_date].append(dvd)

        return DVDSMonthlyByReleaseDate({
            "dvds": dvds,
            "has_prev_page": self.parse_dvds_monthly_has_prev_page(s),
            "has_next_page": self.parse_dvds_monthly_has_next_page(s),
        })

    def parse_dvds_monthly_by_rating(self, s: BeautifulSoup) -> DVDSMonthlyByRating:
        content = sel(s, ".box-content.box-content-striped-articles")
        dvds = []
        for article in asel(content, "article"):
            dvds.append(self.__parse_dvds_monthly_article(article))
        return DVDSMonthlyByRating({
            "dvds": dvds,
            "has_prev_page": self.parse_dvds_monthly_has_prev_page(s),
            "has_next_page": self.parse_dvds_monthly_has_next_page(s),
        })
    
    # DVDS YEARLY

    @staticmethod
    def __parse_dvds_yearly_tr(s: BeautifulSoup, date: str) -> DVDYearly:
        tr_a = sel(s, ".movies a")
        return DVDYearly({
            "id": extract_id(tr_a.get("href")),
            "name": text(tr_a),
            "year": toint(text(s, ".movies .info")),
            "date": date,
        })

    def parse_dvds_yearly_by_release_date(self, s: BeautifulSoup) -> DVDSYearlyByReleaseDate:
        dvds = {}
        for content in asel(s, ".box-content:not(.box-content-striped-articles)"):
            month_name = text(content, ".box-sub-header").split(" ")[0]
            month = Months.get_by_czech_name(month_name)
            dvds[month] = []
            current_date = None

            for tr in asel(content, "table tbody tr"):
                date_td = sel(tr, "td.date-only")

                if date_td is not None:
                    current_date = text(date_td)

                dvd = self.__parse_dvds_yearly_tr(tr, current_date)
                dvds[month].append(dvd)

        return DVDSYearlyByReleaseDate({"dvds": dvds})

    def parse_dvds_yearly_by_rating(self, s: BeautifulSoup) -> DVDSYearlyByRating:
        dvds = []
        current_date = None
        for tr in asel(s, "table tbody tr"):
            date_td = sel(tr, "td.date-only")

            if date_td is not None:
                current_date = text(date_td)

            dvds.append(self.__parse_dvds_yearly_tr(tr, current_date))

        return DVDSYearlyByRating({"dvds": dvds})

class BluraysParser:

    # BLURAYS MONTHLY

    @staticmethod
    def __parse_blurays_monthly_parse_creators(s: BeautifulSoup, name: str) -> List[dict]:
        creators = []
        for p in asel(s, ".film-creators"):
            if text(p).split(":")[0] == name:
                for a in asel(p, "a"):
                    creators.append({
                        "id": extract_id(a.get("href")),
                        "name": text(a),
                    })
        return creators

    def __parse_blurays_monthly_article(self, s: BeautifulSoup) -> BlurayMonthly:
        img = sel(s, "img")
        header = sel(s, ".article-header")
        header_a = sel(header, "a")
        origins_genres = text(s, ".film-origins-genres .info").split(", ")
        distributor = clean(text(s, ".article-content > p:last-of-type", rec_tags=["span"])).split(": ")

        return BlurayMonthly({
            "id": extract_id(header_a.get("href")),
            "name": text(header_a),
            "year": int(text(header, ".info")[1:-1]),
            "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
            "origins": origins_genres[0].split(" / ") if len(origins_genres) > 1 else [],
            "directors": self.__parse_blurays_monthly_parse_creators(s, "Režie"),
            "actors": self.__parse_blurays_monthly_parse_creators(s, "Hrají"),
            "distributor": {
                "name": distributor[1],
                "types": distributor[2].split(" / "),
            },
            "image": url(img.get("src")) if img else None,
        })

    @staticmethod
    def parse_blurays_monthly_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_blurays_monthly_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-next") is not None

    def parse_blurays_monthly_by_release_date(self, s: BeautifulSoup) -> BluraysMonthlyByReleaseDate:
        content = sel(s, ".box-content.box-content-striped-articles")
        blurays = {}
        current_date = None

        for tag in content.children:
            if tag.name not in ["div", "article"]:
                continue

            if tag.name == "div":
                if tag.get("class") != ["box-sub-header"]:
                    continue
                current_date = text(tag).split(" ")[-1]
                blurays[current_date] = []
                continue

            bluray = self.__parse_blurays_monthly_article(tag)
            blurays[current_date].append(bluray)

        return BluraysMonthlyByReleaseDate({
            "blurays": blurays,
            "has_prev_page": self.parse_blurays_monthly_has_prev_page(s),
            "has_next_page": self.parse_blurays_monthly_has_next_page(s),
        })

    def parse_blurays_monthly_by_rating(self, s: BeautifulSoup) -> BluraysMonthlyByRating:
        content = sel(s, ".box-content.box-content-striped-articles")
        blurays = []
        for article in asel(content, "article"):
            blurays.append(self.__parse_blurays_monthly_article(article))
        return BluraysMonthlyByRating({
            "blurays": blurays,
            "has_prev_page": self.parse_blurays_monthly_has_prev_page(s),
            "has_next_page": self.parse_blurays_monthly_has_next_page(s),
        })

    # BLURAYS YEARLY

    @staticmethod
    def __parse_blurays_yearly_tr(s: BeautifulSoup, date: str) -> BlurayYearly:
        tr_a = sel(s, ".movies a")
        return BlurayYearly({
            "id": extract_id(tr_a.get("href")),
            "name": text(tr_a),
            "year": toint(text(s, ".movies .film-title-info .info")),
            "types": clean(text(s, ".movies > .info"))[2:].split(" / "),
            "date": date,
        })

    def parse_blurays_yearly_by_release_date(self, s: BeautifulSoup) -> BluraysYearlyByReleaseDate:
        blurays = {}
        for content in asel(s, ".box-content:not(.box-content-striped-articles)"):
            month_name = text(content, ".box-sub-header").split(" ")[0]
            month = Months.get_by_czech_name(month_name)
            blurays[month] = []
            current_date = None

            for tr in asel(content, "table tbody tr"):
                date_td = sel(tr, "td.date-only")

                if date_td is not None:
                    current_date = text(date_td)

                bluray = self.__parse_blurays_yearly_tr(tr, current_date)
                blurays[month].append(bluray)

        return BluraysYearlyByReleaseDate({"blurays": blurays})

    def parse_dvds_yearly_by_rating(self, s: BeautifulSoup) -> BluraysYearlyByRating:
        blurays = []
        current_date = None
        for tr in asel(s, "table tbody tr"):
            date_td = sel(tr, "td.date-only")

            if date_td is not None:
                current_date = text(date_td)

            blurays.append(self.__parse_blurays_yearly_tr(tr, current_date))

        return BluraysYearlyByRating({"blurays": blurays})

class LeaderboardsParser:

    # GENERICS

    @staticmethod
    def __parse_leaderboards_parse_creators(s: BeautifulSoup, name: str) -> List[dict]:
        creators = []
        for p in asel(s, ".film-creators"):
            if text(p).split(":")[0] == name:
                for a in asel(p, "a"):
                    creators.append({
                        "id": extract_id(a.get("href")),
                        "name": text(a),
                    })
        return creators

    @staticmethod
    def __parse_leaderboards_parse_rating(s: BeautifulSoup) -> dict:
        rating_average = sel(s, ".article-toplist-rating .rating-average")
        rating_total = sel(s, ".article-toplist-rating .rating-total")

        if rating_average and rating_total:
            return {
                "percentage": float(text(rating_average).replace(",", ".")[:-1]),
                "rating_count": toint(text(rating_total))
            }

        return {
            "fan_count": toint(text(rating_total))
        }

    def parse_leaderboards_article(self, s: BeautifulSoup, cls: Type):
        img = sel(s, "img")
        articla_a = sel(s, ".article-content a")
        origins_genres = text(s, ".film-origins-genres .info").split(", ")
        return cls({
            "id": extract_id(articla_a.get("href")),
            "position": toint(text(s, ".article-content .film-title-user")),
            "year": int(text(s, "span.info")[1:-1]),
            "title": text(articla_a),
            "genres": [] if len(origins_genres) == 1 else origins_genres[-1].split(" / "),
            "origins": origins_genres[0].split(" / ") if len(origins_genres) > 1 else [],
            "directors": self.__parse_leaderboards_parse_creators(s, "Režie"),
            "actors": self.__parse_leaderboards_parse_creators(s, "Hrají"),
            "rating": self.__parse_leaderboards_parse_rating(s),
            "image": url(img.get("src")) if img else None
        })
    
    def parse_leaderboards_person(self, s: BeautifulSoup) -> LeaderboardPerson:
        img = sel(s, "img")
        position = sel(s, ".article-content .user-title-position")
        articla_a = sel(s, ".article-content a")
        origin = sel(s, ".article-content p .info")
        p_rating = sel(s, ".article-content .p-rating a")
        return LeaderboardPerson({
            "id": extract_id(articla_a.get("href")),
            "position": toint(text(position)) if position else -1,
            "name": text(articla_a),
            "origin": text(origin) if origin else None,
            "fan_count": toint(text(p_rating)) if p_rating else -1,
            "image": url(img.get("src")) if img else None
        })
    
    def parse_leaderboards_person_best_movie(self, s: BeautifulSoup) -> LeaderboardPersonBestMovie:
        img = sel(s, "img")
        position = sel(s, ".article-content .user-title-position")
        articla_a = sel(s, ".article-content a")
        origin_and_movie_count = sel(s, ".article-content p .info")
        origin_and_movie_count = text(origin_and_movie_count, recursive=True) if origin_and_movie_count else None
        p_rating = sel(s, ".article-content .p-rating strong")
        return LeaderboardPersonBestMovie({
            "id": extract_id(articla_a.get("href")),
            "position": toint(text(position)) if position else -1,
            "name": text(articla_a),
            "origin": origin_and_movie_count.split(", ")[0] if origin_and_movie_count else None,
            "movie_count": toint(origin_and_movie_count.split(", ")[1]) if origin_and_movie_count else -1,
            "avg_rating": float(text(p_rating).replace(",", ".")[:-1]) if p_rating else -1,
            "image": url(img.get("src")) if img else None
        })
    
    # MOVIES

    def parse_leaderboards_movies(self, s: BeautifulSoup) -> List[LeaderboardMovie]:
        return [
            self.parse_leaderboards_article(article, LeaderboardMovie)
            for article in asel(s, "section.box article[id^='highlight-']")
        ]

    # SERIALS

    def parse_leaderboards_serials(self, s: BeautifulSoup) -> List[LeaderboardSerial]:
        return [
            self.parse_leaderboards_article(article, LeaderboardSerial)
            for article in asel(s, "section.box article[id^='highlight-']")
        ]
    
    # ACTORS & ACTRESSES

    def parse_leaderboards_actors(self, s: BeautifulSoup) -> List[LeaderboardPerson]:
        return [
            self.parse_leaderboards_person(article)
            for article in asel(asel(s, "section.box")[0], "article[id^='highlight-']")
        ]

    def parse_leaderboards_actresses(self, s: BeautifulSoup) -> List[LeaderboardPerson]:
        return [
            self.parse_leaderboards_person(article)
            for article in asel(asel(s, "section.box")[1], "article[id^='highlight-']")
        ]

    def parse_leaderboards_all_actors(self, s: BeautifulSoup) -> LeaderboardActors:
        return LeaderboardActors({
            "actors": self.parse_leaderboards_actors(s),
            "actresses": self.parse_leaderboards_actresses(s)
        })
    
    # DIRECTORS

    def parse_leaderboards_directors(self, s: BeautifulSoup) -> List[LeaderboardPerson]:
        return [
            self.parse_leaderboards_person(article)
            for article in asel(asel(s, "section.box")[0], "article[id^='highlight-']")
        ]
    
    def parse_leaderboards_directors_with_best_movie(self, s: BeautifulSoup) -> List[LeaderboardPersonBestMovie]:
        return [
            self.parse_leaderboards_person_best_movie(article)
            for article in asel(asel(s, "section.box")[1], "article[id^='highlight-']")
        ]

    def parse_leaderboards_all_directors(self, s: BeautifulSoup) -> LeaderboardDirectors:
        return LeaderboardDirectors({
            "directors": self.parse_leaderboards_directors(s),
            "with_best_movie": self.parse_leaderboards_directors_best_movie(s)
        })
    
    # OTHERS (SCREENWRITERS, CINEMATOGRAPHERS & COMPOSERS)

    def parse_leaderboards_screenwriters(self, s: BeautifulSoup) -> List[LeaderboardPerson]:
        return [
            self.parse_leaderboards_person(article)
            for article in asel(asel(s, "section.box")[0], "article[id^='highlight-']")
        ]

    def parse_leaderboards_cinematographers(self, s: BeautifulSoup) -> List[LeaderboardPerson]:
        return [
            self.parse_leaderboards_person(article)
            for article in asel(asel(s, "section.box")[1], "article[id^='highlight-']")
        ]

    def parse_leaderboards_composers(self, s: BeautifulSoup) -> List[LeaderboardPerson]:
        return [
            self.parse_leaderboards_person(article)
            for article in asel(asel(s, "section.box")[2], "article[id^='highlight-']")
        ]
    
    def parse_leaderboards_others(self, s: BeautifulSoup) -> LeaderboardOthers:
        return LeaderboardOthers({
            "screenwriters": self.parse_leaderboards_screenwriters(s),
            "cinematographers": self.parse_leaderboards_cinematographers(s),
            "composers": self.parse_leaderboards_composers(s)
        })
    
    # CUSTOM

    def parse_leaderboards_custom_records(self, s: BeautifulSoup) -> List[LeaderboardMovie]:
        return [
            self.parse_leaderboards_article(article, LeaderboardMovie)
            for article in asel(s, "section.box article[id^='highlight-']")
        ]

    @staticmethod
    def parse_leaderboards_custom_has_prev_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-prev") is not None

    @staticmethod
    def parse_leaderboards_custom_has_next_page(s: BeautifulSoup) -> bool:
        return sel(s, ".page-next") is not None

    def parse_leaderboards_custom(self, s: BeautifulSoup, page: int) -> LeaderboardCustom:
        return LeaderboardCustom({
            "page": page,
            "records": self.parse_leaderboards_custom_records(s),
            "has_prev_page": self.parse_leaderboards_custom_has_prev_page(s),
            "has_next_page": self.parse_leaderboards_custom_has_next_page(s)
        })
