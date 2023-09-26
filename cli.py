import sys
import json
import argparse
import datetime
from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *
from src.csfd_utils import *

parser = argparse.ArgumentParser(epilog="by @TheNoiselessNoise")

subparsers = parser.add_subparsers(title='Commands', dest='command')

all_origins = [x.name for x in Origins]

# NOTE: Search Movies - not fully implemented

all_movie_types = [x.name for x in MovieTypes]
all_movie_sorts = [x.value for x in MovieSorts]
all_movie_origin_filters = [x.name for x in MovieOriginFilters]
all_movie_genres = [x.name for x in MovieGenres]
all_movie_genre_filters = [x.name for x in MovieGenreFilters]

search_movies_parser = subparsers.add_parser('search_movies', help='Commands for Search Movies')
search_movies_parser.add_argument('--page', type=int, help='Page of the search (default=1)', default=1)
search_movies_parser.add_argument('--sort', choices=all_movie_sorts, help="(default=rating_count)", default='rating_count')
search_movies_parser.add_argument('--types', nargs='*', choices=all_movie_types, default=['MOVIE'])
search_movies_parser.add_argument('--origins', nargs='*', choices=all_origins, required=True)
search_movies_parser.add_argument('--origins_filter', choices=all_movie_origin_filters, required=True)
search_movies_parser.add_argument('--genres', nargs='*', choices=all_movie_genres, required=True)
search_movies_parser.add_argument('--genres_filter', choices=all_movie_genre_filters, required=True)
search_movies_parser.add_argument('--genres_exclude', nargs='*', choices=all_movie_genres, default=[])

# NOTE: Search Creators - not fully implemented

all_creator_sorts = [x.value for x in CreatorSorts]
all_creator_types = [x.name for x in CreatorTypes]
all_creator_additional_filters = [x.name for x in CreatorFilters]
all_creator_genders = [x.name for x in CreatorGenders]

search_creators_parser = subparsers.add_parser('search_creators', help='Commands for Search Creators')
search_creators_parser.add_argument('--page', type=int, help='Page of the search (default=1)', default=1)
search_creators_parser.add_argument('--sort', choices=all_creator_sorts, help='(default=fanclub_count)', default='fanclub_count')
search_creators_parser.add_argument('--types', nargs='*', choices=all_creator_types, default=['ACTOR'])
search_creators_parser.add_argument('--birth_country', choices=all_origins, required=True)
search_creators_parser.add_argument('--additional_filters', nargs='*', choices=all_creator_additional_filters, default=[])
search_creators_parser.add_argument('--gender', choices=all_creator_genders, required=True)

text_search_parser = subparsers.add_parser('text_search', help='Commands for Text Search')
text_search_parser.add_argument('-s', '--search', type=str, help='Search text', required=True)
text_search_parser.add_argument('-p', '--page', type=int, help='Page of the search', default=1)
text_search_options = text_search_parser.add_argument_group(title='Text Search Options')
text_search_options.add_argument('--movies', action='store_true')
text_search_options.add_argument('--creators', action='store_true')
text_search_options.add_argument('--series', action='store_true')
text_search_options.add_argument('--users', action='store_true')

text_search_auto_parser = subparsers.add_parser('text_search_auto', help='Commands for Text Search (Autocomplete API)')
text_search_auto_parser.add_argument('-s', '--search', type=str, help='Search text', required=True)
text_search_auto_options = text_search_auto_parser.add_argument_group(title='Text Search (Autocomplete API) Options')
text_search_auto_options.add_argument('--tags', action='store_true')
text_search_auto_options.add_argument('--actors', action='store_true')
text_search_auto_options.add_argument('--directors', action='store_true')
text_search_auto_options.add_argument('--composers', action='store_true')
text_search_auto_options.add_argument('--screenwriters', action='store_true')
text_search_auto_options.add_argument('--authors', action='store_true')
text_search_auto_options.add_argument('--cinematographers', action='store_true')
text_search_auto_options.add_argument('--producers', action='store_true')
text_search_auto_options.add_argument('--editors', action='store_true')
text_search_auto_options.add_argument('--sound_engineers', action='store_true')
text_search_auto_options.add_argument('--scenographers', action='store_true')
text_search_auto_options.add_argument('--mask_designers', action='store_true')
text_search_auto_options.add_argument('--costume_designers', action='store_true')

