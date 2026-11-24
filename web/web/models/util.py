import os

def remove_quiet(path):
    try:
        os.remove(path)
    except:
        pass
