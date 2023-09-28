import os
import sys
import difflib
import argparse
from time import sleep
from src.cli_objects import *

parser = argparse.ArgumentParser(epilog="by @TheNoiselessNoise")
parser.add_argument('--timeout', type=int, default=1, help="How many seconds to wait before running next test? (default=1)")
parser.add_argument('--tests', nargs='*', type=str, default=[], help="Specify individual tests (doesn't apply to --delete-* actions)")
parser.add_argument('--excludes', nargs='*', type=str, default=[], help="Specify individual tests to exclude (doesn't apply to --delete-* actions)")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--check', action='store_true', help="Checks existing tests")
group.add_argument('--update', action='store_true', help="Updates non-existing tests")
group.add_argument('--update-all', action='store_true', help="Updates all tests")
group.add_argument('--delete-files', action='store_true', help="Deletes all '<test>_failed.txt' and '<test>_diff.txt' files")
group.add_argument('--delete-removed', action='store_true', help="Deletes all files of removed tests")

class CliTestDummy:
    timeout = 1
    tests = []
    excludes = []

    check = False
    update = False
    update_all = False
    delete_files = False
    delete_removed = False

class CsfdTest:
    def __init__(self, name: str, command: str, args: dict, post_init=None):
        self.name = name
        self.command = command
        self.args = args
        self.post_init = post_init

def get_tests_path():
    this_path = os.path.dirname(__file__)
    tests_path = os.path.join(this_path, "tests")
    if not os.path.exists(tests_path):
        os.makedirs(tests_path)
    return tests_path

def get_test_path(test_name: str):
    return os.path.join(get_tests_path(), test_name + ".json")

def get_failed_test_path(test_name: str):
    return os.path.join(get_tests_path(), test_name + "_failed.txt")

def get_diff_test_path(test_name: str):
    return os.path.join(get_tests_path(), test_name + "_diff.txt")

def get_test_result(test: CsfdTest):
    cli_parser = CliParser()
    if test.command in CSFD_CLI_MAPPING:
        opts = CSFD_CLI_MAPPING[test.command]
        result = cli_parser.parse(opts[0](test.args), opts[1](test.args), opts[2])

        if test.post_init:
            try:
                result = test.post_init(result, cli_parser)
            except Exception as err:
                print(f"\nERROR: post_init function in test `{test.name}` failed, probably bug in CsfdScraper!")
                print(f"MESSAGE: {err}")
                print(f"RESULT (type={type(result).__name__}):")
                print(result)
                exit(1)

        return result
    
    print(f"ERROR: Unknown test command {test.command}")
    exit(1)

def get_test_file_result(test_path: str):
    with open(test_path, "r", encoding="utf-8") as file:
        return file.read()
    
def write_test_file_result(test_path: str, result: str):
    with open(test_path, "w", encoding="utf-8") as file:
        file.write(result)

def print_results(args: dict):
    print("[!] DONE")
    for text, count in args.items():
        print(f"[i] {text}: {count}")

def get_filtered_tests(tests: List[CsfdTest], args: CliTestDummy):
    filtered_tests = []
    for test in tests:
        if args.tests and test.name not in args.tests:
            continue
        if args.excludes and test.name in args.excludes:
            continue

        filtered_tests.append(test)
    return filtered_tests

