# CSFD.cz Scraper

This is a simple scraper for [CSFD.cz](https://www.csfd.cz/), a Czech movie database.

## Usage
Here is just sample usage of the scraper.

Even though the scraper is OOP, every resulted object is printable.\
Every printed object is converted to **JSON** string.

### Now with CLI!
```bash
# some help, you will need it
python3 cli.py --help

# to quickly get a movie
python3 cli.py movie -m 31881

# or just the title
python3 cli.py movie -m 31881 --title

# or just the title and duration?
python3 cli.py movie -m 31881 --title --duration

# need anything else for a movie?
python3 cli.py movie --help
```

### Usage in code
```python
from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *

scraper = CsfdScraper()
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