import os
import pathlib

def getAllItems(mainPath):
    return list(pathlib.Path(mainPath).rglob("*"))

if __name__ == "__main__":
    MUSIC_DIR = os.path.expanduser("~/Music/")
    allItems = getAllItems(MUSIC_DIR)

    for item in allItems:
        if not os.path.isdir(item):
            print(item)
