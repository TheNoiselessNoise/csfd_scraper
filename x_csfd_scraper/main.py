import sys
import argparse
import datetime
from .src.csfd_objects import *
from .src.csfd_utils import *
from .src.cli_objects import *

def parse_args():
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

    leaderboards_movies_froms = [(x * 100) + (not x) for x in range(0, 10)]
    leaderboards_movies_parser = subparsers.add_parser('leaderboards_movies', help='Commands for Leaderboards Movies')
    leaderboards_movies_parser.add_argument('--from', type=int, choices=leaderboards_movies_froms, help="(default=1)", default=1)
    leaderboards_movies_options = leaderboards_movies_parser.add_mutually_exclusive_group(required=True)
    leaderboards_movies_options.add_argument('--best', action='store_true')
    leaderboards_movies_options.add_argument('--most_popular', action='store_true')
    leaderboards_movies_options.add_argument('--most_controversial', action='store_true')
    leaderboards_movies_options.add_argument('--worst', action='store_true')

    leaderboards_serials_froms = [(x * 100) + (not x) for x in range(0, 10)]
    leaderboards_serials_parser = subparsers.add_parser('leaderboards_serials', help='Commands for Leaderboards Serials')
    leaderboards_serials_parser.add_argument('--from', type=int, choices=leaderboards_serials_froms, help="(default=1)", default=1)
    leaderboards_serials_options = leaderboards_serials_parser.add_mutually_exclusive_group(required=True)
    leaderboards_serials_options.add_argument('--best', action='store_true')
    leaderboards_serials_options.add_argument('--most_popular', action='store_true')
    leaderboards_serials_options.add_argument('--most_controversial', action='store_true')
    leaderboards_serials_options.add_argument('--worst', action='store_true')

    leaderboards_actors_froms = [(x * 100) + (not x) for x in range(0, 3)]
    leaderboards_actors_parser = subparsers.add_parser('leaderboards_actors', help='Commands for Leaderboards Actors')
    leaderboards_actors_parser.add_argument('--from_actors', type=int, choices=leaderboards_actors_froms, help="(default=1)", default=1)
    leaderboards_actors_parser.add_argument('--from_actresses', type=int, choices=leaderboards_actors_froms, help="(default=1)", default=1)
    leaderboards_actors_options = leaderboards_actors_parser.add_mutually_exclusive_group()
    leaderboards_actors_options.add_argument('--actors', action='store_true')
    leaderboards_actors_options.add_argument('--actresses', action='store_true')

    leaderboards_directors_froms = [(x * 100) + (not x) for x in range(0, 3)]
    leaderboards_directors_parser = subparsers.add_parser('leaderboards_directors', help='Commands for Leaderboards Actors')
    leaderboards_directors_parser.add_argument('--from_directors', type=int, choices=leaderboards_directors_froms, help="(default=1)", default=1)
    leaderboards_directors_parser.add_argument('--from_with_best_movie', type=int, choices=leaderboards_directors_froms, help="(default=1)", default=1)
    leaderboards_directors_options = leaderboards_directors_parser.add_mutually_exclusive_group()
    leaderboards_directors_options.add_argument('--directors', action='store_true')
    leaderboards_directors_options.add_argument('--with_best_movie', action='store_true')

    leaderboards_others_froms = [(x * 100) + (not x) for x in range(0, 3)]
    leaderboards_others_parser = subparsers.add_parser('leaderboards_others', help='Commands for Leaderboards Others')
    leaderboards_others_parser.add_argument('--from_screenwriters', type=int, choices=leaderboards_others_froms, help="(default=1)", default=1)
    leaderboards_others_parser.add_argument('--from_cinematographers', type=int, choices=leaderboards_others_froms, help="(default=1)", default=1)
    leaderboards_others_parser.add_argument('--from_composers', type=int, choices=leaderboards_others_froms, help="(default=1)", default=1)
    leaderboards_others_options = leaderboards_others_parser.add_mutually_exclusive_group()
    leaderboards_others_options.add_argument('--screenwriters', action='store_true')
    leaderboards_others_options.add_argument('--cinematographers', action='store_true')
    leaderboards_others_options.add_argument('--composers', action='store_true')

    leaderboards_custom_parser = subparsers.add_parser('leaderboards_custom', help='Commands for Leaderboards Custom')
    leaderboards_custom_parser.add_argument('--page', type=int, help='Page of the search (default=1)', default=1)
    leaderboards_custom_parser.add_argument('--type', choices=all_movie_types, default='MOVIE')
    leaderboards_custom_parser.add_argument('--origin', choices=all_origins)
    leaderboards_custom_parser.add_argument('--genres', nargs='*', choices=all_movie_genres, default=[])
    leaderboards_custom_parser.add_argument('--year_from', type=int, help="From 1878 to 2030")
    leaderboards_custom_parser.add_argument('--year_to', type=int, help="From 1878 to 2030")
    leaderboards_custom_parser.add_argument('--actors', type=int, nargs='*', default=[])
    leaderboards_custom_parser.add_argument('--directors', type=int, nargs='*', default=[])

    return parser, parser.parse_args()

def main():
    parser, cli_args = parse_args()

    if not any(vars(cli_args).values()):
        parser.print_help()
        sys.exit()

    cli_parser = CliParser()
    if cli_args.command in CSFD_CLI_MAPPING:
        opts = CSFD_CLI_MAPPING[cli_args.command]
        cli_parser.print_json(cli_parser.parse(opts[0](cli_args), opts[1](cli_args), opts[2]))
    
if __name__ == '__main__':
    main()