def check_tests(tests: List[CsfdTest], args: CliTestDummy):
    tests = get_filtered_tests(tests, args)

    print("[!] Checking tests")

    failed_tests = 0
    passed_tests = 0
    skipped_tests = 0
    for i, test in enumerate(tests):
        print(f"Checking {test.name}...", end="")

        test_path = get_test_path(test.name)

        if not os.path.exists(test_path):
            skipped_tests += 1
            print("SKIPPED")
            continue

        result = get_test_result(test)
        file_result = get_test_file_result(test_path)

        if result == file_result:
            print("PASSED")
            passed_tests += 1
        else:
            failed_test_path = get_failed_test_path(test.name)
            write_test_file_result(failed_test_path, result)

            # create a diff file
            diff_test_path = get_diff_test_path(test.name)
            diff = "".join(difflib.unified_diff(
                a=        open(test_path, "r", encoding="utf-8").readlines(),
                b=        open(failed_test_path, "r", encoding="utf-8").readlines(),
                fromfile= os.path.basename(test_path),
                tofile=   os.path.basename(failed_test_path),
            ))
            write_test_file_result(diff_test_path, diff)

            print("FAILED")
            failed_tests += 1

        if i < len(tests) - 1:
            sleep(args.timeout)

    print_results({
        "Failed Tests": failed_tests,
        "Passed Tests": passed_tests,
        "Skipped Tests": skipped_tests,
        "Total Tests": len(tests)
    })

def update_tests(tests: List[CsfdTest], args: CliTestDummy):
    tests = get_filtered_tests(tests, args)

    print("[!] Updating Non-existing Tests")
    
    updated_tests = 0
    skipped_tests = 0
    for i, test in enumerate(tests):
        print(f"Updating {test.name}...", end="")

        test_path = get_test_path(test.name)

        if os.path.exists(test_path):
            skipped_tests += 1
            print("SKIPPED")
            continue

        result = get_test_result(test)

        if not isinstance(result, str):
            print(f"\nERROR: result of the test `{test.name}` is not a string, but `{type(result).__name__}`")
            print(f"INFO: maybe you should include a post_init function...")
            exit(1)

        write_test_file_result(test_path, result)
        updated_tests += 1
        print("DONE")

        if i < len(tests) - 1:
            sleep(args.timeout)

    print_results({
        "Updated Tests": updated_tests,
        "Skipped Tests": skipped_tests,
        "Total Tests": len(args.tests) if args.tests else len(tests)
    })

def update_all_tests(tests: List[CsfdTest], args: CliTestDummy):
    tests = get_filtered_tests(tests, args)

    print("[!] Updating All Available Tests")

    for i, test in enumerate(tests):
        print(f"Updating {test.name}...", end="")

        test_path = get_test_path(test.name)

        result = get_test_result(test)
        write_test_file_result(test_path, result)
        print("DONE")

        if i < len(tests) - 1:
            sleep(args.timeout)

    print_results({
        "Updated Tests": len(args.tests) if args.tests else len(tests)
    })

def delete_files(tests: List[CsfdTest]):
    print("[!] Deleting Failed and Diff Files")
    
    deleted_failed = 0
    deleted_diffs = 0
    for test in tests:
        failed_test_path = get_failed_test_path(test.name)
        diff_test_path = get_diff_test_path(test.name)

        if os.path.exists(failed_test_path):
            os.remove(failed_test_path)
            deleted_failed += 1

        if os.path.exists(diff_test_path):
            os.remove(diff_test_path)
            deleted_diffs += 1

    print_results({
        "Deleted Fail Files": deleted_failed,
        "Deleted Diff Files": deleted_diffs
    })

def delete_removed(tests: List[CsfdTest]):
    test_names = [test.name for test in tests]

    print("[!] Deleting Removed Tests (files)")
    
    deleted = 0
    deleted_failed = 0
    deleted_diffs = 0
    for file in os.listdir(get_tests_path()):
        file_path = os.path.join(get_tests_path(), file)
        
        if not os.path.isfile(file_path):
            continue

        test_name = os.path.splitext(file)[0]

        if test_name in test_names or test_name.endswith("_failed") or test_name.endswith("_diff"):
            continue

        test_path = get_test_path(test_name)
        failed_test_path = get_failed_test_path(test_name)
        diff_test_path = get_diff_test_path(test_name)

        if os.path.exists(test_path):
            os.remove(test_path)
            deleted += 1

        if os.path.exists(failed_test_path):
            os.remove(failed_test_path)
            deleted_failed += 1

        if os.path.exists(diff_test_path):
            os.remove(diff_test_path)
            deleted_diffs += 1

    print_results({
        "Deleted Result Files": deleted,
        "Deleted Fail Files": deleted_failed,
        "Deleted Diff Files": deleted_diffs
    })

