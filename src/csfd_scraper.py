import requests
from datetime import datetime
from src.csfd_parsers import *
from bs4 import BeautifulSoup
from typing import List, Optional

class CsfdScraper:
    DEBUG: bool = False

    __LAST_URL: Optional[str]            = None
    __LAST_SOUP: Optional[BeautifulSoup] = None

    __MOVIE_PARSER: MovieParser               = MovieParser()
    __CREATOR_PARSER: CreatorParser           = CreatorParser()
    __SEARCH_PARSER: SearchParser             = SearchParser()
    __USER_PARSER: UserParser                 = UserParser()
    __NEWS_PARSER: NewsParser                 = NewsParser()
    __USERS_PARSER: UsersParser               = UsersParser()
    __DVDS_PARSER: DvdsParser                 = DvdsParser()
    __BLURAYS_PARSER: BluraysParser           = BluraysParser()
    __LEADERBOARDS_PARSER: LeaderboardsParser = LeaderboardsParser()

    def get_last_url(self):
        return self.__LAST_URL

    def __reset(self) -> None:
        self.__MOVIE_PARSER.reset()
        self.__CREATOR_PARSER.reset()
    @staticmethod
    def __request(func: callable, u: str, params: Optional[dict] = None) -> requests.Response:
        if CsfdScraper.DEBUG:
            print("Requesting: " + u)
        response = func(u, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            raise CsfdScraperInvalidRequest("Invalid request at url: " + u)
        return response
    def __get(self, *args) -> requests.Response:
        return self.__request(requests.get, *args)
    def __post(self, *args) -> requests.Response:
        return self.__request(requests.post, *args)

    # <editor-fold desc="SOUPS">
    def __get_soup(self, u: str) -> BeautifulSoup:
        if u == self.__LAST_URL and self.__LAST_SOUP:
            return self.__LAST_SOUP
        self.__LAST_URL = u
        self.__LAST_SOUP = soup(self.__get(u).content)
        return self.__LAST_SOUP
    def __get_movie_soup(self, mid: int) -> BeautifulSoup:
        return self.__get_soup(Globals.MOVIES_URL + str(mid))
    def __get_creator_soup(self, cid: int) -> BeautifulSoup:
        return self.__get_soup(Globals.CREATORS_URL + str(cid))
    def __get_user_soup(self, uid: int) -> BeautifulSoup:
        return self.__get_soup(Globals.USERS_URL + str(uid))
    def __get_news_soup(self, nid: int) -> BeautifulSoup:
        return self.__get_soup(Globals.NEWS_URL + str(nid))
    def __get_news_list_soup(self, page: int) -> BeautifulSoup:
        return self.__get_soup(url_prepare(Globals.NEWS_LIST_URL, {"page": page}))
    def __get_most_favorite_users_soup(self) -> BeautifulSoup:
        return self.__get_soup(Globals.MOST_FAVORITE_USERS_URL)
    def __get_most_active_users_soup(self, origin: Optional[Origins], sort: ActiveUsersSorts) -> BeautifulSoup:
        if origin is None:
            u = url_prepare(Globals.ALL_MOST_ACTIVE_USERS_URL, {"sort": sort.value})
        else:
            u = url_prepare(Globals.MOST_ACTIVE_USERS_URL, {"sort": sort.value, "origin": origin.value[0]})
        return self.__get_soup(u)
    def __get_text_search_soup(self, search: str, page: int) -> BeautifulSoup:
        return self.__get_soup(url_prepare(Globals.TEXT_SEARCH_URL, {"search": search, "page": page}))
    def __get_creator_sort_soup(self, cid: int, sort: CreatorFilmographySorts) -> BeautifulSoup:
        return self.__get_soup(url_prepare(Globals.CREATORS_SORT_URL, {"cid": cid, "sort": sort.value}))
    def __get_search_movies_soup(self, params: dict, page: int, sort: MovieSorts) -> BeautifulSoup:
        u = url_prepare(Globals.SEARCH_MOVIES_URL, {"page": page, "sort": sort.value, "params": encode_params(params)})
        return self.__get_soup(u)
    def __get_search_creators_soup(self, params: dict, page: int, sort: CreatorSorts) -> BeautifulSoup:
        u = url_prepare(Globals.SEARCH_CREATORS_URL, {"page": page, "sort": sort.value, "params": encode_params(params)})
        return self.__get_soup(u)
    def __get_dvds_monthly_soup(self, year: Optional[int], month: Months, page: int, sort: str) -> BeautifulSoup:
        args = {"year": year, "month": month.value[0], "page": page}
        if sort != "release_date":
            args["sort"] = sort
        return self.__get_soup(url_params(Globals.DVDS_MONTHLY_ROOT_URL, args))
    def __get_dvds_yearly_soup(self, year: Optional[int], sort: str) -> BeautifulSoup:
        args = {"year": year}
        if sort != "release_date":
            args['sort'] = sort
        return self.__get_soup(url_params(Globals.DVDS_YEARLY_URL, args))
    def __get_blurays_monthly_soup(self, year: Optional[int], month: Months, page: int, sort: str) -> BeautifulSoup:
        args = {"year": year, "month": month.value[0], "page": page}
        if sort != "release_date":
            args['sort'] = sort
        u = url_params(Globals.BLURAYS_MONTHLY_URL, args)
        return self.__get_soup(u)
    def __get_blurays_yearly_soup(self, year: Optional[int], sort: str) -> BeautifulSoup:
        args = {"year": year}
        if sort != "release_date":
            args['sort'] = sort
        return self.__get_soup(url_params(Globals.BLURAYS_YEARLY_URL, args))
    def __get_user_ratings_soup(
            self,
            uid: int,
            mtype: Optional[MovieTypes],
            origin: Optional[Origins],
            genre: Optional[MovieGenres],
            sort: UserRatingsSorts,
            page: int
    ) -> BeautifulSoup:
        u = url_prepare(Globals.USER_RATINGS_URL, {"uid": uid})
        u = url_params(u, {
            "type": None if mtype is None else mtype.value,
            "origin": None if origin is None else origin.value[0],
            "genre": None if genre is None else genre.value[0],
            "sort": sort.value,
            "page": page
        })
        return self.__get_soup(u)
    def __get_user_reviews_soup(
            self,
            uid: int,
            mtype: Optional[MovieTypes],
            origin: Optional[Origins],
            genre: Optional[MovieGenres],
            sort: UserReviewsSorts,
            page: int
    ) -> BeautifulSoup:
        u = url_prepare(Globals.USER_REVIEWS_URL, {"uid": uid})
        u = url_params(u, {
            "type": None if mtype is None else mtype.value,
            "country": None if origin is None else origin.value[0],
            "genre": None if genre is None else genre.value[0],
            "sort": sort.value,
            "page": page
        })
        return self.__get_soup(u)
    def __get_leaderboards_movies_best_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_MOVIES_BEST, args)
        return self.__get_soup(u)
    def __get_leaderboards_movies_most_popular_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_MOVIES_MOST_POPULAR, args)
        return self.__get_soup(u)
    def __get_leaderboards_movies_most_controversial_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_MOVIES_MOST_CONTROVERSIAL, args)
        return self.__get_soup(u)
    def __get_leaderboards_movies_worst_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_MOVIES_WORST, args)
        return self.__get_soup(u)
    def __get_leaderboards_serials_best_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_SERIALS_BEST, args)
        return self.__get_soup(u)
    def __get_leaderboards_serials_most_popular_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_SERIALS_MOST_POPULAR, args)
        return self.__get_soup(u)
    def __get_leaderboards_serials_most_controversial_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_SERIALS_MOST_CONTROVERSIAL, args)
        return self.__get_soup(u)
    def __get_leaderboards_serials_worst_soup(self, _from: int):
        args = {} if _from == 1 else {"from": _from}
        u = url_params(Globals.LEADERBOARDS_SERIALS_WORST, args)
        return self.__get_soup(u)
    def __get_leaderboards_actors_and_actresses_soup(self, from_actors: int, from_actresses: int):
        args = {} if from_actors == 1 else {"fromLeft": from_actors}
        if from_actresses != 1:
            args.update({"fromRight": from_actresses})
        u = url_params(Globals.LEADERBOARDS_ACTORS, args)
        return self.__get_soup(u)
    def __get_leaderboards_directors_soup(self, from_directors: int, from_with_best_movie: int):
        args = {} if from_directors == 1 else {"fromLeft": from_directors}
        if from_with_best_movie != 1:
            args.update({"fromRight": from_with_best_movie})
        u = url_params(Globals.LEADERBOARDS_DIRECTORS, args)
        return self.__get_soup(u)

    # </editor-fold>

    # <editor-fold desc="SEARCH">
    def search_movies(self, options: dict, page: int = 1, sort: MovieSorts = MovieSorts.BY_RATING_COUNT) -> SearchMoviesResult:
        params = {}
        for key, param in MovieParams.__members__.items():
            name = param.value[0]
            default = param.value[1]

            opt = MovieOptions.__members__[key]
            opt_value = options.get(param, default)

            if opt in [MovieOptions.TYPES, MovieOptions.ADDITIONAL_FILTERS]:
                params[name] = [x.value for x in opt_value]
            elif opt == MovieOptions.GENRES:
                genre_filter = opt_value.get(MovieGenreOptions.FILTER, MovieGenreFilters.AT_LEAST_ALL_SELECTED).value
                genres = opt_value.get(MovieGenreOptions.GENRES, [])
                exclude = opt_value.get(MovieGenreOptions.EXCLUDE, [])
                params[name] = {1: [], 2: [], 3: [], 4: [], "type": genre_filter}
                params[name][genre_filter] = [x.value[0] for x in genres]
                params[name][4] = [x.value[0] for x in exclude]
            elif opt == MovieOptions.ORIGINS:
                origin_filter = opt_value.get(MovieOriginOptions.FILTER, MovieOriginFilters.AT_LEAST_ALL_SELECTED).value
                origins = opt_value.get(MovieOriginOptions.ORIGINS, [])
                exclude = opt_value.get(MovieOriginOptions.EXCLUDE, [])
                params[name] = {1: [], 2: [], 3: [], 4: [], "type": origin_filter}
                params[name][origin_filter] = [x.value[0] for x in origins]
                params[name][4] = [x.value[0] for x in exclude]
            else:
                params[name] = opt_value

        s = self.__get_search_movies_soup(params, page, sort)
        return self.__SEARCH_PARSER.parse_movies_search(s, page)
    def search_creators(self, options: dict, page: int = 1, sort: CreatorSorts = CreatorSorts.BY_FAN_COUNT) -> SearchCreatorsResult:
        params = {}
        for key, param in CreatorParams.__members__.items():
            name = param.value[0]
            default = param.value[1]

            opt = CreatorOptions.__members__[key]
            opt_value = options.get(param, default)

            if opt == CreatorOptions.TYPES:
                params[name] = [x.value[0] for x in opt_value]
            elif opt in [CreatorOptions.BIRTH_FROM, CreatorOptions.BIRTH_TO]:
                params[name] = {
                    "date": None if opt_value is None else opt_value,
                    "year": None if opt_value is None else datetime.strptime(opt_value, "%d.%m.%Y").strftime("%Y")
                }
            elif opt in [CreatorOptions.DEATH_FROM, CreatorOptions.DEATH_TO]:
                params[name] = {
                    "date": None if opt_value is None else opt_value,
                    "year": None if opt_value is None else datetime.strptime(opt_value, "%d.%m.%Y").strftime("%Y")
                }
            elif opt in [CreatorOptions.BIRTH_COUNTRY, CreatorOptions.DEATH_COUNTRY]:
                params[name] = None if opt_value is None else opt_value.value[0]
            elif opt == CreatorOptions.ADDITIONAL_FILTERS:
                params[name] = [x.value for x in opt_value]
            elif opt == CreatorOptions.GENDER:
                params[name] = opt_value.value
            else:
                params[name] = opt_value

        s = self.__get_search_creators_soup(params, page, sort)
        return self.__SEARCH_PARSER.parse_creators_search(s, page)
    # </editor-fold>

    # <editor-fold desc="TEXT SEARCH">
    def text_search(self, search: str, page: int = 1) -> TextSearchResult:
        return self.__SEARCH_PARSER.parse_text_search(self.__get_text_search_soup(search, page))
    def text_search_movies(self, search: str, page: int = 1) -> List[TextSearchedMovie]:
        return self.__SEARCH_PARSER.parse_text_search_movies(self.__get_text_search_soup(search, page))
    def text_search_creators(self, search: str, page: int = 1) -> List[TextSearchedCreator]:
        return self.__SEARCH_PARSER.parse_text_search_creators(self.__get_text_search_soup(search, page))
    def text_search_series(self, search: str, page: int = 1) -> List[TextSearchedSeries]:
        return self.__SEARCH_PARSER.parse_text_search_series(self.__get_text_search_soup(search, page))
    def text_search_users(self, search: str, page: int = 1) -> List[TextSearchedUser]:
        return self.__SEARCH_PARSER.parse_text_search_users(self.__get_text_search_soup(search, page))
    # </editor-fold>

    # <editor-fold desc="TEXT SEARCH (by AUTOCOMPLETE)">
    def text_search_tags(self, search: str) -> List[Tag]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "tag", "search": search})
        return [Tag(x) for x in json.loads(self.__get(u).content)]
    def text_search_actors(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "actors", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_directors(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "director", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_composers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "composer", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_screenwriters(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "screenwriter", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_authors(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "author", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_cinematographers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "cinematographer", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_producers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "production", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_editors(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "edit", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_sound_engineers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "sound", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_scenographers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "scenography", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_mask_designers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "mask", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def text_search_costume_designers(self, search: str) -> List[FilmCreator]:
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "costumes", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    # </editor-fold>

    # <editor-fold desc="NEWS">
    def news(self, nid: int) -> News:
        return self.__NEWS_PARSER.parse_news(self.__get_news_soup(nid), nid)
    @staticmethod
    def news_url(nid: int) -> str:
        return Globals.NEWS_URL + str(nid)
    def news_title(self, nid: int) -> Optional[str]:
        return self.__NEWS_PARSER.parse_news_title(self.__get_news_soup(nid))
    def news_text(self, nid: int) -> Optional[str]:
        return self.__NEWS_PARSER.parse_news_text(self.__get_news_soup(nid))
    def news_date(self, nid: int) -> Optional[str]:
        return self.__NEWS_PARSER.parse_news_date(self.__get_news_soup(nid))
    def news_author_id(self, nid: int) -> int:
        return self.__NEWS_PARSER.parse_news_author_id(self.__get_news_soup(nid))
    def news_author_name(self, nid: int) -> Optional[str]:
        return self.__NEWS_PARSER.parse_news_author_name(self.__get_news_soup(nid))
    def news_most_read_news(self, nid: int) -> List[dict]:
        return self.__NEWS_PARSER.parse_news_most_read_news(self.__get_news_soup(nid))
    def news_most_latest_news(self, nid: int) -> List[dict]:
        return self.__NEWS_PARSER.parse_news_most_latest_news(self.__get_news_soup(nid))
    def news_related_news(self, nid: int) -> List[dict]:
        return self.__NEWS_PARSER.parse_news_related_news(self.__get_news_soup(nid))
    def news_image(self, nid: int) -> Optional[str]:
        return self.__NEWS_PARSER.parse_news_image(self.__get_news_soup(nid))
    def news_prev_news_id(self, nid: int) -> int:
        return self.__NEWS_PARSER.parse_news_prev_news_id(self.__get_news_soup(nid))
    def news_next_news_id(self, nid: int) -> int:
        return self.__NEWS_PARSER.parse_news_next_news_id(self.__get_news_soup(nid))

    # NEWS LIST

    def news_list(self, page: int = 1) -> NewsList:
        return self.__NEWS_PARSER.parse_news_list(self.__get_news_list_soup(page), page)
    @staticmethod
    def news_list_url(page: int = 1) -> str:
        return url_prepare(Globals.NEWS_LIST_URL, {"page": page})
    def news_list_main_news(self) -> dict:
        return self.__NEWS_PARSER.parse_news_list_main_news(self.__get_news_list_soup(1))
    def news_list_news(self, page: int = 1) -> List[dict]:
        return self.__NEWS_PARSER.parse_news_list_news_list(self.__get_news_list_soup(page))
    def news_list_most_read_news(self) -> List[dict]:
        return self.__NEWS_PARSER.parse_news_list_most_read_news(self.__get_news_list_soup(1))
    def news_list_most_latest_news(self) -> List[dict]:
        return self.__NEWS_PARSER.parse_news_list_most_latest_news(self.__get_news_list_soup(1))
    def news_list_has_prev_page(self, page: int = 1) -> bool:
        return self.__NEWS_PARSER.parse_news_list_has_prev_page(self.__get_news_list_soup(page))
    def news_list_has_next_page(self, page: int = 1) -> bool:
        return self.__NEWS_PARSER.parse_news_list_has_next_page(self.__get_news_list_soup(page))
    # </editor-fold>

    # <editor-fold desc="MOVIE">
    def movie(self, mid: int) -> Movie:
        return self.__MOVIE_PARSER.parse_movie(self.__get_movie_soup(mid), mid)
    @staticmethod
    def movie_url(mid: int) -> str:
        return Globals.MOVIES_URL + str(mid)
    def movie_type(self, mid: int) -> Optional[str]:
        return self.__MOVIE_PARSER.parse_movie_type(self.__get_movie_soup(mid))
    def movie_title(self, mid: int) -> Optional[str]:
        return self.__MOVIE_PARSER.parse_movie_title(self.__get_movie_soup(mid))
    def movie_year(self, mid: int) -> int:
        return self.__MOVIE_PARSER.parse_movie_year(self.__get_movie_soup(mid))
    def movie_duration(self, mid: int) -> Optional[str]:
        return self.__MOVIE_PARSER.parse_movie_duration(self.__get_movie_soup(mid))
    def movie_genres(self, mid: int) -> List[str]:
        return self.__MOVIE_PARSER.parse_movie_genres(self.__get_movie_soup(mid))
    def movie_origins(self, mid: int) -> List[str]:
        return self.__MOVIE_PARSER.parse_movie_origins(self.__get_movie_soup(mid))
    def movie_rating(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_rating(self.__get_movie_soup(mid))
    def movie_ranks(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_ranks(self.__get_movie_soup(mid))
    def movie_other_names(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_other_names(self.__get_movie_soup(mid))
    def movie_creators(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_creators(self.__get_movie_soup(mid))
    def movie_vods(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_vods(self.__get_movie_soup(mid))
    def movie_tags(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_tags(self.__get_movie_soup(mid))
    def movie_reviews_count(self, mid: int) -> int:
        return self.__MOVIE_PARSER.parse_movie_reviews_count(self.__get_movie_soup(mid))
    def movie_reviews(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_reviews(self.__get_movie_soup(mid))
    def movie_gallery_count(self, mid: int) -> int:
        return self.__MOVIE_PARSER.parse_movie_gallery_count(self.__get_movie_soup(mid))
    def movie_gallery(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_gallery(self.__get_movie_soup(mid))
    def movie_trivia_count(self, mid: int) -> int:
        return self.__MOVIE_PARSER.parse_movie_trivia_count(self.__get_movie_soup(mid))
    def movie_trivia(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_trivia(self.__get_movie_soup(mid))
    def movie_premieres(self, mid: int) -> List[dict]:
        return self.__MOVIE_PARSER.parse_movie_premieres(self.__get_movie_soup(mid))
    def movie_plot(self, mid: int) -> dict:
        return self.__MOVIE_PARSER.parse_movie_plot(self.__get_movie_soup(mid))
    def movie_cover(self, mid: int) -> Optional[str]:
        return self.__MOVIE_PARSER.parse_movie_cover(self.__get_movie_soup(mid))
    # </editor-fold>

    # <editor-fold desc="CREATOR">
    def creator(self, cid: int, sort: CreatorFilmographySorts = CreatorFilmographySorts.BY_NEWEST) -> Creator:
        return self.__CREATOR_PARSER.parse_creator(self.__get_creator_sort_soup(cid, sort), cid)
    @staticmethod
    def creator_url(cid: int) -> str:
        return Globals.CREATORS_URL + str(cid)
    def creator_type(self, cid: int) -> Optional[str]:
        return self.__CREATOR_PARSER.parse_creator_type(self.__get_creator_soup(cid))
    def creator_name(self, cid: int) -> Optional[str]:
        return self.__CREATOR_PARSER.parse_creator_name(self.__get_creator_soup(cid))
    def creator_age(self, cid: int) -> int:
        return self.__CREATOR_PARSER.parse_creator_age(self.__get_creator_soup(cid))
    def creator_birth_date(self, cid: int) -> Optional[str]:
        return self.__CREATOR_PARSER.parse_creator_birth_date(self.__get_creator_soup(cid))
    def creator_birth_place(self, cid: int) -> Optional[str]:
        return self.__CREATOR_PARSER.parse_creator_birth_place(self.__get_creator_soup(cid))
    def creator_bio(self, cid: int) -> Optional[str]:
        return self.__CREATOR_PARSER.parse_creator_bio(self.__get_creator_soup(cid))
    def creator_trivia_count(self, cid: int) -> int:
        return self.__CREATOR_PARSER.parse_creator_trivia_count(self.__get_creator_soup(cid))
    def creator_trivia(self, cid: int) -> dict:
        return self.__CREATOR_PARSER.parse_creator_trivia(self.__get_creator_soup(cid))
    def creator_ranks(self, cid: int) -> dict:
        return self.__CREATOR_PARSER.parse_creator_ranks(self.__get_creator_soup(cid))
    def creator_gallery_count(self, cid: int) -> int:
        return self.__CREATOR_PARSER.parse_creator_gallery_count(self.__get_creator_soup(cid))
    def creator_gallery(self, cid: int) -> dict:
        return self.__CREATOR_PARSER.parse_creator_gallery(self.__get_creator_soup(cid))
    def creator_filmography(self, cid: int, sort: CreatorFilmographySorts = CreatorFilmographySorts.BY_NEWEST) -> dict:
        return self.__CREATOR_PARSER.parse_creator_filmography(self.__get_creator_sort_soup(cid, sort))
    def creator_image(self, cid: int) -> Optional[str]:
        return self.__CREATOR_PARSER.parse_creator_image(self.__get_creator_soup(cid))
    # </editor-fold>

    # <editor-fold desc="USER">
    def user(self, uid: int) -> User:
        return self.__USER_PARSER.parse_user(self.__get_user_soup(uid), uid)
    @staticmethod
    def user_url(uid: int) -> str:
        return Globals.USERS_URL + str(uid)
    def user_name(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_name(self.__get_user_soup(uid))
    def user_real_name(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_real_name(self.__get_user_soup(uid))
    def user_origin(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_origin(self.__get_user_soup(uid))
    def user_about(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_about(self.__get_user_soup(uid))
    def user_registered(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_registered(self.__get_user_soup(uid))
    def user_last_login(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_last_login(self.__get_user_soup(uid))
    def user_points(self, uid: int) -> int:
        return self.__USER_PARSER.parse_user_points(self.__get_user_soup(uid))
    def user_awards(self, uid: int) -> dict:
        return self.__USER_PARSER.parse_user_awards(self.__get_user_soup(uid))
    def user_most_watched_genres(self, uid: int) -> dict:
        return self.__USER_PARSER.parse_user_most_watched_genres(self.__get_user_soup(uid))
    def user_most_watched_types(self, uid: int) -> dict:
        return self.__USER_PARSER.parse_user_most_watched_types(self.__get_user_soup(uid))
    def user_most_watched_origins(self, uid: int) -> dict:
        return self.__USER_PARSER.parse_user_most_watched_origins(self.__get_user_soup(uid))
    def user_reviews_count(self, uid: int) -> int:
        return self.__USER_PARSER.parse_user_reviews_count(self.__get_user_soup(uid))
    def user_last_reviews(self, uid: int) -> dict:
        return self.__USER_PARSER.parse_user_reviews(self.__get_user_soup(uid))
    def user_ratings_count(self, uid: int) -> int:
        return self.__USER_PARSER.parse_user_ratings_count(self.__get_user_soup(uid))
    def user_last_ratings(self, uid: int) -> dict:
        return self.__USER_PARSER.parse_user_ratings(self.__get_user_soup(uid))
    def user_is_currently_online(self, uid: int) -> bool:
        return self.__USER_PARSER.parse_user_is_currently_online(self.__get_user_soup(uid))
    def user_image(self, uid: int) -> Optional[str]:
        return self.__USER_PARSER.parse_user_image(self.__get_user_soup(uid))
    # </editor-fold>

    # <editor-fold desc="USER OTHERS">

    def user_ratings(
        self,
        uid: int,
        mtype: Optional[MovieTypes] = None,
        origin: Optional[Origins] = None,
        genre: Optional[MovieGenres] = None,
        sort: UserRatingsSorts = UserRatingsSorts.BY_NEWLY_ADDED,
        page: int = 1
    ) -> UserRatings:
        return self.__USER_PARSER.parse_user_ratings_ratings(
            self.__get_user_ratings_soup(uid, mtype, origin, genre, sort, page)
        )
    def user_reviews(
        self,
        uid: int,
        mtype: Optional[MovieTypes] = None,
        origin: Optional[Origins] = None,
        genre: Optional[MovieGenres] = None,
        sort: UserReviewsSorts = UserReviewsSorts.BY_NEWLY_ADDED,
        page: int = 1
    ) -> UserReviews:
        return self.__USER_PARSER.parse_user_reviews_reviews(
            self.__get_user_reviews_soup(uid, mtype, origin, genre, sort, page)
        )

    # </editor-fold>

    # <editor-fold desc="USERS">
    # MOST FAVORITE USERS
    def favorite_users(self) -> FavoriteUsers:
        return self.__USERS_PARSER.parse_favorite_users(self.__get_most_favorite_users_soup())
    def favorite_users_most_favorite_users(self) -> List[FavoriteUser]:
        return self.__USERS_PARSER.parse_favorite_users_most_favorite_users(self.__get_most_favorite_users_soup())
    def favorite_users_by_regions(self) -> Dict[Origins, List[OtherFavoriteUser]]:
        return self.__USERS_PARSER.parse_favorite_users_by_regions(self.__get_most_favorite_users_soup())
    def favorite_users_by_country(self) -> Dict[Origins, List[OtherFavoriteUser]]:
        return self.__USERS_PARSER.parse_favorite_users_by_country(self.__get_most_favorite_users_soup())

    # MOST ACTIVE USERS
    def active_users(self, origin: Optional[Origins] = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME) -> ActiveUsers:
        return self.__USERS_PARSER.parse_active_users(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_reviews(self, origin: Optional[Origins] = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME) -> List[ActiveUserByReviews]:
        return self.__USERS_PARSER.parse_active_users_by_reviews(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_diaries(self, origin: Optional[Origins] = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME) -> List[ActiveUserByDiaries]:
        return self.__USERS_PARSER.parse_active_users_by_diaries(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_content(self, origin: Optional[Origins] = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME) -> List[ActiveUserByContent]:
        return self.__USERS_PARSER.parse_active_users_by_content(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_trivia(self, origin: Optional[Origins] = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME) -> List[ActiveUserByTrivia]:
        return self.__USERS_PARSER.parse_active_users_by_trivia(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_biography(self, origin: Optional[Origins] = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME) -> List[ActiveUserByBiography]:
        return self.__USERS_PARSER.parse_active_users_by_biography(self.__get_most_active_users_soup(origin, sort))
    # </editor-fold>

    # <editor-fold desc="DVDS">

    """Year is range from 1996 to the current, default is the current year"""
    def dvds_monthly_by_release_date(self, year: Optional[int] = None, page: int = 1, month: Months = Months.JANUARY) -> DVDSMonthlyByReleaseDate:
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_monthly_by_release_date(self.__get_dvds_monthly_soup(year, month, page, "release_date"))
    """Year is range from 1996 to the current, default is the current year"""
    def dvds_monthly_by_rating(self, year: Optional[int] = None, page: int = 1, month: Months = Months.JANUARY) -> DVDSMonthlyByRating:
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_monthly_by_rating(self.__get_dvds_monthly_soup(year, month, page, "rating"))
    """Year is range from 1996 to the current, default is the current year"""
    def dvds_yearly_by_release_date(self, year: Optional[int] = None) -> DVDSYearlyByReleaseDate:
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_yearly_by_release_date(self.__get_dvds_yearly_soup(year, "release_date"))
    """Year is range from 1996 to the current, default is the current year"""
    def dvds_yearly_by_rating(self, year: Optional[int] = None) -> DVDSYearlyByRating:
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_yearly_by_rating(self.__get_dvds_yearly_soup(year, "rating"))

    # </editor-fold>

    # <editor-fold desc="BLU-RAYS">

    """Year is range from 2007 to the current, default is the current year"""
    def blurays_monthly_by_release_date(self, year: Optional[int] = None, page: int = 1, month: Months = Months.JANUARY):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_blurays_monthly_by_release_date(
            self.__get_blurays_monthly_soup(year, month, page, "release_date"))
    """Year is range from 2007 to the current, default is the current year"""
    def blurays_monthly_by_rating(self, year: Optional[int] = None, page: int = 1, month: Months = Months.JANUARY):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_blurays_monthly_by_rating(
            self.__get_blurays_monthly_soup(year, month, page, "rating"))
    """Year is range from 2007 to the current, default is the current year"""
    def blurays_yearly_by_release_date(self, year: Optional[int] = None):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_blurays_yearly_by_release_date(
            self.__get_blurays_yearly_soup(year, "release_date"))
    """Year is range from 2007 to the current, default is the current year"""
    def blurays_yearly_by_rating(self, year: Optional[int] = None):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_dvds_yearly_by_rating(self.__get_blurays_yearly_soup(year, "rating"))

    # </editor-fold>

    # <editor-fold desc="Leaderboards Movies">

    def leaderboards_movies_best(self, _from: int = 1) -> List[LeaderboardMovie]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_movies(
            self.__get_leaderboards_movies_best_soup(_from))

    def leaderboards_movies_most_popular(self, _from: int = 1) -> List[LeaderboardMovie]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_movies(
            self.__get_leaderboards_movies_most_popular_soup(_from))

    def leaderboards_movies_most_controversial(self, _from: int = 1) -> List[LeaderboardMovie]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_movies(
            self.__get_leaderboards_movies_most_controversial_soup(_from))

    def leaderboards_movies_worst(self, _from: int = 1) -> List[LeaderboardMovie]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_movies(
            self.__get_leaderboards_movies_worst_soup(_from))

    # </editor-fold>

    # <editor-fold desc="Leaderboards Serials">

    def leaderboards_serials_best(self, _from: int = 1) -> List[LeaderboardSerial]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_serials(
            self.__get_leaderboards_serials_best_soup(_from))

    def leaderboards_serials_most_popular(self, _from: int = 1) -> List[LeaderboardSerial]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_serials(
            self.__get_leaderboards_serials_most_popular_soup(_from))

    def leaderboards_serials_most_controversial(self, _from: int = 1) -> List[LeaderboardSerial]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_serials(
            self.__get_leaderboards_serials_most_controversial_soup(_from))

    def leaderboards_serials_worst(self, _from: int = 1) -> List[LeaderboardSerial]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_serials(
            self.__get_leaderboards_serials_worst_soup(_from))

    # </editor-fold>

    # <editor-fold desc="Leaderboards Actors & Actresses">

    def leaderboards_actors(self, from_actors: int = 1, from_actresses: int = 1) -> LeaderboardActors:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_all_actors(
            self.__get_leaderboards_actors_and_actresses_soup(from_actors, from_actresses))

    def leaderboards_actors_actors(self, from_actors: int = 1, from_actresses: int = 1) -> List[LeaderboardPerson]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_actors(
            self.__get_leaderboards_actors_and_actresses_soup(from_actors, from_actresses))

    def leaderboards_actors_actresses(self, from_actors: int = 1, from_actresses: int = 1) -> List[LeaderboardPerson]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_actresses(
            self.__get_leaderboards_actors_and_actresses_soup(from_actors, from_actresses))

    # </editor-fold>

    # <editor-fold desc="Leaderboards Directors">

    def leaderboards_directors(self, from_directors: int = 1, from_with_best_movie: int = 1) -> LeaderboardDirectors:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_all_directors(
            self.__get_leaderboards_directors_soup(from_directors, from_with_best_movie))

    def leaderboards_directors_directors(self, from_directors: int = 1, from_with_best_movie: int = 1) -> List[LeaderboardPerson]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_directors(
            self.__get_leaderboards_directors_soup(from_directors, from_with_best_movie))

    def leaderboards_directors_with_best_movie(self, from_directors: int = 1, from_with_best_movie: int = 1) -> List[LeaderboardPersonBestMovie]:
        return self.__LEADERBOARDS_PARSER.parse_leaderboards_directors_with_best_movie(
            self.__get_leaderboards_directors_soup(from_directors, from_with_best_movie))

    # </editor-fold>