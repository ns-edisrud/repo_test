python_library(
    name="lib",
    dependencies=[
        "3rdparty/python:ansicolor",
        "3rdparty/python:behave",
        "3rdparty/python:boto3",
        "3rdparty/python:requests",
        "test_utils/behave/src",
    ],
    sources=globs("ns_tests_replicated/**/*"),
    tags={"python", "tests", "tests-tableau-server"},
)
python_binary(
    name="tests-replicated",
    source="ns_tests_tableau_server/behave_cli.py",
    dependencies=[":lib"],
    tags={"python", "tests", "tests-tableau-server"},
)