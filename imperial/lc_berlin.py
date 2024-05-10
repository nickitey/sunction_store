from main import read_from_excel, write_to_excel, test_data_dict

file = r"Наличие склада на 16.01.2024 .xlsx"
sheet = "Лист2"
cols = list(range(3))

data = read_from_excel(file, sheet, cols)

# dict_keys(['Бренд', 'Вид', 'Характеристика'])
brand = data["Бренд"]
product_type = data["Вид"]
specs = data["Характеристика"]


def split_clean_strings(
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


def prepare_data_for_pandas(dataset: dict, keys_list: list) -> dict:
    """

    :param dataset: dataset to be processed; typically result of manipulation
    with source data.
    :param keys_list: column headers after prepared data is parsed
    and converted with pandas to table file.
    :return: dictionary with keys from keys_list, values are also dictionary
    where keys represent strings numbers in table file.
    """

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
            raise TypeError(
                f"The type of data in dictionary has no length, so cannot be empty."
            )

    data_keys = list(dataset.keys())
    prepared_data = {key: {} for key in keys_list}
    parameters_amount = len(dataset)
    for i in range(parameters_amount):
        prepared_data[keys_list[0]][i] = data_keys[i]
        for y in range(1, len(dataset[data_keys[i]]) + 1):
            prepared_data[keys_list[y]][i] = dataset[data_keys[i]][y - 1]
    return clear_empty_keys(prepared_data)


lc_berlin = {
    specs[i]: split_clean_strings(specs[i], ":", "IB ", "")
    for i in brand.keys()
    if brand[i] == "Ic-berlin" and product_type[i] == "Оптическая оправа"
}

target_keys = [
    "title",
    "first part",
    "second part",
    "third part",
    "fourth part",
    "fifth part",
    "sixth part",
    "seventh part",
]

to_write = prepare_data_for_pandas(lc_berlin, target_keys)

try:
    write_to_excel(to_write, "lc_berlin_splitted.xlsx")
except Exception as e:
    print(e)
else:
    print("Готово")
