import logging
import math
import os.path
from os import path, rename, walk

import pandas as pd
import pillow_heif
from PIL import Image

nan = float("nan")

pillow_heif.register_heif_opener()


class SunctionStoreScriptError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def read_from_excel(path_to_file, sheet, cols):
    xl = pd.ExcelFile(path_to_file)
    dataframe = pd.read_excel(xl, sheet, usecols=cols)
    return dataframe.to_dict()


def write_to_excel(data_dict, path_to_file, sheet="python"):
    to_write_db = pd.DataFrame.from_dict(data_dict)
    to_write_db.to_excel(path_to_file, sheet_name=sheet)


def test_data_dict(data_dict, test_asset):
    def compare_details(item1, item2):
        if isinstance(item1, float) and isinstance(item2, float):
            if not (math.isnan(item1) and math.isnan(item2)):
                print("nan and nan")
                return False
            return True
        elif isinstance(item1, list) and isinstance(item2, list):
            if len(item1) != len(item2):
                print("different length")
                return False
            for i in range(len(item1)):
                if isinstance(item1[i], float) and isinstance(item2[i], float):
                    if not (math.isnan(item1[i]) and math.isnan(item2[i])):
                        print("nan and nan in list")
                        return False
                elif item1[i] != item2[i]:
                    print("different elements in list")
                    print(type(item1[i]), type(item2[i]))
                    print(item1[i], item2[i])
                    return False
        else:
            print("different types")
            return False
        return True

    test_status = True
    for item in test_asset:
        try:
            checker = test_asset[item]
            checked = data_dict[item]
        except KeyError:
            print(f"Test failed with {item}.")
            print(f"Key {item} is absent in tested dictionary.")
            return False
        try:
            assert checker == checked
        except AssertionError:
            if compare_details(checker, checked):
                continue
            test_status = False
            print(f"Test failed with {item}.")
            print(
                f"Expected: {test_asset[item]}, "
                f"type - {type(test_asset[item])}."
            )
            print(
                f"Received: {data_dict[item]}, "
                f"type - {type(data_dict[item])}."
            )
    if test_status:
        print("All tests passed")
    return test_status


def split_and_clean_strings(
    string: str, delimiter: str, replace_from=None, replace_to=None
) -> list:
    """

    :param string: string to process | str
    :param delimiter: delimiter for splitting string | str
    :param replace_from: if used, selects the pattern in substring to replace
    :param replace_to: if used with replace_from-parameter, used as replace
           for replaced pattern
    :return: list of initial string's parts | list
    """
    substrings_list = string.split(delimiter)
    for i in range(len(substrings_list)):
        substrings_list[i] = substrings_list[i].strip()
        if replace_from:
            substrings_list[i] = substrings_list[i].replace(
                replace_from, replace_to
            )
    return substrings_list


def clear_empty_keys(dictionary: dict) -> dict:
    """

    :param dictionary: python dictionary with any numbers of keys
    :return: same dictionary but without keys which values are zero-length:
    strings, dictionaries, lists, sets, tuples

    NB! If key's value has no 'length' attribute, TypeError rises.
    """
    try:
        return {
            key: dictionary[key]
            for key in dictionary
            if len(dictionary[key]) != 0
        }
    except TypeError:
        err_message = ("The type of data in dictionary has no length,"
                       " so cannot be empty.")
        logging.exception(err_message)
        raise SunctionStoreScriptError(err_message)


def prepare_data_for_pandas(dataset: dict, keys_list: list) -> dict:
    """

    :param dataset: dataset to be processed; typically result of manipulation
    with source data.
    :param keys_list: column headers after prepared data is parsed
    and converted with pandas to table file.
    :return: dictionary with keys from keys_list, values are also dictionary
    where keys represent strings numbers in table file.
    """
    data_keys = list(dataset.keys())
    prepared_data = {key: {} for key in keys_list}
    parameters_amount = len(dataset)
    for i in range(parameters_amount):
        list_in_dataset = dataset[data_keys[i]]
        prepared_data[keys_list[0]][i] = data_keys[i]
        for y in range(1, len(dataset[data_keys[i]]) + 1):
            try:
                prepared_data[keys_list[y]][i] = list_in_dataset[y - 1]
            except IndexError as e:
                logging.exception(
                    f'{e} with index = {y}, dataset = {list_in_dataset}, '
                    f'keys = {keys_list}'
                )
                raise SunctionStoreScriptError(e)
    return clear_empty_keys(prepared_data)


def string_proceed_casual(proc_string):
    return (
        proc_string.lower()
        .replace(" ", "_")
        .replace(",", "")
        .replace(";", "_")
        .replace("'", "")
        .replace(".", "_")
    )


def string_proceed_universal(proc_string, replacements_dict, lower=False, upper=False):
    if lower:
        proc_string = proc_string.lower()
    if upper:
        proc_string = proc_string.upper()
    for replace_pattern in replacements_dict:
        proc_string = proc_string.replace(replace_pattern, replacements_dict[replace_pattern])
    return proc_string


def clean_string_from_forbidden_symbols(string):
    file_extension = string[-5:]
    extensions = [".jpg", ".heic", ".webm"]
    for extension in extensions:
        if file_extension.endswith(extension):
            string_parts = string.split(extension)
            proceeded_parts = list(map(string_proceed_casual, string_parts))
            return extension.join(proceeded_parts)
    return string_proceed_casual(string)


def convert_image_from_heic_to_jpg(file_path):
    new_file_name = file_path.strip(".heic")
    new_file_path = f"{new_file_name}.jpg"
    try:
        img = Image.open(file_path)
        img.save(
            new_file_path,
            format="JPEG",
            quality=100,
            optimize=True,
            progressive=True,
        )
        logging.info(f"{file_path} converted into {new_file_name}.jpg.")
        return new_file_path
    except Exception as e:
        logging.exception(e)


def collect_paths_from_tree(root_url, collect_files=False):
    if not os.path.exists(root_url):
        err_message = (f'{root_url} does not exist. Check the path is correct '
                       f'and retry.')
        logging.exception(err_message)
        raise SunctionStoreScriptError(err_message)
    dirs_list = []
    files_list = []
    for cur_dir, subdirs, files in walk(root_url):
        dirs_list.append(path.abspath(cur_dir))
        if collect_files:
            for file in files:
                path_to_file = f"{cur_dir}/{file}"
                files_list.append(path_to_file)
    return dirs_list, files_list


def rename_os_items(handler, source, *lists_to_handle):
    for items_list in lists_to_handle:
        for old_item_name in items_list:
            item_name_elements = old_item_name.split("/")
            item_name_elements[-1] = handler(item_name_elements[-1])
            new_item_name = "/".join(item_name_elements)
            if old_item_name == new_item_name:
                continue
            try:
                rename(old_item_name, new_item_name)
            except FileNotFoundError as e:
                logging.exception(e)
                lists_to_handle = collect_paths_from_tree(source, True)
                return rename_os_items(handler, source, *lists_to_handle)
            else:
                logging.info(f"{old_item_name} renamed to {new_item_name}")
    return collect_paths_from_tree(source, True)
