import os
import sys
import traceback
from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *
from src.csfd_utils import flatten
from time import sleep

def extract_user_info(user: User):
    return {
        "name": user.name,
        "real_name": user.real_name,
        "about": user.about,
        "registered": user.registered,
        "last_login": user.last_login
    }

def extract_movie_info(movie: Movie):
    return {
        "title": movie.title,
        "type": movie.type
    }

def bulk_test(f, x, a, n=5):
    y = []
    for i in range(n):
        try:
            y.append(x(f(*a())))
        except CsfdScraperInvalidRequest:
            continue
    print(tojson(y))

scraper = CsfdScraper()
tests = {
    "User": [
        scraper.user,
        [447317],
        lambda x: f"User's name: {x.name}"
    ],
    "Movie": [
        scraper.movie,
        [135983],
        lambda x: f"Movie's title: {x.title}"
    ],
    "User reviews": [
        scraper.user_reviews,
        [447317, MovieTypes.MOVIE, None, MovieGenres.EROTIC],
        lambda x: f"User reviews total: {x.total}"
    ],
    "User ratings": [
        scraper.user_ratings,
        [447317, MovieTypes.MOVIE, Origins.USA],
        lambda x: f"User ratings total: {x.total}"
    ],
    "Blurays monthly by release date": [
        scraper.blurays_monthly_by_release_date,
        [2022, 1, Months.OCTOBER],
        lambda x: f"Blurays monthly by release date total: {len(flatten([*x.blurays.values()]))}"
    ],
    "Blurays yearly by release date": [
        scraper.blurays_yearly_by_release_date,
        [2023],
        lambda x: f"Blurays yearly by release date total: {len(flatten([*x.blurays.values()]))}"
    ],
    "Dvds yearly by release date": [
        scraper.dvds_yearly_by_release_date,
        [2023],
        lambda x: f"Dvds yearly by release date total: {len(flatten([*x.dvds.values()]))}"
    ],
    "Dvds monthly by release date": [
        scraper.dvds_monthly_by_release_date,
        [2014, 2, Months.JANUARY],
        lambda x: f"Dvds monthly by release date total: {len(flatten([*x.dvds.values()]))}"
    ],
    "Dvds yearly by rating": [
        scraper.dvds_yearly_by_rating,
        [1997],
        lambda x: f"Dvds yearly by rating total: {len(x.dvds)}"
    ],
    "Dvds monthly by rating": [
        scraper.dvds_monthly_by_rating,
        [1997, 1, Months.OCTOBER],
        lambda x: f"Dvds monthly by rating total: {len(x.dvds)}"
    ],
    "Favorite users": [
        scraper.favorite_users,
        [],
        lambda x: f"Favorite users total: {len(x.most_favorite_users)}"
    ],
    "Active users": [
        scraper.active_users,
        [],
        lambda x: f"Active users total by reviews: {len(x.by_reviews)}"
    ],
    "Active users by country": [
        scraper.active_users,
        [Origins.USA, ActiveUsersSorts.LAST_MONTH],
        lambda x: f"Active users total by country by reviews: {len(x.by_reviews)}"
    ],
    "Text search": [
        scraper.text_search,
        ["spielberg"],
        lambda x: f"Text search m: {len(x.movies)} c: {len(x.creators)} s: {len(x.series)} u: {len(x.users)}"
    ],
    "Text search movies": [
        scraper.text_search_movies,
        ["spielberg"],
        lambda x: f"Text search movies total: {len(x)}"
    ],
    "Text search creators": [
        scraper.text_search_creators,
        ["spielberg"],
        lambda x: f"Text search creators total: {len(x)}"
    ],
    "Text search series": [
        scraper.text_search_series,
        ["spielberg"],
        lambda x: f"Text search series total: {len(x)}"
    ],
    "Text search users": [
        scraper.text_search_users,
        ["spielberg"],
        lambda x: f"Text search users total: {len(x)}"
    ],
    "Search creators": [
        scraper.search_creators,
        [{
            CreatorParams.TYPES: [
                CreatorTypes.COMPOSER,
                CreatorTypes.DIRECTOR,
                CreatorTypes.CINEMATOGRAPHER
            ],
            CreatorParams.BIRTH_COUNTRY: Origins.USA,
            CreatorParams.ADDITIONAL_FILTERS: [
                CreatorFilters.WITH_BIOGRAPHY,
                CreatorFilters.WITH_AWARDS,
                CreatorFilters.WITH_TRIVIA
            ],
            CreatorParams.GENDER: CreatorGenders.FEMALE
        }],
        lambda x: f"Search creators total: {len(x.creators)}\n"
                  f"First creator: " + (x.creators[0].name if len(x.creators) > 0 else "None")
    ],
    "Search movies": [
        scraper.search_movies,
        [{
            MovieParams.TYPES: [MovieTypes.MOVIE],
            MovieParams.ORIGINS: {
                MovieOriginOptions.FILTER: MovieOriginFilters.AT_LEAST_ALL_SELECTED,
                MovieOriginOptions.ORIGINS: [Origins.USA],
            },
            MovieParams.GENRES: {
                MovieGenreOptions.FILTER: MovieGenreFilters.AT_LEAST_ALL_SELECTED,
                MovieGenreOptions.GENRES: [
                    MovieGenres.ACTION,
                    MovieGenres.ADVENTURE,
                    MovieGenres.FANTASY,
                    MovieGenres.HORROR,
                    MovieGenres.COMEDY,
                ],
                MovieGenreOptions.EXCLUDE: [MovieGenres.DRAMA, MovieGenres.EROTIC]
            }
        }],
        lambda x: f"Search movies total: {len(x.movies)}\n"
                  f"First movie: " + (x.movies[0].name if len(x.movies) > 0 else "None")
    ],
}

