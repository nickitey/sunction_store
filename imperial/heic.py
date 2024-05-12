import logging
import os
from datetime import datetime

import main

logging.basicConfig(
    filemode="w",
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt="%d/%m/%Y %I:%M:%S %p",
    filename="heic_converter.log",
    encoding="utf-8",
    level=main.logging.INFO,
)


def fill_table_with_links(processed_data, data_template, handler=None):
    for filename in processed_data:
        if ".heic" in filename:
            continue
        parts_of_way = filename.split("/")
        brand_folder = parts_of_way[-3]
        model_folder = parts_of_way[-2]
        image_file = parts_of_way[-1]
        if model_folder not in data_template:
            data_template[model_folder] = set()
        link_template = "catalog/suppliers/imperial/{}/{}/{}"
        link = link_template.format(brand_folder, model_folder, image_file)
        if handler:
            link = handler(link)
        data_template[model_folder].add(link)
    return data_template


input_table_file = "work_table.xlsx"
sheet = "Лист1"
cols = [0, 3]

input_data = main.read_from_excel(input_table_file, sheet, cols)

brands = input_data["Бренд"]
model = input_data["Характеристика"]

prep_data = {}
for value in model.values():
    prep_data[value] = set()


root = f"{os.getcwd()}/opravy"

raw_directories, raw_files = main.collect_paths_from_tree(root, True)
converted_file_list = [
    main.convert_image_from_heic_to_jpg(file) if ".heic" in file else file
    for file in raw_files
]
prepared_for_conversion = main.clear_empty_keys(
    fill_table_with_links(converted_file_list, prep_data, main.string_proceed)
)

# Хотя функция и возвращает список переименованных директорий и файлов,
# Фактически результат работы этой нам не нужен. Данные, которые пойдут
# в таблицу, уже обработаны (очищены от запрещенных символов и приведены
# к требуемому "стандарту", скажем так (catalog/suppliers/imperial/ и т.д.)

main.rename_os_items(
    main.clean_string_from_forbidden_symbols, root, raw_directories, raw_files
)

keys_list = [
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "nineth",
    "tenth",
]
to_write = main.prepare_data_for_pandas(prepared_for_conversion, keys_list)

try:
    main.write_to_excel(to_write, "lets_try_it.xlsx")
except Exception as e:
    logging.exception(e)
else:
    day = datetime.now().strftime("%d-%m-%Y")
    time = datetime.now().strftime("%H:%M:%S")
    message = f"Работа завершена {day} в {time}."
    logging.info(message)
    print(f"Готово, дата: {day}, время: {time}")
