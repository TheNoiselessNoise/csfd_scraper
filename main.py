from csfd_scraper import CsfdScraper

def main():
    scraper = CsfdScraper()
    # print(scraper.movie(264179)) # Herukules
    # print(scraper.movie(450398)) # Chata
    print(scraper.movie(478500)) # Noční mlha (only gallery)

if __name__ == "__main__":
    main()
