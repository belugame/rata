import sys

from .libs.application import Rata
from .libs.io import is_inside_git_dir


def main():
    try:
        file_name = sys.argv[1]
    except IndexError:
        print("File name argument missing. Start rata with a path like 'rata timerecords.txt'")
        sys.exit()

    if not is_inside_git_dir(file_name):
        print("No git directory. rata expects the given file name to be git-versioned to commit changes.")
        sys.exit()

    Rata(file_name)


if __name__ == '__main__':
    sys.exit(main())
