import os

DIR_KNOWLEDGE_BASE = "knowledge_base"
DIR_SOURCE = "source_data"
DIR_DATA = "Warhammer 40000 books"

FILE_MAP_RENAME = "terms_map.json"


def convert_data():
    if not os.path.isdir(DIR_SOURCE):
        print(f"ERROR: no {DIR_SOURCE} directory!")
        exit(1)
    if not os.path.isfile(FILE_MAP_RENAME):
        print(f"ERROR: no '{FILE_MAP_RENAME}' file!")
        exit(1)
    if not os.path.isdir(DIR_KNOWLEDGE_BASE):
        os.makedirs(DIR_KNOWLEDGE_BASE)


def prepare_source_data():
    if not os.path.isdir(DIR_DATA):
        print(f"ERROR: no {DIR_DATA} directory!")
        exit(1)
    if not os.path.isdir(DIR_SOURCE):
        os.makedirs(DIR_SOURCE)


if __name__ == "__main__":
    prepare_source_data()
    convert_data()
