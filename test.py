import os
import sys
import argparse
from time import sleep
from src.csfd_scraper import CsfdScraper
from src.csfd_objects import *
from src.csfd_utils import *
from src.cli_objects import *

parser = argparse.ArgumentParser(epilog="by @TheNoiselessNoise")
parser.add_argument('--timeout', type=int, default=1, help="How many seconds to wait before running next test?")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--check', action='store_true', help="Checks existing tests")
group.add_argument('--update', action='store_true', help="Updates non-existant tests")
group.add_argument('--update-all', action='store_true', help="Updates all tests")
group.add_argument('--delete-failed', action='store_true', help="Deletes all failed results")

class CliTestDummy:
    timeout = 1
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

def get_test_path(test_name: str):
    this_path = os.path.dirname(__file__)
    return os.path.join(this_path, "tests", test_name + ".txt")

def get_failed_test_path(test_name: str):
    this_path = os.path.dirname(__file__)
    return os.path.join(this_path, "tests", test_name + "_failed.txt")

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

def check_tests(tests: List[CsfdTest], timeout=1):
    print("[!] Checking tests")

    failed_tests = 0
    passed_tests = 0
    skipped_tests = 0
    for test in tests:
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

        sleep(timeout)

    print_results({
        "Failed": failed_tests,
        "Passed": passed_tests,
        "Skipped": skipped_tests,
        "Total": len(tests)
    })

def update_tests(tests: List[CsfdTest], timeout=1):
    print("[!] Updating Non-existing Tests")
    
    updated_tests = 0
    skipped_tests = 0
    for test in tests:
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
        sleep(timeout)

    print_results({
        "Updated": updated_tests,
        "Skipped": skipped_tests,
        "Total": len(tests)
    })

def update_all_tests(tests: List[CsfdTest], timeout: int=1):
    print("[!] Updating All Available Tests")

    for test in tests:
        print(f"Updating {test.name}...", end="")

        test_path = get_test_path(test.name)

        result = get_test_result(test)
        write_test_file_result(test_path, result)
        print("DONE")
        sleep(timeout)

    print_results({
        "Updated": len(tests)
    })

def delete_failed(tests: List[CsfdTest]):
    print("[!] Deleting Failed Results")
    
    deleted = 0
    for test in tests:
        failed_test_path = get_failed_test_path(test.name)

        if not os.path.exists(failed_test_path):
            continue

        os.remove(failed_test_path)
        deleted += 1

    print_results({
        "Deleted Failed": deleted,
        "Total": len(tests)
    })

def main(cli_args):
    tests = [
        # Avatar: The Way of Water
        CsfdTest("test-movie-title",
            "movie", {"movie": 277495, "title": True}, lambda x: x["title"]),
        CsfdTest("test-user-name",
            "user", {"user": 1000, "name": True}, lambda x: x["name"]),
        CsfdTest("test-advanced-search-movies",
            "search_movies",
            {
                "page": 1,
                "sort": "rating_count",
                "types": ["MOVIE"],
                "origins": ["USA"],
                "origins_filter": "AT_LEAST_ALL_SELECTED",
                "genres": ["ACTION", "ADVENTURE", "FANTASY", "HORROR", "COMEDY"],
                "genres_filter": "AT_LEAST_ALL_SELECTED",
                "genres_exclude": ["DRAMA", "EROTIC"]
            },
            lambda x: x.movies[0].title
        ),
        CsfdTest("test-advanced-search-creators",
            "search_creators",
            {
                "page": 1,
                "sort": "fanclub_count",
                "types": ["COMPOSER", "DIRECTOR", "CINEMATOGRAPHER"],
                "birth_country": "USA",
                "additional_filters": ["WITH_BIOGRAPHY", "WITH_AWARDS", "WITH_TRIVIA"],
                "gender": "FEMALE"
            },
            lambda x: x.creators[0].name
        )
    ]

    cli_args: CliTestDummy = cli_args

    if cli_args.check:
        check_tests(tests, cli_args.timeout)

    if cli_args.update:
        update_tests(tests, cli_args.timeout)

    if cli_args.update_all:
        update_all_tests(tests, cli_args.timeout)

    if cli_args.delete_failed:
        delete_failed(tests)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit()
    main(parser.parse_args())