news_parser = subparsers.add_parser('news', help='Commands for News')
news_parser.add_argument('-n', '--news', type=int, help='ID of the News', required=True)
news_options = news_parser.add_argument_group(title='News Options')
news_options.add_argument('--url', action='store_true')
news_options.add_argument('--title', action='store_true')
news_options.add_argument('--text', action='store_true')
news_options.add_argument('--date', action='store_true')
news_options.add_argument('--author_id', action='store_true')
news_options.add_argument('--author_name', action='store_true')
news_options.add_argument('--most_read_news', action='store_true')
news_options.add_argument('--most_latest_news', action='store_true')
news_options.add_argument('--related_news', action='store_true')
news_options.add_argument('--image', action='store_true')
news_options.add_argument('--prev_news_id', action='store_true')
news_options.add_argument('--next_news_id', action='store_true')

news_list_parser = subparsers.add_parser('news_list', help='Commands for News List')
news_list_parser.add_argument('-p', '--page', type=int, help='Page of the News List', default=1)
news_list_options = news_list_parser.add_argument_group(title='News List Options')
news_list_options.add_argument('--url', action='store_true')
news_list_options.add_argument('--main_news', action='store_true')
news_list_options.add_argument('--news', action='store_true')
news_list_options.add_argument('--most_read_news', action='store_true')
news_list_options.add_argument('--most_latest_news', action='store_true')
news_list_options.add_argument('--has_prev_page', action='store_true')
news_list_options.add_argument('--has_next_page', action='store_true')

movie_parser = subparsers.add_parser('movie', help='Commands for Movies')
movie_parser.add_argument('-m', '--movie', type=int, help='ID of the movie', required=True)
movie_options = movie_parser.add_argument_group(title='Movie Options')
movie_options.add_argument('--url', action='store_true')
movie_options.add_argument('--type', action='store_true')
movie_options.add_argument('--title', action='store_true')
movie_options.add_argument('--year', action='store_true')
movie_options.add_argument('--duration', action='store_true')
movie_options.add_argument('--genres', action='store_true')
movie_options.add_argument('--origins', action='store_true')
movie_options.add_argument('--rating', action='store_true')
movie_options.add_argument('--ranks', action='store_true')
movie_options.add_argument('--other_names', action='store_true')
movie_options.add_argument('--creators', action='store_true')
movie_options.add_argument('--vods', action='store_true')
movie_options.add_argument('--tags', action='store_true')
movie_options.add_argument('--reviews_count', action='store_true')
movie_options.add_argument('--reviews', action='store_true')
movie_options.add_argument('--gallery_count', action='store_true')
movie_options.add_argument('--gallery', action='store_true')
movie_options.add_argument('--trivia_count', action='store_true')
movie_options.add_argument('--trivia', action='store_true')
movie_options.add_argument('--premieres', action='store_true')
movie_options.add_argument('--plot', action='store_true')
movie_options.add_argument('--cover', action='store_true')

creator_parser = subparsers.add_parser('creator', help='Commands for Creators')
creator_parser.add_argument('-c', '--creator', type=int, help='ID of a Creator', required=True)
creator_options = creator_parser.add_argument_group(title='Creator Options')
creator_options.add_argument('--url', action='store_true')
creator_options.add_argument('--type', action='store_true')
creator_options.add_argument('--name', action='store_true')
creator_options.add_argument('--age', action='store_true')
creator_options.add_argument('--birth_date', action='store_true')
creator_options.add_argument('--birth_place', action='store_true')
creator_options.add_argument('--bio', action='store_true')
creator_options.add_argument('--trivia_count', action='store_true')
creator_options.add_argument('--trivia', action='store_true')
creator_options.add_argument('--ranks', action='store_true')
creator_options.add_argument('--gallery_count', action='store_true')
creator_options.add_argument('--gallery', action='store_true')
creator_options.add_argument('--filmography', action='store_true')
creator_filmography_sorts = [x.value for x in CreatorFilmographySorts]
creator_options.add_argument('--filmography_sort', choices=creator_filmography_sorts, default="year")
creator_options.add_argument('--image', action='store_true')

