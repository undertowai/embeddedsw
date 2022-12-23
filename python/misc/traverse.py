import os


class Traverse:
    def walk(dict, root, func):
        for root, dirs, files in os.walk(root):
            if len(dirs) == 0:
                func(dict, root, files)

            for dir in dirs:
                Traverse.walk(dict, root + dir, func)
