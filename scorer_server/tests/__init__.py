import os


def get_test_resource(name):
    return os.path.abspath(os.path.join(__file__, f'../../../test_data/{name}'))
