import os
import sys
import requests as r
from utils import url_prepare, soup, Globals
from parsers import MovieParser, CreatorParser
from objects import Movie, Creator, CreatorFilmographySort

class CsfdScraperInvalidRequest(Exception):
    """Exception for invalid request"""
    pass

class CsfdScraper:
    __LAST_SOUP = None
    __MOVIE_PARSER = MovieParser()
    __CREATOR_PARSER = CreatorParser()

    def __reset(self):
        self.__LAST_SOUP = None
        self.__MOVIE_PARSER.reset()
        self.__CREATOR_PARSER.reset()

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

    def __get_soup(self, s=None):
        if not self.__LAST_SOUP:
            self.__LAST_SOUP = soup(s)
        return self.__LAST_SOUP

    def __get_movie_soup(self, mid):
        return self.__get_soup(self.__get(Globals.MOVIES_URL + str(mid)).content)

    def __get_creator_soup(self, cid):
        return self.__get_soup(self.__get(Globals.CREATORS_URL + str(cid)).content)

    def __get_creator_sort_soup(self, cid, sort):
        url = url_prepare(Globals.CREATORS_SORT_URL, {"cid": cid, "sort": sort.value})
        return self.__get_soup(self.__get(url).content)

    # MOVIE

    def movie(self, mid) -> Movie:
        return self.__MOVIE_PARSER.parse_movie(self.__get_movie_soup(mid), mid)

    @staticmethod
    def movie_url(mid):
        return Globals.MOVIES_URL + str(mid)

    def movie_type(self, mid):
        return self.__MOVIE_PARSER.parse_movie_type(self.__get_movie_soup(mid))

    def movie_title(self, mid):
        return self.__MOVIE_PARSER.parse_movie_title(self.__get_movie_soup(mid))

    def movie_year(self, mid):
        return self.__MOVIE_PARSER.parse_movie_year(self.__get_movie_soup(mid))

    def movie_duration(self, mid):
        return self.__MOVIE_PARSER.parse_movie_duration(self.__get_movie_soup(mid))

    def movie_genres(self, mid):
        return self.__MOVIE_PARSER.parse_movie_genres(self.__get_movie_soup(mid))

    def movie_origins(self, mid):
        return self.__MOVIE_PARSER.parse_movie_origins(self.__get_movie_soup(mid))

    def movie_rating(self, mid):
        return self.__MOVIE_PARSER.parse_movie_rating(self.__get_movie_soup(mid))

    def movie_ranks(self, mid):
        return self.__MOVIE_PARSER.parse_movie_ranks(self.__get_movie_soup(mid))

    def movie_other_names(self, mid):
        return self.__MOVIE_PARSER.parse_movie_other_names(self.__get_movie_soup(mid))

    def movie_creators(self, mid):
        return self.__MOVIE_PARSER.parse_movie_creators(self.__get_movie_soup(mid))

    def movie_vods(self, mid):
        return self.__MOVIE_PARSER.parse_movie_vods(self.__get_movie_soup(mid))

    def movie_tags(self, mid):
        return self.__MOVIE_PARSER.parse_movie_tags(self.__get_movie_soup(mid))

    def movie_reviews_count(self, mid):
        return self.__MOVIE_PARSER.parse_movie_reviews_count(self.__get_movie_soup(mid))

    def movie_reviews(self, mid):
        return self.__MOVIE_PARSER.parse_movie_reviews(self.__get_movie_soup(mid))

    def movie_gallery_count(self, mid):
        return self.__MOVIE_PARSER.parse_movie_gallery_count(self.__get_movie_soup(mid))

    def movie_gallery(self, mid):
        return self.__MOVIE_PARSER.parse_movie_gallery(self.__get_movie_soup(mid))

    def movie_trivia_count(self, mid):
        return self.__MOVIE_PARSER.parse_movie_trivia_count(self.__get_movie_soup(mid))

    def movie_trivia(self, mid):
        return self.__MOVIE_PARSER.parse_movie_trivia(self.__get_movie_soup(mid))

    def movie_premieres(self, mid):
        return self.__MOVIE_PARSER.parse_movie_premieres(self.__get_movie_soup(mid))

    def movie_plot(self, mid):
        return self.__MOVIE_PARSER.parse_movie_plot(self.__get_movie_soup(mid))

    def movie_cover(self, mid):
        return self.__MOVIE_PARSER.parse_movie_cover(self.__get_movie_soup(mid))

    # CREATOR

    def creator(self, cid, sort: CreatorFilmographySort = CreatorFilmographySort.NEWEST) -> Creator:
        return self.__CREATOR_PARSER.parse_creator(self.__get_creator_sort_soup(cid, sort), cid)

    @staticmethod
    def creator_url(cid):
        return Globals.CREATORS_URL + str(cid)

    def creator_type(self, cid):
        return self.__CREATOR_PARSER.parse_creator_type(self.__get_creator_soup(cid))

    def creator_name(self, cid):
        return self.__CREATOR_PARSER.parse_creator_name(self.__get_creator_soup(cid))

    def creator_age(self, cid):
        return self.__CREATOR_PARSER.parse_creator_age(self.__get_creator_soup(cid))

    def creator_birth_date(self, cid):
        return self.__CREATOR_PARSER.parse_creator_birth_date(self.__get_creator_soup(cid))

    def creator_birth_place(self, cid):
        return self.__CREATOR_PARSER.parse_creator_birth_place(self.__get_creator_soup(cid))

    def creator_bio(self, cid):
        return self.__CREATOR_PARSER.parse_creator_bio(self.__get_creator_soup(cid))

    def creator_trivia_count(self, cid):
        return self.__CREATOR_PARSER.parse_creator_trivia_count(self.__get_creator_soup(cid))

    def creator_trivia(self, cid):
        return self.__CREATOR_PARSER.parse_creator_trivia(self.__get_creator_soup(cid))

    def creator_ranks(self, cid):
        return self.__CREATOR_PARSER.parse_creator_ranks(self.__get_creator_soup(cid))

    def creator_gallery_count(self, cid):
        return self.__CREATOR_PARSER.parse_creator_gallery_count(self.__get_creator_soup(cid))

    def creator_gallery(self, cid):
        return self.__CREATOR_PARSER.parse_creator_gallery(self.__get_creator_soup(cid))

    def creator_filmography(self, cid, sort: CreatorFilmographySort = CreatorFilmographySort.NEWEST):
        return self.__CREATOR_PARSER.parse_creator_filmography(self.__get_creator_sort_soup(cid, sort))

    def creator_image(self, cid):
        return self.__CREATOR_PARSER.parse_creator_image(self.__get_creator_soup(cid))