def post_init_movie(movie: Movie, p: CliParser):
    # without reviews, because those are randomly chosen
    movie.args['reviews']['items'] = {}
    # without trivia, because those are randomly chosen
    movie.args['trivia']['items'] = {}
    # without gallery main image, because it's randomly chosen
    movie.args['gallery']['image'] = None

    # if anything other fails, the movie was updated with some new information

    return str(movie)

def post_init_creator(creator: Creator, p: CliParser):
    # without gallery main image, because it's randomly chosen
    creator.args['gallery']['image'] = None

    return str(creator)

def main(cli_args):
    tests = [
        # CsfdTest("<test_name>", "<command>", {<cli_args>}, ?<lambda x: x.prop>)
        CsfdTest("test-movie", "movie", {"movie": 277495}, post_init_movie),
        CsfdTest("test-creator", "creator", {"creator": 1000}, post_init_creator),
        CsfdTest("test-user", "user", {"user": 1000}, lambda user, p: str(user)),
        CsfdTest("test-news", "news", {"news": 1000}, lambda news, p: str(news)),
        
        # can't really test for news_list
        
        # can test for user_ratings, but one day it can fail
        CsfdTest("test-user-ratings",
            "user_ratings",
            {
                "page": 1,
                "sort": "inserted_datetime",
                "user": 1000,
                "origin": Origins.USA,
                "genre": MovieGenres.MYSTERY
            },
            lambda user_ratings, p: str(user_ratings)
        ),

        # can test for user_reviews, but one day it can fail
        CsfdTest("test-user-reviews",
            "user_reviews",
            {
                "page": 1,
                "sort": "inserted_datetime",
                "user": 447317,
                "origin": Origins.USA,
                "genre": MovieGenres.SPORT
            },
            lambda user_reviews, p: str(user_reviews)
        ),

        CsfdTest("test-advanced-search-movies",
            "search_movies",
            {
                "page": 1,
                "sort": "rating_count",
                "types": [MovieTypes.MOVIE],
                "origins": [Origins.USA],
                "origins_filter": MovieOriginFilters.AT_LEAST_ALL_SELECTED,
                "genres": [MovieGenres.ACTION, MovieGenres.ADVENTURE, MovieGenres.FANTASY, MovieGenres.HORROR, MovieGenres.COMEDY],
                "genres_filter": MovieGenreFilters.AT_LEAST_ALL_SELECTED,
                "genres_exclude": [MovieGenres.DRAMA, MovieGenres.EROTIC]
            },
            lambda search_movies_result, p: str(search_movies_result)
        ),
        CsfdTest("test-advanced-search-creators",
            "search_creators",
            {
                "page": 1,
                "sort": "fanclub_count",
                "types": [CreatorTypes.COMPOSER, CreatorTypes.DIRECTOR, CreatorTypes.CINEMATOGRAPHER],
                "birth_country": Origins.USA,
                "additional_filters": [CreatorFilters.WITH_BIOGRAPHY, CreatorFilters.WITH_AWARDS, CreatorFilters.WITH_TRIVIA],
                "gender": CreatorGenders.FEMALE
            },
            lambda search_creators_result, p: str(search_creators_result)
        ),

        CsfdTest("test-dvds-monthly-by-release-date",
            "dvds_monthly",
            {
                "page": 1,
                "year": 1998,
                "month": Months.JUNE,
                "by_release_date": True
            },
            lambda dvds_monthly, p: str(dvds_monthly["by_release_date"])
        ),
        CsfdTest("test-dvds-monthly-by-rating",
            "dvds_monthly",
            {
                "page": 1,
                "year": 1998,
                "month": Months.JUNE,
                "by_rating": True
            },
            lambda dvds_monthly, p: str(dvds_monthly["by_rating"])
        ),

        CsfdTest("test-dvds-yearly-by-release-date",
            "dvds_yearly",
            { "year": 1997, "by_release_date": True },
            lambda dvds_yearly, p: str(dvds_yearly["by_release_date"])
        ),
        CsfdTest("test-dvds-yearly-by-rating",
            "dvds_yearly",
            { "year": 1997, "by_rating": True },
            lambda dvds_yearly, p: str(dvds_yearly["by_rating"])
        ),

        CsfdTest("test-blurays-monthly-by-release-date",
            "blurays_monthly",
            {
                "page": 1,
                "year": 2007,
                "month": Months.JUNE,
                "by_release_date": True
            },
            lambda blurays_monthly, p: str(blurays_monthly["by_release_date"])
        ),
        CsfdTest("test-blurays-monthly-by-rating",
            "blurays_monthly",
            {
                "page": 1,
                "year": 2007,
                "month": Months.JUNE,
                "by_rating": True
            },
            lambda blurays_monthly, p: str(blurays_monthly["by_rating"])
        ),

        CsfdTest("test-blurays-yearly-by-release-date",
            "blurays_yearly",
            { "year": 2007, "by_release_date": True },
            lambda blurays_yearly, p: str(blurays_yearly["by_release_date"])
        ),
        CsfdTest("test-blurays-yearly-by-rating",
            "blurays_yearly",
            { "year": 2007, "by_rating": True },
            lambda blurays_yearly, p: str(blurays_yearly["by_rating"])
        ),

        # can test for leaderboards_movies, but one day it can fail
        CsfdTest("test-leaderboards-movies-best-1",
            "leaderboards_movies",
            { "from": 1, "best": True },
            lambda leaderboards_movies, p: p.get_json(leaderboards_movies["best"])
        ),
        CsfdTest("test-leaderboards-movies-best-900",
            "leaderboards_movies",
            { "from": 900, "best": True },
            lambda leaderboards_movies, p: p.get_json(leaderboards_movies["best"])
        ),

        # can test for leaderboards_serials, but one day it can fail
        CsfdTest("test-leaderboards-serials-best-1",
            "leaderboards_serials",
            { "from": 1, "best": True },
            lambda leaderboards_serials, p: p.get_json(leaderboards_serials["best"])
        ),
        CsfdTest("test-leaderboards-serials-best-900",
            "leaderboards_serials",
            { "from": 900, "best": True },
            lambda leaderboards_serials, p: p.get_json(leaderboards_serials["best"])
        ),
    ]

    cli_args: CliTestDummy = cli_args
    cli_args.tests = list(dict.fromkeys(cli_args.tests))

    test_names = [x.name for x in tests]

    non_existing_tests = list(filter(lambda name: name not in test_names, cli_args.tests))
    if non_existing_tests:
        print("ERROR: can't process non-existing tests:", "".join(f"\n`{x}`" for x in non_existing_tests))
        exit(1)

    non_existing_exludes_tests = list(filter(lambda name: name not in test_names, cli_args.excludes))
    if non_existing_exludes_tests:
        print("ERROR: can't exclude non-existing tests:", "".join(f"\n`{x}`" for x in non_existing_exludes_tests))
        exit(1)

    test_and_exclude = list(filter(lambda name: name in cli_args.excludes, cli_args.tests))
    if test_and_exclude:
        print("ERROR: can't process and exclude tests at the same time:", "".join(f"\n`{x}`" for x in test_and_exclude))
        exit(1)

    if cli_args.check:
        check_tests(tests, cli_args)

    if cli_args.update:
        update_tests(tests, cli_args)

    if cli_args.update_all:
        update_all_tests(tests, cli_args)

    if cli_args.delete_files:
        delete_files(tests)

    if cli_args.delete_removed:
        delete_removed(tests)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit()
    main(parser.parse_args())