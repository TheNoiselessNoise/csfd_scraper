# CSFD.cz Scraper

This is a simple scraper for [CSFD.cz](https://www.csfd.cz/), a Czech movie database.

#### This scraper is not meant to be used for any illegal purposes.
#### I am *NOT* responsible for any misuse of this scraper.

## Usage
Here is just sample usage of the scraper.\
If you want to know what else you can do with it,\
check out the [LIST OF METHODS](USAGE.md)

Even though the scraper is OOP, every resulted object is printable.\
Every printed object is converted to **JSON** string.

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

### News list
```python
news_list = scraper.news_list()
news_list_2 = scraper.news_list(page=2)
```

### Get News by ID
```python
news = scraper.news(8360)
```

### Most favorite users
```python
users = scraper.favorite_users()
in_great_britain = users.by_country[Origins.GREAT_BRITAIN]
```

### Most active users
```python
users = scraper.active_users()
users = scraper.active_users(sort=ActiveUsersSorts.LAST_MONTH)
users = scraper.active_users(sort=ActiveUsersSorts.LAST_MONTH, origin=Origins.USA)
users = scraper.active_users(origin=Origins.USA)
```

### DVDs yearly
```python
result = scraper.scraper.dvds_yearly_by_release_date(2023)
in_january = result.dvds[Months.JANUARY]

result = scraper.dvds_yearly_by_rating(2023)
```

### DVDs monthly
```python
result = scraper.dvds_monthly_by_release_date(2023, 2, Months.JANUARY)
result = scraper.dvds_monthly_by_rating(2023, 2, Months.JANUARY)
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
})
```
- #### Should return [The Monster Squad](https://www.csfd.cz/film/31881-zahrobni-komando/prehled/)

### Search creators by Advanced Search
```python
result = scraper.search_creators({
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
})
```
- #### Should return [Lana Del Rey](https://www.csfd.cz/tvurce/84039-lana-del-rey/prehled/)