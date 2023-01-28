from csfd_scraper import CsfdScraper
from objects import CreatorFilmographySort

def main():
    scraper = CsfdScraper()

    # print(scraper.movie(264179)) # Herukules
    # print(scraper.movie(450398)) # Chata
    # print(scraper.movie(478500)) # Noční mlha (only gallery)
    # print(scraper.creator(87470, sort=CreatorFilmographySort.BEST))
    print(scraper.creator(292815, sort=CreatorFilmographySort.BEST))

if __name__ == "__main__":
    main()
