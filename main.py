from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *

def main():
    scraper = CsfdScraper()

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
    #     CreatorSearchParameters.TYPES: [
    #         CreatorSearchTypes.COMPOSER,
    #         CreatorSearchTypes.DIRECTOR,
    #         CreatorSearchTypes.CINEMATOGRAPHER
    #     ],
    #     CreatorSearchParameters.BIRTH_COUNTRY: SearchOrigins.USA,
    #     CreatorSearchParameters.ADDITIONAL_FILTERS: [
    #         CreatorSearchAdditionalFilters.WITH_BIOGRAPHY,
    #         CreatorSearchAdditionalFilters.WITH_AWARDS,
    #         CreatorSearchAdditionalFilters.WITH_TRIVIA
    #     ],
    #     CreatorSearchParameters.GENDER: CreatorSearchGenders.FEMALE
    # })
    #
    # if len(result.creators):
    #     creator = result.creators[0]
    #     print(creator.name)
    #     print(creator.get_types())
    #     print(creator)

    # --- SEARCH MOVIES

    # result = scraper.search_movies({
    #     MovieSearchParameters.TYPES: [MovieSearchTypes.MOVIE],
    #     MovieSearchParameters.ORIGINS: {
    #         MovieSearchOriginOptions.FILTER: MovieSearchOriginFilters.AT_LEAST_ALL_SELECTED,
    #         MovieSearchOriginOptions.ORIGINS: [SearchOrigins.CZECHOSLOVAKIA],
    #     },
    #     MovieSearchParameters.GENRES: {
    #         MovieSearchGenreOptions.FILTER: MovieSearchGenreFilters.AT_LEAST_ALL_SELECTED,
    #         MovieSearchGenreOptions.GENRES: [MovieSearchGenres.ACTION],
    #         MovieSearchGenreOptions.EXCLUDE: [MovieSearchGenres.DRAMA, MovieSearchGenres.EROTIC]
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

    # print(scraper.user(27877))
    # print(scraper.movie(264179)) # Herukules
    # print(scraper.movie(450398)) # Chata
    # print(scraper.movie(478500)) # Noční mlha (only gallery)
    # print(scraper.creator(87470, sort=CreatorFilmographySort.BEST))
    # print(scraper.creator(292815, sort=CreatorFilmographySort.BEST))

if __name__ == "__main__":
    main()
