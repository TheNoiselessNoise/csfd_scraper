import requests
from datetime import datetime
from src.csfd_parsers import *

class CsfdScraper:
    __LAST_SOUP = None
    __MOVIE_PARSER = MovieParser()
    __CREATOR_PARSER = CreatorParser()
    __SEARCH_PARSER = SearchParser()
    __USER_PARSER = UserParser()
    __NEWS_PARSER = NewsParser()
    __USERS_PARSER = UsersParser()
    __DVDS_PARSER = DvdsParser()
    __BLURAYS_PARSER = BluraysParser()

    def __reset(self):
        self.__LAST_SOUP = None
        self.__MOVIE_PARSER.reset()
        self.__CREATOR_PARSER.reset()

    @staticmethod
    def __request(func, u, params=None):
        print("Requesting: " + u)
        response = func(u, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            raise CsfdScraperInvalidRequest("Invalid request at url: " + u)
        return response
    def __get(self, *args):
        self.__reset()
        return self.__request(requests.get, *args)
    def __post(self, *args):
        self.__reset()
        return self.__request(requests.post, *args)

    # <editor-fold desc="SOUPS">
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
    def __get_news_soup(self, nid):
        return self.__get_soup() or self.__get_soup(self.__get(Globals.NEWS_URL + str(nid)).content)
    def __get_news_list_soup(self, page):
        u = url_prepare(Globals.NEWS_LIST_URL, {"page": page})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_most_favorite_users_soup(self):
        return self.__get_soup() or self.__get_soup(self.__get(Globals.MOST_FAVORITE_USERS_URL).content)
    def __get_most_active_users_soup(self, origin, sort):
        if origin is None:
            u = url_prepare(Globals.ALL_MOST_ACTIVE_USERS_URL, {"sort": sort.value})
        else:
            u = url_prepare(Globals.MOST_ACTIVE_USERS_URL, {"sort": sort.value, "origin": origin.value[0]})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_text_search_soup(self, search, page):
        u = url_prepare(Globals.TEXT_SEARCH_URL, {"search": search, "page": page})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_creator_sort_soup(self, cid, sort):
        u = url_prepare(Globals.CREATORS_SORT_URL, {"cid": cid, "sort": sort.value})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_search_movies_soup(self, params, page, sort):
        params = encode_params(params)
        u = url_prepare(Globals.SEARCH_MOVIES_URL, {"page": page, "sort": sort.value, "params": params})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_search_creators_soup(self, params, page, sort):
        params = encode_params(params)
        u = url_prepare(Globals.SEARCH_CREATORS_URL, {"page": page, "sort": sort.value, "params": params})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_dvds_monthly_soup(self, year, month, page, sort):
        u = url_prepare(Globals.DVDS_MONTHLY_URL, {"year": year, "month": month.value[0], "sort": sort, "page": page})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_dvds_yearly_soup(self, year, sort):
        u = url_prepare(Globals.DVDS_YEARLY_URL, {"year": year, "sort": sort})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_blurays_monthly_soup(self, year, month, page, sort):
        u = url_prepare(Globals.BLURAYS_MONTHLY_URL, {"year": year, "month": month.value[0], "sort": sort, "page": page})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_blurays_yearly_soup(self, year, sort):
        u = url_prepare(Globals.BLURAYS_YEARLY_URL, {"year": year, "sort": sort})
        return self.__get_soup() or self.__get_soup(self.__get(u).content)
    def __get_user_ratings_soup(self, uid, mtype, origin, genre, sort, page):
        u = url_prepare(Globals.USER_RATINGS_URL, {"uid": uid})
        u = url_params(u, {
            "type": None if mtype is None else mtype.value,
            "origin": None if origin is None else origin.value[0],
            "genre": None if genre is None else genre.value[0],
            "sort": sort.value,
            "page": page
        })
        return self.__get_soup() or self.__get_soup(self.__get(u).content)

    # </editor-fold>

    # <editor-fold desc="SEARCH">
    def search_movies(self, options, page=1, sort=MovieSorts.BY_RATING_COUNT):
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
    def search_creators(self, options, page=1, sort=CreatorSorts.BY_FAN_COUNT):
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
    # </editor-fold>

    # <editor-fold desc="AUTOCOMPLETE SEARCH">
    def search_tags(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "tag", "search": search})
        return [Tag(x) for x in json.loads(self.__get(u).content)]
    def search_actors(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "actors", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_directors(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "director", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_composers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "composer", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_screenwriters(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "screenwriter", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_authors(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "author", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_cinematographers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "cinematographer", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_producers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "production", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_editors(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "edit", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_sound_engineers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "sound", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_scenographers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "scenography", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_mask_designers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "mask", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    def search_costume_designers(self, search):
        u = url_prepare(Globals.SEARCH_AUTOCOMPLETE_URL, {"type": "costumes", "search": search})
        return [FilmCreator(x) for x in json.loads(self.__get(u).content)]
    # </editor-fold>

    # <editor-fold desc="NEWS">
    def news(self, nid):
        return self.__NEWS_PARSER.parse_news(self.__get_news_soup(nid), nid)
    @staticmethod
    def news_url(nid):
        return Globals.NEWS_URL + str(nid)
    def news_title(self, nid):
        return self.__NEWS_PARSER.parse_news_title(self.__get_news_soup(nid))
    def news_text(self, nid):
        return self.__NEWS_PARSER.parse_news_text(self.__get_news_soup(nid))
    def news_date(self, nid):
        return self.__NEWS_PARSER.parse_news_date(self.__get_news_soup(nid))
    def news_author_id(self, nid):
        return self.__NEWS_PARSER.parse_news_author_id(self.__get_news_soup(nid))
    def news_author_name(self, nid):
        return self.__NEWS_PARSER.parse_news_author_name(self.__get_news_soup(nid))
    def news_most_read_news(self, nid):
        return self.__NEWS_PARSER.parse_news_most_read_news(self.__get_news_soup(nid))
    def news_most_latest_news(self, nid):
        return self.__NEWS_PARSER.parse_news_most_latest_news(self.__get_news_soup(nid))
    def news_related_news(self, nid):
        return self.__NEWS_PARSER.parse_news_related_news(self.__get_news_soup(nid))
    def news_image(self, nid):
        return self.__NEWS_PARSER.parse_news_image(self.__get_news_soup(nid))
    def news_prev_news_id(self, nid):
        return self.__NEWS_PARSER.parse_news_prev_news_id(self.__get_news_soup(nid))
    def news_next_news_id(self, nid):
        return self.__NEWS_PARSER.parse_news_next_news_id(self.__get_news_soup(nid))

    # NEWS LIST

    def news_list(self, page=1):
        return self.__NEWS_PARSER.parse_news_list(self.__get_news_list_soup(page), page)
    @staticmethod
    def news_list_url(page=1):
        return url_prepare(Globals.NEWS_LIST_URL, {"page": page})
    def news_list_main_news(self):
        return self.__NEWS_PARSER.parse_news_list_main_news(self.__get_news_list_soup(1))
    def news_list_news(self, page=1):
        return self.__NEWS_PARSER.parse_news_list_news_list(self.__get_news_list_soup(page))
    def news_list_most_read_news(self):
        return self.__NEWS_PARSER.parse_news_list_most_read_news(self.__get_news_list_soup(1))
    def news_list_most_latest_news(self):
        return self.__NEWS_PARSER.parse_news_list_most_latest_news(self.__get_news_list_soup(1))
    def news_list_has_prev_page(self, page=1):
        return self.__NEWS_PARSER.parse_news_list_has_prev_page(self.__get_news_list_soup(page))
    def news_list_has_next_page(self, page=1):
        return self.__NEWS_PARSER.parse_news_list_has_next_page(self.__get_news_list_soup(page))
    # </editor-fold>

    # <editor-fold desc="MOVIE">
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
    # </editor-fold>

    # <editor-fold desc="CREATOR">
    def creator(self, cid, sort: CreatorFilmographySorts = CreatorFilmographySorts.BY_NEWEST) -> Creator:
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
    def creator_filmography(self, cid, sort: CreatorFilmographySorts = CreatorFilmographySorts.BY_NEWEST):
        return self.__CREATOR_PARSER.parse_creator_filmography(self.__get_creator_sort_soup(cid, sort))
    def creator_image(self, cid):
        return self.__CREATOR_PARSER.parse_creator_image(self.__get_creator_soup(cid))
    # </editor-fold>

    # <editor-fold desc="USER">
    def user(self, uid) -> User:
        return self.__USER_PARSER.parse_user(self.__get_user_soup(uid), uid)
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
    def user_last_reviews(self, uid):
        return self.__USER_PARSER.parse_user_reviews(self.__get_user_soup(uid))
    def user_ratings_count(self, uid):
        return self.__USER_PARSER.parse_user_ratings_count(self.__get_user_soup(uid))
    def user_last_ratings(self, uid):
        return self.__USER_PARSER.parse_user_ratings(self.__get_user_soup(uid))
    def user_is_currently_online(self, uid):
        return self.__USER_PARSER.parse_user_is_currently_online(self.__get_user_soup(uid))
    def user_image(self, uid):
        return self.__USER_PARSER.parse_user_image(self.__get_user_soup(uid))
    # </editor-fold>

    # <editor-fold desc="USER OTHERS">

    def user_ratings(self,
                     uid,
                     mtype: MovieTypes = None,
                     origin: Origins = None,
                     genre: MovieGenres = None,
                     sort: UserRatingsSorts = UserRatingsSorts.BY_NEWLY_ADDED,
                     page=1):
        return self.__USER_PARSER.parse_user_ratings_ratings(
            self.__get_user_ratings_soup(uid, mtype, origin, genre, sort, page)
        )

    # </editor-fold>

    # <editor-fold desc="USERS">
    # MOST FAVORITE USERS
    def favorite_users(self):
        return self.__USERS_PARSER.parse_favorite_users(self.__get_most_favorite_users_soup())
    def favorite_users_most_favorite_users(self):
        return self.__USERS_PARSER.parse_favorite_users_most_favorite_users(self.__get_most_favorite_users_soup())
    def favorite_users_by_regions(self):
        return self.__USERS_PARSER.parse_favorite_users_by_regions(self.__get_most_favorite_users_soup())
    def favorite_users_by_country(self):
        return self.__USERS_PARSER.parse_favorite_users_by_country(self.__get_most_favorite_users_soup())

    # MOST ACTIVE USERS
    def active_users(self, origin: Origins = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME):
        return self.__USERS_PARSER.parse_active_users(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_reviews(self, origin: Origins = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME):
        return self.__USERS_PARSER.parse_active_users_by_reviews(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_diaries(self, origin: Origins = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME):
        return self.__USERS_PARSER.parse_active_users_by_diaries(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_content(self, origin: Origins = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME):
        return self.__USERS_PARSER.parse_active_users_by_content(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_trivia(self, origin: Origins = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME):
        return self.__USERS_PARSER.parse_active_users_by_trivia(self.__get_most_active_users_soup(origin, sort))
    def active_users_by_biography(self, origin: Origins = None, sort: ActiveUsersSorts = ActiveUsersSorts.ALL_TIME):
        return self.__USERS_PARSER.parse_active_users_by_biography(self.__get_most_active_users_soup(origin, sort))
    # </editor-fold>

    # <editor-fold desc="DVDS">

    """Year is range from 1996 to the current, default is the current year"""
    def dvds_monthly_by_release_date(self, year=None, page=1, month: Months = Months.JANUARY):
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_monthly_by_release_date(self.__get_dvds_monthly_soup(year, month, page, "release_date"))
    """Year is range from 1996 to the current, default is the current year"""
    def dvds_monthly_by_rating(self, year=None, page=1, month: Months = Months.JANUARY):
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_monthly_by_rating(self.__get_dvds_monthly_soup(year, month, page, "rating"))
    """Year is range from 1996 to the current, default is the current year"""
    def dvds_yearly_by_release_date(self, year=None):
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_yearly_by_release_date(self.__get_dvds_yearly_soup(year, "release_date"))
    """Year is range from 1996 to the current, default is the current year"""
    def dvds_yearly_by_rating(self, year=None):
        if year is None:
            year = datetime.now().year
        return self.__DVDS_PARSER.parse_dvds_yearly_by_rating(self.__get_dvds_yearly_soup(year, "rating"))

    # </editor-fold>

    # <editor-fold desc="BLU-RAYS">

    """Year is range from 2007 to the current, default is the current year"""
    def blurays_monthly_by_release_date(self, year=None, page=1, month: Months = Months.JANUARY):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_blurays_monthly_by_release_date(
            self.__get_blurays_monthly_soup(year, month, page, "release_date"))
    """Year is range from 2007 to the current, default is the current year"""
    def blurays_monthly_by_rating(self, year=None, page=1, month: Months = Months.JANUARY):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_blurays_monthly_by_rating(
            self.__get_blurays_monthly_soup(year, month, page, "rating"))
    """Year is range from 2007 to the current, default is the current year"""
    def blurays_yearly_by_release_date(self, year=None):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_blurays_yearly_by_release_date(
            self.__get_blurays_yearly_soup(year, "release_date"))
    """Year is range from 2007 to the current, default is the current year"""
    def blurays_yearly_by_rating(self, year=None):
        if year is None:
            year = datetime.now().year
        return self.__BLURAYS_PARSER.parse_dvds_yearly_by_rating(self.__get_blurays_yearly_soup(year, "rating"))

    # </editor-fold>
