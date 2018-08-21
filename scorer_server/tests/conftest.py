import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--end-to-end", action='store_true', default=False, help="run end to end tests."
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--end-to-end"):
        return
    skip_end_to_end = pytest.mark.skip(reason="need --end-to-end option to run")
    for item in items:
        if "end_to_end" in item.keywords:
            item.add_marker(skip_end_to_end)


