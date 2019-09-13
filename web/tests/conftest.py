import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--end-to-end", action='store_true', default=False, help="run end to end tests."
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--end-to-end"):
        skip_non_end_to_end = pytest.mark.skip(reason="not an end to end test")
        for item in items:
            if "end_to_end" not in item.keywords:
                item.add_marker(skip_non_end_to_end)
    else:
        skip_end_to_end = pytest.mark.skip(reason="need --end-to-end option to run")
        for item in items:
            if "end_to_end" in item.keywords:
                item.add_marker(skip_end_to_end)


