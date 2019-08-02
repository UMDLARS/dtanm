import os


def get_test_resource(*args):
    return os.path.abspath(os.path.join(__file__, f'../../../test_data', *args))