user_parser = subparsers.add_parser('user', help='Commands for Users')
user_parser.add_argument('-u', '--user', type=int, help='ID of a User', required=True)
user_options = user_parser.add_argument_group(title='User Options')
user_options.add_argument('--url', action='store_true')
user_options.add_argument('--name', action='store_true')
user_options.add_argument('--real_name', action='store_true')
user_options.add_argument('--origin', action='store_true')
user_options.add_argument('--about', action='store_true')
user_options.add_argument('--registered', action='store_true')
user_options.add_argument('--last_login', action='store_true')
user_options.add_argument('--points', action='store_true')
user_options.add_argument('--awards', action='store_true')
user_options.add_argument('--most_watched_genres', action='store_true')
user_options.add_argument('--most_watched_types', action='store_true')
user_options.add_argument('--most_watched_origins', action='store_true')
user_options.add_argument('--reviews_count', action='store_true')
user_options.add_argument('--last_reviews', action='store_true')
user_options.add_argument('--ratings_count', action='store_true')
user_options.add_argument('--last_ratings', action='store_true')
user_options.add_argument('--is_currently_online', action='store_true')
user_options.add_argument('--image', action='store_true')

all_user_ratings_sorts = [x.name for x in UserRatingsSorts]
user_ratings_parser = subparsers.add_parser('user_ratings', help='Commands for User Ratings')
user_ratings_parser.add_argument('--user', type=int, help='ID of a User', required=True)
user_ratings_parser.add_argument('--movie_type', choices=all_movie_types)
user_ratings_parser.add_argument('--origin', choices=all_origins)
user_ratings_parser.add_argument('--genre', choices=all_movie_genres)
user_ratings_parser.add_argument('--sort', choices=all_user_ratings_sorts, help="(default=inserted_datetime)", default="inserted_datetime")
user_ratings_parser.add_argument('--page', type=int, default=1)

all_user_reviews_sorts = [x.name for x in UserReviewsSorts]
user_reviews_parser = subparsers.add_parser('user_reviews', help='Commands for User Reviews')
user_reviews_parser.add_argument('--user', type=int, help='ID of a User', required=True)
user_reviews_parser.add_argument('--movie_type', choices=all_movie_types)
user_reviews_parser.add_argument('--origin', choices=all_origins)
user_reviews_parser.add_argument('--genre', choices=all_movie_genres)
user_reviews_parser.add_argument('--sort', choices=all_user_reviews_sorts, help="(default=inserted_datetime)", default="inserted_datetime")
user_reviews_parser.add_argument('--page', type=int, default=1)

favorite_users_parser = subparsers.add_parser('favorite_users', help='Commands for Favorite Users')
favorite_users_options = favorite_users_parser.add_argument_group(title='Favorite Users Options')
favorite_users_options.add_argument('--most_favorite_users', action='store_true')
favorite_users_options.add_argument('--by_regions', action='store_true')
favorite_users_options.add_argument('--by_country', action='store_true')

all_active_users_sorts = [x.name for x in ActiveUsersSorts]
active_users_parser = subparsers.add_parser('active_users', help='Commands for Active Users')
active_users_parser.add_argument('--origin', choices=all_origins)
active_users_parser.add_argument('--sort', choices=all_active_users_sorts, help="(default=ALL_TIME)", default="ALL_TIME")
active_users_options = active_users_parser.add_argument_group(title='Active Users Options')
active_users_options.add_argument('--by_reviews', action='store_true')
active_users_options.add_argument('--by_diaries', action='store_true')
active_users_options.add_argument('--by_content', action='store_true')
active_users_options.add_argument('--by_trivia', action='store_true')
active_users_options.add_argument('--by_biography', action='store_true')

