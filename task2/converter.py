# -*- coding: utf-8 -*-

import os
import shutil
import re
import json

DIR_LOCATION = ""
DIR_KNOWLEDGE_BASE = "knowledge_base"
DIR_SOURCE = "source_data"
DIR_DATA = "Warhammer 40000 books"

FILE_MAP_RENAME = "terms_map.json"
ENCODING_DEFAULT = "UTF-8"


def read_mapper():
    if not os.path.isfile(FILE_MAP_RENAME):
        print(f"ERROR: no '{FILE_MAP_RENAME}' file!")
        exit(1)
    with open(FILE_MAP_RENAME, "r", encoding=ENCODING_DEFAULT) as file:
        data = json.load(file)

    print("INFO: Using content remapper:")
    print(json.dumps(data, indent=4))
    return data


def copy_remapped_content(filepath_src, filepath_dst, mapper):
    with open(filepath_dst, "w", encoding=ENCODING_DEFAULT) as output_file:
        with open(filepath_src, "r", encoding=ENCODING_DEFAULT) as input_file:
            for line in input_file:
                for lhv, rhv in mapper.items():
                    regex_replace = re.compile(re.escape(lhv), re.IGNORECASE)
                    line = regex_replace.sub(rhv, line)
                output_file.write(line)


def convert_data():
    if not os.path.isdir(DIR_SOURCE):
        print(f"ERROR: no {DIR_SOURCE} directory!")
        exit(1)
    if not os.path.isdir(DIR_KNOWLEDGE_BASE):
        os.makedirs(DIR_KNOWLEDGE_BASE)

    remapper = read_mapper()

    for address, _, files in os.walk(DIR_SOURCE):
        for name in files:
            src_path = os.path.join(address, name)
            dest_dir = address.replace(DIR_SOURCE, DIR_KNOWLEDGE_BASE)
            dest_path = os.path.join(dest_dir, name)
            os.makedirs(dest_dir, exist_ok=True)

            print(
                f"INFO: Copy remapped file content "
                f"from \n\t{src_path}\nto\n\t{dest_path}"
            )
            copy_remapped_content(src_path, dest_path, remapper)


def copy_fb2_file_content(filepath_src, filepath_dst, func=None):
    supported_codecs = [ENCODING_DEFAULT, "windows-1251"]
    with open(filepath_dst, "w", encoding=ENCODING_DEFAULT) as output_file:
        content = list[str]()
        for codec in supported_codecs:
            try:
                with open(filepath_src, "r", encoding=codec) as input_file:
                    content = input_file.readlines()
                    # content = re.findall(r"<p>(.+)<\/p>", source_content)
                    if func:
                        content = func(str().join(content))
                        content = [line + "\n" for line in content]
            except Exception as error:
                print("WARNING: ", error)
        if not content:
            print("ERROR: could not read file", filepath_src)
            exit(1)
        output_file.writelines(content)


def prepare_source_data():
    if not os.path.isdir(DIR_DATA):
        print(f"ERROR: no {DIR_DATA} directory!")
        exit(1)
    if not os.path.isdir(DIR_SOURCE):
        os.makedirs(DIR_SOURCE)

    files_copy_count = 0
    files_copy_count_txt = 0
    files_copy_count_fb2 = 0
    for address, _, files in os.walk(DIR_DATA):
        for name in files:
            src_path = os.path.join(address, name)
            dest_dir = address.replace(DIR_DATA, DIR_SOURCE)
            dest_path = os.path.join(dest_dir, name)
            if name.endswith("fb2"):
                dest_path = dest_path.replace("fb2", "txt")
                print(
                    f"INFO: Copy FB2 file content "
                    f"from \n\t{src_path}\nto\n\t{dest_path}"
                )
                os.makedirs(dest_dir, exist_ok=True)
                copy_fb2_file_content(
                    src_path,
                    dest_path,
                    lambda content: re.findall(r"<p>(.+)<\/p>", content),
                )
                files_copy_count_fb2 += 1
            elif name.endswith("txt"):
                print(f"INFO: Copy TXT file from \n\t{src_path}\nto\n\t{dest_path}")
                os.makedirs(dest_dir, exist_ok=True)
                copy_fb2_file_content(
                    src_path,
                    dest_path,
                )
                # shutil.copy(src_path, dest_path)
                files_copy_count_txt += 1
            else:
                print(f"INFO: Ignoring file {src_path}.")

            files_copy_count += os.path.isfile(dest_path)

    print(
        f"INFO: Finished preparing source data. Copied {files_copy_count} files."
        f"There should be {files_copy_count_txt} TXT files and {files_copy_count_fb2} FB2."
    )


if __name__ == "__main__":
    DIR_LOCATION = os.path.dirname(os.path.abspath(__file__))
    DIR_KNOWLEDGE_BASE = os.path.join(DIR_LOCATION, DIR_KNOWLEDGE_BASE)
    DIR_SOURCE = os.path.join(DIR_LOCATION, DIR_SOURCE)
    DIR_DATA = os.path.join(DIR_LOCATION, DIR_DATA)
    FILE_MAP_RENAME = os.path.join(DIR_LOCATION, FILE_MAP_RENAME)

    prepare_source_data()
    convert_data()
