from main import read_from_excel, write_to_excel, nan

file = r"C:\Users\klast\Downloads\Наличие склада на 16.01.2024 .xlsx"
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


lc_berlin = {
    specs[i]: split_clean_strings(specs[i], ":", "IB ", "")
    for i in brand.keys()
    if brand[i] == "Ic-berlin" and product_type[i] == "Оптическая оправа"
}

to_write = {
    "title": {},
    "first part": {},
    "second part": {},
    "third part": {},
    "fourth part": {},
    "fifth part": {},
    "sixth part": {},
    "seventh part": {},
}
lc_berlin_keys = list(lc_berlin.keys())
count = 0

for i in range(len(lc_berlin)):
    to_write["title"][i] = lc_berlin_keys[i]
    try:
        to_write["first part"][i] = lc_berlin[lc_berlin_keys[i]][0]
        to_write["second part"][i] = lc_berlin[lc_berlin_keys[i]][1]
        to_write["third part"][i] = lc_berlin[lc_berlin_keys[i]][2]
        to_write["fourth part"][i] = lc_berlin[lc_berlin_keys[i]][3]
        to_write["fifth part"][i] = lc_berlin[lc_berlin_keys[i]][4]
        to_write["sixth part"][i] = lc_berlin[lc_berlin_keys[i]][5]
        to_write["seventh part"][i] = lc_berlin[lc_berlin_keys[i]][6]
    except IndexError:
        continue


for key in to_write:
    length = len(to_write[key])
    print(f'{key} length is {length}.')

try:
    write_to_excel(to_write, "lc_berlin_splitted.xlsx")
except Exception as e:
    print(e)
else:
    print("Готово")
