"""Programmatic entrypoint to running behave from the command line"""
import os
import sys

from behave.__main__ import main as behave_main

if __name__ == "__main__":
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    # Hack for localdev to enable the root logger until we have behave v2 framework completed
    os.environ["LOG_LEVEL"] = "DEBUG"
    try:
        exit_code = behave_main(sys.argv[1:])
    finally:
        os.chdir(cwd)
        sys.exit(exit_code)