all_months = [x.name for x in Months]
current_year = datetime.datetime.now().year
dvds_monthly_parser = subparsers.add_parser('dvds_monthly', help='Commands for DVDs Monthly')
dvds_monthly_parser.add_argument('--year', type=int, help=f"From 1996 (default={current_year})", default=current_year)
dvds_monthly_parser.add_argument('--page', type=int, help="(default=1)", default=1)
dvds_monthly_parser.add_argument('--month', choices=all_months, help="(default=JANUARY)", default="JANUARY")
dvds_monthly_options = dvds_monthly_parser.add_mutually_exclusive_group(required=True)
dvds_monthly_options.add_argument('--by_release_date', action='store_true')
dvds_monthly_options.add_argument('--by_rating', action='store_true')

dvds_yearly_parser = subparsers.add_parser('dvds_yearly', help='Commands for DVDs Yearly')
dvds_yearly_parser.add_argument('--year', type=int, help=f"From 1996 (default={current_year})", default=current_year)
dvds_yearly_options = dvds_yearly_parser.add_mutually_exclusive_group(required=True)
dvds_yearly_options.add_argument('--by_release_date', action='store_true')
dvds_yearly_options.add_argument('--by_rating', action='store_true')

blurays_monthly_parser = subparsers.add_parser('blurays_monthly', help='Commands for Blu-rays Monthly')
blurays_monthly_parser.add_argument('--year', type=int, help=f"From 2007 (default={current_year})", default=current_year)
blurays_monthly_parser.add_argument('--page', type=int, help="(default=1)", default=1)
blurays_monthly_parser.add_argument('--month', choices=all_months, help="(default=JANUARY)", default="JANUARY")
blurays_monthly_options = blurays_monthly_parser.add_mutually_exclusive_group(required=True)
blurays_monthly_options.add_argument('--by_release_date', action='store_true')
blurays_monthly_options.add_argument('--by_rating', action='store_true')

blurays_yearly_parser = subparsers.add_parser('blurays_yearly', help='Commands for Blu-rays Yearly')
blurays_yearly_parser.add_argument('--year', type=int, help=f"From 2007 (default={current_year})", default=current_year)
blurays_yearly_options = blurays_yearly_parser.add_mutually_exclusive_group(required=True)
blurays_yearly_options.add_argument('--by_release_date', action='store_true')
blurays_yearly_options.add_argument('--by_rating', action='store_true')

class CliDummy:
    __exclude = ["get_dict", "get_filtered_dict", "get_enum_value"]

    # NOTE: Cli<name>OptionsDummy instances holds the optional methods of CsfdScraper
    # For example: there is a `movie` method, and "option"al methods are `movie_title`, `movie_reviews`, ...

    # order of the arguments into a given CsfdScraper method
    # List[str] or List[prop_names]
    _order = []

    # when some properties (options) doesn't have it's own CsfdScraper methods
    # List[str] or List[prop_names]
    _exclude_optionals = []

    # when some properties (options) doesn't take any arguments in it's own CsfdScraper method
    # List[str] or List[prop_names]
    _method_no_args = []

    # when some properties (options) needs some more arguments in it's own CsfdScraper method
    # Dict[str, List[str]] or Dict[prop_name, List[prop_names]]
    _method_args_mapping = {}

    # when you need some property conversions
    # Dict[str, Type] or Dict[prop_name, class_to_convert_to]
    _method_args_conversions = {}

    def __init__(self, args) -> None:
        for k, v in self.get_dict().items():
            value = getattr(args, k, None)

            if k in self._method_args_conversions and value:
                conv = self._method_args_conversions[k]

                if type(value) is list:
                    value = [self.get_enum_value(conv, x) for x in value]
                else:
                    value = self.get_enum_value(conv, value)

            setattr(self, k, value)

    def get_enum_value(self, e, value):
        if issubclass(e, Enum):
            try:
                return e(value)
            except ValueError: # probably name
                return e[value]
        return None                

    def get_dict(self) -> dict:
        keys = [x for x in dir(self) if not x.startswith("_") and not x.endswith("_") and x not in self.__exclude]
        return {k: getattr(self, k, None) for k in keys}
    
    def get_filtered_dict(self) -> dict:
        return {k: getattr(self, k, None) for k in self.get_dict() if getattr(self, k, None) and k not in self._exclude_optionals}

