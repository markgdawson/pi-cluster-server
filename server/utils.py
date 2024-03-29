import os

def ensure_exists(directory):
    "Creates a directory unless it exists"

    while not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            print('directory creation failed: {directory}'.format(directory=directory))