def main():
    global scraper, tests

    for test_name, test_options in tests.items():
        func = test_options[0]
        args = test_options[1]
        result_func = test_options[2]
        print(f"{test_name} | {result_func(func(*args))}")
        input()
        # sleep(3)

    # TODO: add color rating to everywhere it is missing

    # bulk testing
    # bulk_test(scraper.user, extract_user_info, lambda: (randint(100000, 500000),))
    # bulk_test(scraper.movie, extract_movie_info, lambda: (randint(100000, 500000),))
    # bulk_test(scraper.text_search_movies, extract_movie_info, lambda: ("spielberg",))

    # print(scraper.movie(135983))
    # print(scraper.user(447317))

    # --- USER REVIEWS

    # result = scraper.user_reviews(447317, mtype=MovieTypes.MOVIE, genre=MovieGenres.EROTIC)
    # print(result)

    # --- USER RATINGS

    # result = scraper.user_ratings(447317, mtype=MovieTypes.MOVIE, origin=Origins.USA)
    # print(result)

    # --- BLURAYS

    # result = scraper.blurays_monthly_by_release_date(2022, 1, Months.OCTOBER)
    # result = scraper.blurays_yearly_by_release_date(2023)
    # print(result)

    # --- DVDS

    # result = scraper.dvds_yearly_by_release_date(2023)
    # print(result.dvds[Months.JANUARY])

    # result = scraper.dvds_monthly_by_release_date(2014, 2, Months.JANUARY)
    # print(result)

    # result = scraper.dvds_yearly_by_rating(1997)
    # result = scraper.dvds_monthly_by_release_date(1997, 1, Months.OCTOBER)
    # result = scraper.dvds_monthly_by_rating(1997, 1, Months.OCTOBER)
    # print(result)

    # --- USERS
    # users = scraper.favorite_users()
    # print(users.by_country[Origins.GREAT_BRITAIN])

    # users = scraper.active_users()
    # users = scraper.active_users(sort=ActiveUsersSorts.LAST_MONTH)
    # users = scraper.active_users(origin=Origins.USA, sort=ActiveUsersSorts.LAST_MONTH)
    # print(users)

    # --- SEARCH BY TEXT

    # result = scraper.text_search("spielberg")
    # print(result.movies[0])
    #
    # movies = scraper.text_search_movies("spielberg")
    # print(movies[0])
    #
    # creators = scraper.text_search_creators("spielberg")
    # print(creators[0])
    #
    # series = scraper.text_search_series("spielberg")
    # print(series[0])
    #
    # users = scraper.text_search_users("spielberg")
    # print(users[0])

    # --- SEARCH CREATORS

    # result = scraper.search_creators({
    #     CreatorParams.TYPES: [
    #         CreatorTypes.COMPOSER,
    #         CreatorTypes.DIRECTOR,
    #         CreatorTypes.CINEMATOGRAPHER
    #     ],
    #     CreatorParams.BIRTH_COUNTRY: Origins.USA,
    #     CreatorParams.ADDITIONAL_FILTERS: [
    #         CreatorFilters.WITH_BIOGRAPHY,
    #         CreatorFilters.WITH_AWARDS,
    #         CreatorFilters.WITH_TRIVIA
    #     ],
    #     CreatorParams.GENDER: CreatorGenders.FEMALE
    # })
    #
    # if len(result.creators):
    #     creator = result.creators[0]
    #     print(creator.name)
    #     print(creator.get_types())
    #     print(creator)

    # --- SEARCH MOVIES

    # result = scraper.search_movies({
    #     MovieParams.TYPES: [MovieTypes.MOVIE],
    #     MovieParams.ORIGINS: {
    #         MovieOriginOptions.FILTER: MovieOriginFilters.AT_LEAST_ALL_SELECTED,
    #         MovieOriginOptions.ORIGINS: [Origins.USA],
    #     },
    #     MovieParams.GENRES: {
    #         MovieGenreOptions.FILTER: MovieGenreFilters.AT_LEAST_ALL_SELECTED,
    #         MovieGenreOptions.GENRES: [
    #             MovieGenres.ACTION,
    #             MovieGenres.ADVENTURE,
    #             MovieGenres.FANTASY,
    #             MovieGenres.HORROR,
    #             MovieGenres.COMEDY,
    #         ],
    #         MovieGenreOptions.EXCLUDE: [MovieGenres.DRAMA, MovieGenres.EROTIC]
    #     }
    # })
    #
    # if len(result.movies):
    #     movie = result.movies[0]
    #     print(movie.name)
    #     print(movie.get_genres())
    #     print(movie.get_origins())
    #     print(movie)

    # --- GENERIC SCRAPING

    # print(scraper.news(8360))
    # print(scraper.news_list())
    # print(scraper.user(27877))
    # print(scraper.movie(264179)) # Herukules
    # print(scraper.movie(450398)) # Chata
    # print(scraper.movie(478500)) # Noční mlha (only gallery)
    # print(scraper.creator(87470, sort=CreatorFilmographySort.BEST))
    # print(scraper.creator(292815, sort=CreatorFilmographySort.BEST))

if __name__ == "__main__":
    main()