class CliSearchCreatorsDummy(CliDummy):
    _order = ["options", "page", "sort"]
    _method_args_conversions = {
        "sort": CreatorSorts,
        "types": CreatorTypes,
        "birth_country": Origins,
        "additional_filters": CreatorFilters,
        "gender": CreatorGenders
    }

    def __init__(self, args) -> None:
        self.page = 1
        self.sort = 'fanclub_count'
        self.types = []
        self.birth_country = None
        self.additional_filters = []
        self.gender = None

        super().__init__(args)

        self.options = {
            CreatorParams.TYPES: self.types,
            CreatorParams.BIRTH_COUNTRY: self.birth_country,
            CreatorParams.ADDITIONAL_FILTERS: self.additional_filters,
            CreatorParams.GENDER: self.gender
        }

class CliSearchMoviesDummy(CliDummy):
    _order = ["options", "page", "sort"]
    _method_args_conversions = {
        "sort": MovieSorts,
        "types": MovieTypes,
        "origins": Origins,
        "origins_filter": MovieOriginFilters,
        "genres": MovieGenres,
        "genres_filter": MovieGenreFilters,
        "genres_exclude": MovieGenres
    }

    def __init__(self, args) -> None:
        self.page = 1
        self.sort = 'rating_count'
        self.types = []
        self.origins = []
        self.origins_filter = None
        self.genres = []
        self.genres_filter = None
        self.genres_exclude = []

        super().__init__(args)

        self.options = {
            MovieParams.TYPES: self.types,
            MovieParams.ORIGINS: {
                MovieOriginOptions.FILTER: self.origins_filter,
                MovieOriginOptions.ORIGINS: self.origins
            },
            MovieParams.GENRES: {
                MovieGenreOptions.FILTER: self.genres_filter,
                MovieGenreOptions.GENRES: self.genres,
                MovieGenreOptions.EXCLUDE: self.genres_exclude
            }
        }

class CliTextSearchDummy(CliDummy):
    _order = ["search", "page"]

    def __init__(self, args) -> None:
        self.search = None
        self.page = None

        super().__init__(args)

class CliTextSearchOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.movies = False
        self.creators = False
        self.series = False
        self.users = False

        super().__init__(args)

class CliTextSearchAutoDummy(CliDummy):
    def __init__(self, args) -> None:
        self.search = None

        super().__init__(args)

class CliTextSearchAutoOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.tags = False
        self.actors = False
        self.directors = False
        self.composers = False
        self.screenwriters = False
        self.authors = False
        self.cinematographers = False
        self.producers = False
        self.editors = False
        self.sound_engineers = False
        self.scenographers = False
        self.mask_designers = False
        self.costume_designers = False

        super().__init__(args)

class CliNewsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.news = None

        super().__init__(args)

class CliNewsOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.url = False
        self.title = False
        self.text = False
        self.date = False
        self.author_id = False
        self.author_name = False
        self.most_read_news = False
        self.most_latest_news = False
        self.related_news = False
        self.image = False
        self.prev_news_id = False
        self.next_news_id = False

        super().__init__(args)

class CliNewsListDummy(CliDummy):
    def __init__(self, args) -> None:
        self.page = 1

        super().__init__(args)

class CliNewsListOptionsDummy(CliDummy):
    _method_no_args = ["main_news", "most_read_news", "most_latest_news"]

    def __init__(self, args) -> None:
        self.url = False
        self.main_news = False
        self.news = False
        self.most_read_news = False
        self.most_latest_news = False
        self.has_prev_page = False
        self.has_next_page = False

        super().__init__(args)

class CliMovieDummy(CliDummy):
    def __init__(self, args) -> None:
        self.movie = None

        super().__init__(args)

class CliMovieOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.url = False
        self.type = False
        self.title = False
        self.year = False
        self.duration = False
        self.genres = False
        self.origins = False
        self.rating = False
        self.ranks = False
        self.other_names = False
        self.creators = False
        self.vods = False
        self.tags = False
        self.reviews_count = False
        self.reviews = False
        self.gallery_count = False
        self.gallery = False
        self.trivia_count = False
        self.trivia = False
        self.premieres = False
        self.plot = False
        self.cover = False

        super().__init__(args)

