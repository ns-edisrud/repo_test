"""Programmatic entrypoint to running behave from the command line"""
import os
import sys

from behave.__main__ import main as behave_main

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    exit_code = behave_main(
            "--tags=tests-replicated "
            "-D environment='https://replicated-test.n-s.internal/' "
            "tests_replicated/src/ns_tests_replicated"
        )
