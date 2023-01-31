from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *

def main():
    scraper = CsfdScraper()

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
