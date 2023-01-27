import bs4
import json
import requests as r
from utils import soup, Globals
from parsers import MovieParser

class CsfdScraperInvalidRequest(Exception):
    """Exception for invalid request"""
    pass

class CsfdScraper:
    __LAST_SOUP = None
    __MOVIE_PARSER = MovieParser()

    def __reset(self):
        self.__LAST_SOUP = None
        self.__MOVIE_PARSER.reset()

    @staticmethod
    def __request(func, url, params=None):
        response = func(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            raise CsfdScraperInvalidRequest("Invalid request at url: " + url)
        return response

    def __get(self, *args):
        self.__reset()
        return self.__request(r.get, *args)

    def __post(self, *args):
        self.__reset()
        return self.__request(r.post, *args)

    def __get_movie_soup(self, mid):
        if not self.__LAST_SOUP:
            self.__LAST_SOUP = soup(self.__get(Globals.MOVIES_URL + str(mid)).content)
        return self.__LAST_SOUP

    @staticmethod
    def __json(o):
        if type(o) not in [dict, list]:
            return o
        return json.dumps(o, indent=4, ensure_ascii=False)

    # MOVIE

    def movie(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie(self.__get_movie_soup(mid), mid))

    def movie_url(self, mid):
        return self.__json(Globals.MOVIES_URL + str(mid))

    def movie_type(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_type(self.__get_movie_soup(mid)))

    def movie_title(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_title(self.__get_movie_soup(mid)))

    def movie_year(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_year(self.__get_movie_soup(mid)))

    def movie_duration(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_duration(self.__get_movie_soup(mid)))

    def movie_genres(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_genres(self.__get_movie_soup(mid)))

    def movie_origins(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_origins(self.__get_movie_soup(mid)))

    def movie_rating(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_rating(self.__get_movie_soup(mid)))

    def movie_other_names(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_other_names(self.__get_movie_soup(mid)))

    def movie_creators(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_creators(self.__get_movie_soup(mid)))

    def movie_vods(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_vods(self.__get_movie_soup(mid)))

    def movie_tags(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_tags(self.__get_movie_soup(mid)))

    def movie_reviews(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_reviews(self.__get_movie_soup(mid)))

    def movie_gallery(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_gallery(self.__get_movie_soup(mid)))

    def movie_trivia(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_trivia(self.__get_movie_soup(mid)))

    def movie_premieres(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_premieres(self.__get_movie_soup(mid)))

    def movie_description(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_description(self.__get_movie_soup(mid)))

    def movie_cover(self, mid):
        return self.__json(self.__MOVIE_PARSER.parse_movie_cover(self.__get_movie_soup(mid)))

