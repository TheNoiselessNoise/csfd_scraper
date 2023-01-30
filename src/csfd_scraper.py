import json
import requests
from datetime import datetime
from src.csfd_objects import *
from src.csfd_utils import encode_params, url_prepare, soup, Globals
from src.csfd_parsers import MovieParser, CreatorParser, SearchParser, UserParser

class CsfdScraper:
    __LAST_SOUP = None
    __MOVIE_PARSER = MovieParser()
    __CREATOR_PARSER = CreatorParser()
    __SEARCH_PARSER = SearchParser()
    __USER_PARSER = UserParser()

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
        return self.__request(requests.get, *args)
    def __post(self, *args):
        self.__reset()
        return self.__request(requests.post, *args)

    def __get_soup(self, s=None):
        if s is None and self.__LAST_SOUP is None:
            return None
        if s is None and self.__LAST_SOUP:
            return self.__LAST_SOUP

        if not self.__LAST_SOUP:
            self.__LAST_SOUP = soup(s)
        return self.__LAST_SOUP
    def __get_movie_soup(self, mid):
        return self.__get_soup() or self.__get_soup(self.__get(Globals.MOVIES_URL + str(mid)).content)
    def __get_creator_soup(self, cid):
        return self.__get_soup() or self.__get_soup(self.__get(Globals.CREATORS_URL + str(cid)).content)
    def __get_user_soup(self, uid):
        return self.__get_soup() or self.__get_soup(self.__get(Globals.USERS_URL + str(uid)).content)
    def __get_text_search_soup(self, search, page):
        url = url_prepare(Globals.TEXT_SEARCH_URL, {"search": search, "page": page})
        return self.__get_soup() or self.__get_soup(self.__get(url).content)
    def __get_creator_sort_soup(self, cid, sort):
        url = url_prepare(Globals.CREATORS_SORT_URL, {"cid": cid, "sort": sort.value})
        return self.__get_soup() or self.__get_soup(self.__get(url).content)
    def __get_search_movies_soup(self, params, sort, page):
        params = encode_params(params)
        url = url_prepare(Globals.SEARCH_MOVIES_URL, {"page": page, "sort": sort.value, "params": params})
        return self.__get_soup() or self.__get_soup(self.__get(url).content)
    def __get_search_creators_soup(self, params, sort, page):
        params = encode_params(params)
        url = url_prepare(Globals.SEARCH_CREATORS_URL, {"page": page, "sort": sort.value, "params": params})
        return self.__get_soup() or self.__get_soup(self.__get(url).content)

    # SEARCH GENERICS

    def search_tags(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "tag", "search": search})
        return [Tag(x) for x in json.loads(self.__get(url).content)]
    def search_movies(self, options, sort=MovieSearchSort.BY_RATING_COUNT, page=1):
        params = {}
        for key, param in MovieSearchParameters.__members__.items():
            name = param.value[0]
            default = param.value[1]

            opt = MovieSearchOptions.__members__[key]
            opt_value = options.get(param, default)

            if opt in [MovieSearchOptions.TYPES, MovieSearchOptions.ADDITIONAL_FILTERS]:
                params[name] = [x.value for x in opt_value]
            elif opt == MovieSearchOptions.GENRES:
                genre_filter = opt_value.get(MovieSearchGenreOptions.FILTER, MovieSearchGenreFilters.AT_LEAST_ALL_SELECTED).value
                genres = opt_value.get(MovieSearchGenreOptions.GENRES, [])
                exclude = opt_value.get(MovieSearchGenreOptions.EXCLUDE, [])
                params[name] = {1: [], 2: [], 3: [], 4: [], "type": genre_filter}
                params[name][genre_filter] = [x.value[0] for x in genres]
                params[name][4] = [x.value[0] for x in exclude]
            elif opt == MovieSearchOptions.ORIGINS:
                origin_filter = opt_value.get(MovieSearchOriginOptions.FILTER, MovieSearchOriginFilters.AT_LEAST_ALL_SELECTED).value
                origins = opt_value.get(MovieSearchOriginOptions.ORIGINS, [])
                exclude = opt_value.get(MovieSearchOriginOptions.EXCLUDE, [])
                params[name] = {1: [], 2: [], 3: [], 4: [], "type": origin_filter}
                params[name][origin_filter] = [x.value[0] for x in origins]
                params[name][4] = [x.value[0] for x in exclude]
            else:
                params[name] = opt_value

        s = self.__get_search_movies_soup(params, sort, page)
        return self.__SEARCH_PARSER.parse_movies_search(s, page)
    def search_creators(self, options, sort=CreatorSearchSort.BY_FAN_COUNT, page=1):
        params = {}
        for key, param in CreatorSearchParameters.__members__.items():
            name = param.value[0]
            default = param.value[1]

            opt = CreatorSearchOptions.__members__[key]
            opt_value = options.get(param, default)

            if opt == CreatorSearchOptions.TYPES:
                params[name] = [x.value[0] for x in opt_value]
            elif opt in [CreatorSearchOptions.BIRTH_FROM, CreatorSearchOptions.BIRTH_TO]:
                params[name] = {
                    "date": None if opt_value is None else opt_value,
                    "year": None if opt_value is None else datetime.strptime(opt_value, "%d.%m.%Y").strftime("%Y")
                }
            elif opt in [CreatorSearchOptions.DEATH_FROM, CreatorSearchOptions.DEATH_TO]:
                params[name] = {
                    "date": None if opt_value is None else opt_value,
                    "year": None if opt_value is None else datetime.strptime(opt_value, "%d.%m.%Y").strftime("%Y")
                }
            elif opt in [CreatorSearchOptions.BIRTH_COUNTRY, CreatorSearchOptions.DEATH_COUNTRY]:
                params[name] = None if opt_value is None else opt_value.value[0]
            elif opt == CreatorSearchOptions.ADDITIONAL_FILTERS:
                params[name] = [x.value for x in opt_value]
            elif opt == CreatorSearchOptions.GENDER:
                params[name] = opt_value.value
            else:
                params[name] = opt_value

        s = self.__get_search_creators_soup(params, sort, page)
        return self.__SEARCH_PARSER.parse_creators_search(s, page)

    def text_search(self, search, page=1):
        return self.__SEARCH_PARSER.parse_text_search(self.__get_text_search_soup(search, page))
    def text_search_movies(self, search, page=1):
        return self.__SEARCH_PARSER.parse_text_search_movies(self.__get_text_search_soup(search, page))
    def text_search_creators(self, search, page=1):
        return self.__SEARCH_PARSER.parse_text_search_creators(self.__get_text_search_soup(search, page))
    def text_search_series(self, search, page=1):
        return self.__SEARCH_PARSER.parse_text_search_series(self.__get_text_search_soup(search, page))
    def text_search_users(self, search, page=1):
        return self.__SEARCH_PARSER.parse_text_search_users(self.__get_text_search_soup(search, page))

    # SEARCH FILM CREATORS

    def search_actors(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "actors", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_directors(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "director", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_composers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "composer", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_screenwriters(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "screenwriter", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_authors(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "author", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_cinematographers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "cinematographer", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_producers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "production", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_editors(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "edit", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_sound_engineers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "sound", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_scenographers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "scenography", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_mask_designers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "mask", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]
    def search_costume_designers(self, search):
        url = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "costumes", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(url).content)]

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

    def creator(self, cid, sort: CreatorFilmographySort = CreatorFilmographySort.BY_NEWEST) -> Creator:
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
    def creator_filmography(self, cid, sort: CreatorFilmographySort = CreatorFilmographySort.BY_NEWEST):
        return self.__CREATOR_PARSER.parse_creator_filmography(self.__get_creator_sort_soup(cid, sort))
    def creator_image(self, cid):
        return self.__CREATOR_PARSER.parse_creator_image(self.__get_creator_soup(cid))

    # USER

    def user(self, mid) -> User:
        return self.__USER_PARSER.parse_user(self.__get_user_soup(mid), mid)
    @staticmethod
    def user_url(uid):
        return Globals.USERS_URL + str(uid)
    def user_name(self, uid):
        return self.__USER_PARSER.parse_user_name(self.__get_user_soup(uid))
    def user_real_name(self, uid):
        return self.__USER_PARSER.parse_user_real_name(self.__get_user_soup(uid))
    def user_origin(self, uid):
        return self.__USER_PARSER.parse_user_origin(self.__get_user_soup(uid))
    def user_about(self, uid):
        return self.__USER_PARSER.parse_user_about(self.__get_user_soup(uid))
    def user_registered(self, uid):
        return self.__USER_PARSER.parse_user_registered(self.__get_user_soup(uid))
    def user_last_login(self, uid):
        return self.__USER_PARSER.parse_user_last_login(self.__get_user_soup(uid))
    def user_points(self, uid):
        return self.__USER_PARSER.parse_user_points(self.__get_user_soup(uid))
    def user_awards(self, uid):
        return self.__USER_PARSER.parse_user_awards(self.__get_user_soup(uid))
    def user_most_watched_genres(self, uid):
        return self.__USER_PARSER.parse_user_most_watched_genres(self.__get_user_soup(uid))
    def user_most_watched_types(self, uid):
        return self.__USER_PARSER.parse_user_most_watched_types(self.__get_user_soup(uid))
    def user_most_watched_origins(self, uid):
        return self.__USER_PARSER.parse_user_most_watched_origins(self.__get_user_soup(uid))
    def user_reviews_count(self, uid):
        return self.__USER_PARSER.parse_user_reviews_count(self.__get_user_soup(uid))
    def user_reviews(self, uid):
        return self.__USER_PARSER.parse_user_reviews(self.__get_user_soup(uid))
    def user_ratings_count(self, uid):
        return self.__USER_PARSER.parse_user_ratings_count(self.__get_user_soup(uid))
    def user_ratings(self, uid):
        return self.__USER_PARSER.parse_user_ratings(self.__get_user_soup(uid))
    def user_is_currently_online(self, uid):
        return self.__USER_PARSER.parse_user_is_currently_online(self.__get_user_soup(uid))
    def user_image(self, uid):
        return self.__USER_PARSER.parse_user_image(self.__get_user_soup(uid))
