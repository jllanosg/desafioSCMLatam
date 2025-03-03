import os
from os import listdir
from os.path import isfile, join
from datetime import datetime

FOLDER_PATH = "./sample-files"
SECONDS_IN_A_MONTH = 2_592_000

def get_last_modification_time(path):
    try:
        return os.path.getmtime(path)
    except:
        return OSError(f"Couldn't find file {path}")
    
def get_seconds_old(timestamp):
    return (datetime.now()-datetime.fromtimestamp(timestamp)).seconds

def get_file_paths_from_folder_path(folder_path):
    return [f for f in listdir(folder_path) if isfile(join(folder_path, f))]


def main():
    try:
        files = get_file_paths_from_folder_path(FOLDER_PATH)
    except:
        return OSError(f"Couldn't find folder {FOLDER_PATH}")

    for file_path in files:
        last_modification_timestamp = get_last_modification_time(f"{FOLDER_PATH}/{file_path}")
        seconds_old = get_seconds_old(last_modification_timestamp)
        if seconds_old > SECONDS_IN_A_MONTH:
            os.remove(f"{FOLDER_PATH}/{file_path}")

if __name__ == "__main__":
    main()