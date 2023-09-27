import json
from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *

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
            if isinstance(args, dict):
                value = args.get(k, None)
            else:
                value = getattr(args, k, None)

            if k in self._method_args_conversions and value:
                conv = self._method_args_conversions[k]

                if type(value) is list:
                    value = [self.get_enum_value(conv, x) for x in value]
                else:
                    value = self.get_enum_value(conv, value)

            setattr(self, k, value)

    def get_enum_value(self, e, value):
        if isinstance(value, e):
            return value
        
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
    
    def print_json(self, data):
        if isinstance(data, PrintableObject):
            print(str(data))
        else:
            print(json.dumps(data, indent=4, cls=CsfdJSONEncoder, ensure_ascii=False))
    
class CsfdJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PrintableObject):
            return o.to_dict()
        if isinstance(o, AutoCompleteSearchJsonWrapper):
            return o.to_dict()
        
CSFD_CLI_MAPPING = {
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