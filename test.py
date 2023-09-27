import os
import sys
import argparse
from time import sleep
from src.csfd_objects import *
from src.csfd_utils import *
from src.cli_objects import *

parser = argparse.ArgumentParser(epilog="by @TheNoiselessNoise")
parser.add_argument('--timeout', type=int, default=1, help="How many seconds to wait before running next test? (default=1)")
parser.add_argument('--tests', nargs='*', type=str, default=[], help="Specify individual tests")
parser.add_argument('--excludes', nargs='*', type=str, default=[], help="Specify individual tests to exclude")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--check', action='store_true', help="Checks existing tests")
group.add_argument('--update', action='store_true', help="Updates non-existing tests")
group.add_argument('--update-all', action='store_true', help="Updates all tests")
group.add_argument('--delete-failed', action='store_true', help="Deletes all failed results")

class CliTestDummy:
    timeout = 1
    tests = []
    excludes = []

    check = False
    update = False
    update_all = False
    delete_failed = False

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
        print(f"[i] {text} Tests: {count}")

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
            print("FAILED")
            failed_tests += 1

        if i < len(tests) - 1:
            sleep(args.timeout)

    print_results({
        "Failed": failed_tests,
        "Passed": passed_tests,
        "Skipped": skipped_tests,
        "Total": len(tests)
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
        "Updated": updated_tests,
        "Skipped": skipped_tests,
        "Total": len(args.tests) if args.tests else len(tests)
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
        "Updated": len(args.tests) if args.tests else len(tests)
    })

def delete_failed(tests: List[CsfdTest], args: CliTestDummy):
    tests = get_filtered_tests(tests, args)
    
    print("[!] Deleting Failed Results")
    
    deleted = 0
    for i, test in enumerate(tests):
        failed_test_path = get_failed_test_path(test.name)

        if not os.path.exists(failed_test_path):
            continue

        os.remove(failed_test_path)
        deleted += 1

    print_results({
        "Deleted Failed": deleted,
        "Total": len(args.tests) if args.tests else len(tests)
    })

def main(cli_args):
    tests = [
        CsfdTest("test-movie-title", "movie", {"movie": 277495, "title": True}, lambda x: x["title"]),
        CsfdTest("test-user-name", "user", {"user": 1000, "name": True}, lambda x: x["name"]),
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
            lambda x: x.movies[0].title
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
            lambda x: x.creators[0].name
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

    if cli_args.delete_failed:
        delete_failed(tests, cli_args)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit()
    main(parser.parse_args())