class CliCreatorDummy(CliDummy):
    def __init__(self, args) -> None:
        self.creator = None

        super().__init__(args)

class CliCreatorOptionsDummy(CliDummy):
    _exclude_optionals = ["filmography_sort"]

    _method_args_mapping = {
        "filmography": ["filmography_sort"]
    }

    _method_args_conversions = {
        "filmography_sort": CreatorFilmographySorts
    }

    def __init__(self, args) -> None:
        self.url = False
        self.type = False
        self.name = False
        self.age = False
        self.birth_date = False
        self.birth_place = False
        self.bio = False
        self.trivia_count = False
        self.trivia = False
        self.ranks = False
        self.gallery_count = False
        self.gallery = False
        self.filmography = False
        self.filmography_sort = "year"
        self.image = False

        super().__init__(args)

class CliUserDummy(CliDummy):
    def __init__(self, args) -> None:
        self.user = None

        super().__init__(args)

class CliUserOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.url = False
        self.name = False
        self.real_name = False
        self.origin = False
        self.about = False
        self.registered = False
        self.last_login = False
        self.points = False
        self.awards = False
        self.most_watched_genres = False
        self.most_watched_types = False
        self.most_watched_origins = False
        self.reviews_count = False
        self.last_reviews = False
        self.ratings_count = False
        self.last_ratings = False
        self.is_currently_online = False
        self.image = False

        super().__init__(args)

class CliUserRatingsDummy(CliDummy):
    _order = ["user", "movie_type", "origin", "genre", "sort", "page"]
    _method_args_conversions = {
        "movie_type": MovieTypes,
        "origin": Origins,
        "genre": MovieGenres,
        "sort": UserRatingsSorts
    }

    def __init__(self, args) -> None:
        self.user = None
        self.movie_type = None
        self.origin = None
        self.genre = None
        self.sort = 'inserted_datetime'
        self.page = 1

        super().__init__(args)

class CliUserReviewsDummy(CliDummy):
    _order = ["user", "movie_type", "origin", "genre", "sort", "page"]
    _method_args_conversions = {
        "movie_type": MovieTypes,
        "origin": Origins,
        "genre": MovieGenres,
        "sort": UserReviewsSorts
    }

    def __init__(self, args) -> None:
        self.user = None
        self.movie_type = None
        self.origin = None
        self.genre = None
        self.sort = 'inserted_datetime'
        self.page = 1

        super().__init__(args)

class CliFavoriteUsersDummy(CliDummy):
    def __init__(self, args) -> None:
        super().__init__(args)

class CliFavoriteUsersOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.most_favorite_users = False
        self.by_regions = False
        self.by_country = False

        super().__init__(args)

class CliActiveUsersDummy(CliDummy):
    _order = ["origin", "sort"]
    _method_args_conversions = {
        "origin": Origins,
        "sort": ActiveUsersSorts
    }

    def __init__(self, args) -> None:
        self.origin = None
        self.sort = "ALL_TIME"

        super().__init__(args)

class CliActiveUsersOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.by_reviews = False
        self.by_diaries = False
        self.by_content = False
        self.by_trivia = False
        self.by_biography = False

        super().__init__(args)

class CliDVDsMonthlyDummy(CliDummy):
    _order = ["year", "page", "month"]
    _method_args_conversions = {
        "month": Months
    }

    def __init__(self, args) -> None:
        self.year = None
        self.page = 1
        self.month = "JANUARY"

        super().__init__(args)

class CliDVDsMonthlyOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.by_release_date = False
        self.by_rating = False

        super().__init__(args)

class CliDVDsYearlyDummy(CliDummy):
    def __init__(self, args) -> None:
        self.year = None

        super().__init__(args)

class CliDVDsYearlyOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.by_release_date = False
        self.by_rating = False

        super().__init__(args)

class CliBluraysMonthlyDummy(CliDummy):
    _order = ["year", "page", "month"]
    _method_args_conversions = {
        "month": Months
    }

    def __init__(self, args) -> None:
        self.year = None
        self.page = 1
        self.month = "JANUARY"

        super().__init__(args)

class CliBluraysMonthlyOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.by_release_date = False
        self.by_rating = False

        super().__init__(args)

class CliBluraysYearlyDummy(CliDummy):
    def __init__(self, args) -> None:
        self.year = None

        super().__init__(args)

class CliBluraysYearlyOptionsDummy(CliDummy):
    def __init__(self, args) -> None:
        self.by_release_date = False
        self.by_rating = False

        super().__init__(args)

class CliParser:
    def __init__(self):
        self.csfd_scraper = CsfdScraper()

    def run(self, main_args, option_args, prop_name, whole_func_name):
        method = getattr(self.csfd_scraper, whole_func_name, None)
        assert method is not None, f"Couldn't find a `{whole_func_name}` parser."
        
        more_args = []
        if prop_name not in option_args._method_no_args:
            main_args_d = main_args.get_dict()

            more_args = main_args_d.values()
            if main_args._order:
                more_args = [main_args_d[x] for x in main_args._order]

            if prop_name in option_args._method_args_mapping:
                for arg in option_args._method_args_mapping[prop_name]:
                    arg_value = getattr(option_args, arg, None)
                    more_args.append(arg_value)

        return method(*more_args)

    def parse(self, main_args, option_args, prefix=""):
        if not option_args.get_filtered_dict():
            return self.run(main_args, option_args, prefix, prefix)

        data = {}
        for k, v in option_args.get_dict().items():
            if v and k not in option_args._exclude_optionals:
                data[k] = self.run(main_args, option_args, k, f"{prefix}_{k}")
        return data
    
class CsfdJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PrintableObject):
            return o.to_dict()
        if isinstance(o, AutoCompleteSearchJsonWrapper):
            return o.to_dict()

def print_json(data):
    if isinstance(data, PrintableObject):
        print(str(data))
    else:
        print(json.dumps(data, indent=4, cls=CsfdJSONEncoder, ensure_ascii=False))

def main(cli_args):
    cli_mapping = {
        # command: [main_args, optional_args, prefix]
        "search_movies": [CliSearchMoviesDummy, CliDummy, "search_movies"], 
        "search_creators": [CliSearchCreatorsDummy, CliDummy, "search_creators"],
        "text_search": [CliTextSearchDummy, CliTextSearchOptionsDummy, "text_search"],
        "text_search_auto": [CliTextSearchAutoDummy, CliTextSearchAutoOptionsDummy, "text_search"],
        "news": [CliNewsDummy, CliNewsOptionsDummy, "news"],
        "news_list": [CliNewsListDummy, CliNewsListOptionsDummy, "news_list"],
        "movie": [CliMovieDummy, CliMovieOptionsDummy, "movie"],
        "creator": [CliCreatorDummy, CliCreatorOptionsDummy, "creator"],
        "user": [CliUserDummy, CliUserOptionsDummy, "user"],
        "user_ratings": [CliUserRatingsDummy, CliDummy, "user_ratings"],
        "user_reviews": [CliUserReviewsDummy, CliDummy, "user_reviews"],
        "favorite_users": [CliFavoriteUsersDummy, CliFavoriteUsersOptionsDummy, "favorite_users"],
        "active_users": [CliActiveUsersDummy, CliActiveUsersOptionsDummy, "active_users"],
        "dvds_monthly": [CliDVDsMonthlyDummy, CliDVDsMonthlyOptionsDummy, "dvds_monthly"],
        "dvds_yearly": [CliDVDsYearlyDummy, CliDVDsYearlyOptionsDummy, "dvds_yearly"],
        "blurays_monthly": [CliBluraysMonthlyDummy, CliBluraysMonthlyOptionsDummy, "blurays_monthly"],
        "blurays_yearly": [CliBluraysYearlyDummy, CliBluraysYearlyOptionsDummy, "blurays_yearly"],
    }

    cli_parser = CliParser()
    if cli_args.command in cli_mapping:
        opts = cli_mapping[cli_args.command]
        print_json(cli_parser.parse(opts[0](cli_args), opts[1](cli_args), opts[2]))
    
if __name__ == '__main__':
    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit()
    main(parser.parse_args())