from csfd_scraper import CsfdScraper

def main():
    scraper = CsfdScraper()
    print(scraper.movie(264179))

if __name__ == "__main__":
    main()
