# CSFD.cz Scraper

This is a simple scraper for [CSFD.cz](https://www.csfd.cz/), a Czech movie database.

#### This scraper is not meant to be used for any illegal purposes.
#### I am *NOT* responsible for any misuse of this scraper.

## Usage

### Imports
```python
from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *

scraper = CsfdScraper()
```

### Get movie by ID
```python
movie = scraper.movie(31881)
```

### Get creator by ID
```python
creator = scraper.creator(84039)
```

### Get user by ID
```python
user = scraper.user(447317)
```

### Search movies/creators/series/users by text
```python
result = scraper.text_search("spielberg")
```

### Search movies by text
```python
result = scraper.text_search_movies("spielberg")
```

### Search creators by text
```python
result = scraper.text_search_creators("spielberg")
```

### Search series by text
```python
result = scraper.text_search_series("spielberg")
```

### Search users by text
```python
result = scraper.text_search_users("spielberg")
```

### Search movies by Advanced Search
```python
result = scraper.search_movies({
    MovieSearchParameters.TYPES: [MovieSearchTypes.MOVIE],
    MovieSearchParameters.ORIGINS: {
        MovieSearchOriginOptions.FILTER: MovieSearchOriginFilters.AT_LEAST_ALL_SELECTED,
        MovieSearchOriginOptions.ORIGINS: [SearchOrigins.USA],
    },
    MovieSearchParameters.GENRES: {
        MovieSearchGenreOptions.FILTER: MovieSearchGenreFilters.AT_LEAST_ALL_SELECTED,
        MovieSearchGenreOptions.GENRES: [
            MovieSearchGenres.ACTION,
            MovieSearchGenres.ADVENTURE,
            MovieSearchGenres.FANTASY,
            MovieSearchGenres.HORROR,
            MovieSearchGenres.COMEDY,
        ],
        MovieSearchGenreOptions.EXCLUDE: [MovieSearchGenres.DRAMA, MovieSearchGenres.EROTIC]
    }
})
```
- #### Should return [The Monster Squad](https://www.csfd.cz/film/31881-zahrobni-komando/prehled/)

### Search creators by Advanced Search
```python
result = scraper.search_creators({
    CreatorSearchParameters.TYPES: [
        CreatorSearchTypes.COMPOSER,
        CreatorSearchTypes.DIRECTOR,
        CreatorSearchTypes.CINEMATOGRAPHER
    ],
    CreatorSearchParameters.BIRTH_COUNTRY: SearchOrigins.USA,
    CreatorSearchParameters.ADDITIONAL_FILTERS: [
        CreatorSearchAdditionalFilters.WITH_BIOGRAPHY,
        CreatorSearchAdditionalFilters.WITH_AWARDS,
        CreatorSearchAdditionalFilters.WITH_TRIVIA
    ],
    CreatorSearchParameters.GENDER: CreatorSearchGenders.FEMALE
})
```
- #### Should return [Lana Del Rey](https://www.csfd.cz/tvurce/84039-lana-del-rey/prehled/)