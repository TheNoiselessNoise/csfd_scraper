import os
import sys
import difflib
import argparse
from time import sleep
from src.csfd_objects import *
from src.csfd_utils import *
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
    return os.path.join(get_tests_path(), test_name + ".txt")

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
                result = test.post_init(result)
            except:
                print(f"ERROR: post_init function in test `{test.name}` failed, probably bug in CsfdScraper!")
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

def post_init_movie(movie: Movie):
    # without reviews, because those are randomly chosen
    movie.args['reviews']['items'] = {}
    # without trivia, because those are randomly chosen
    movie.args['trivia']['items'] = {}
    # without gallery main image, because it's randomly chosen
    movie.args['gallery']['image'] = None

    # if anything other fails, the movie was updated with some new information

    return str(movie)

def main(cli_args):
    tests = [
        # CsfdTest("<test_name>", "<command>", {<cli_args>}, ?<lambda x: x.prop>)
        CsfdTest("test-movie", "movie", {"movie": 277495}, post_init_movie),
        CsfdTest("test-user", "user", {"user": 1000}, lambda user: str(user)),
        CsfdTest("test-news", "news", {"news": 1000}, lambda news: str(news)),
        # can't really test for news_list
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
            lambda search_movies_result: str(search_movies_result)
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
            lambda search_creators_result: str(search_creators_result)
        )
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