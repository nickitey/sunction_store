import logging
from typing import Callable

import main

logging.basicConfig(
    filemode="w",
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt="%d/%m/%Y %H:%M:%S",
    filename="heic_converter.log",
    encoding="utf-8",
    level=logging.INFO,
)


def fill_table_with_links(processed_data: list, data_template: dict, handler: bool | Callable = None) -> dict:
    """

    :param processed_data: Коллекция обрабатываемых данных, словарь, где
    ключ - артикул или иная индивидуальная характеристика товара
    :param data_template: Заготовка итоговой коллекции, которая будет
    преобразована в датафрейм для записи в *.xlsx-файл.
    :param handler: Функция-обработчик данных, если есть, то применяется
    на обрабатываемых данных (например, обработка строк от посторонних
    и запрещенных символов). Значение по-умолчанию: None
    :return: Заполненная данными итоговая коллекция.

    Предполагается, что data-template представляет собой словарь, в котором
    ключами выступают артикулы товаров, а значениями - коллекции параметров,
    которые впоследствии будут рассортированы по столбцам таблицы. То есть,
    в итоговой таблице одному товару будет соответствовать строка, в которой
    в первом столбце будет артикул (как индивидуальная характеристика),
    а в остальных столбцах по одной характеристике, в данном случае - ссылки
    Подходящих коллекций может быть две: множество (set) и список (list).
    Использование set сомнительно, поскольку это неиндексируемая коллекция,
    поэтому при подготовке данных для pandas необходима конвертация в list,
    но при этом не гарантируется, что в списке элементы будут в том же порядке,
    в каком они были в множестве.
    Необходимо подумать о целесообразности изначального выбора в качестве
    коллекции списка и последущей проверке на каждой итерации наличия в нем
    дубликата добавляемого элемента
    """
    for filename in processed_data:
        if ".heic" in filename:
            continue
        parts_of_way = filename.split("/")
        brand_folder = parts_of_way[-3]
        model_folder = parts_of_way[-2]
        image_file = parts_of_way[-1]
        if model_folder not in data_template:
            # Если все же будет list, то необходимо поменять тип данных здесь...
            # data_template[model_folder] = list()
            data_template[model_folder] = set()
        link_template = "catalog/suppliers/imperial/{}/{}/{}"
        link = link_template.format(brand_folder, model_folder, image_file)
        if handler:
            link = handler(link)
        # if link not in data_template[model_folder]:
        #    data_template[model_folder].append(link)
        # ...и добавить вот эту проверку вхождения ссылки в обрабатываемый список
        # Мне это не нравится, потому что алгоритм становится квадратичной
        # сложности: каждый элемент списка сравнивается с другими элементами
        # списка эквивалетное длине списка раз
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
    # Чуз ё файтер, как говорится
    prep_data[value] = set()
    # prep_data[value] = list()

root = "/home/nikita/Desktop/Медицинские оправы"

raw_directories, raw_files = main.collect_paths_from_tree(root, True)

extensions = [".jpg", ".heic", ".webm", ".jpeg",
              ".JPG", ".HEIC", ".JPEG", ".WEBM",
              ".PNG", ".png", ".webp", ".WEBP",
              ".bmp", ".BMP"]

converted_file_list = [
    main.convert_image_to_jpg(file) if ".heic" in file else file
    for file in raw_files
]

prepared_for_conversion = fill_table_with_links(
    converted_file_list, prep_data, main.clean_string_from_forbidden_symbols
)

"""
keys_list = [
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
    "eleventh",
    "twelfth",
    "thirteenth",
    "fourteenth",
    "fifteenth",
    "sixteenth",
    "seventeenth",
    "eighteenth",
    "nineteenth",
    "twentieth",
    "twenty first",
    "twenty second",
    "twenty third",
    "twenty fourth",
    "twenty fifth",
    "twenty sixth",
    "twenty seventh",
    "twenty eighth",
    "twenty ninth",
    "thirtieth"
]
"""
# Я не ожидал, что в папке может быть так много файлов, поэтому вручную
# прописывать названия столбцов уже не получится, нужно автоматизированное
# решение

keys_list = []
for i in range(1000):
    keys_list.append(f"column no. {i}")

to_write = main.prepare_data_for_pandas(prepared_for_conversion, keys_list)

main.write_to_excel(to_write, "imperial_optic_links.xlsx")

# Хотя функция и возвращает список переименованных директорий и файлов,
# Фактически результат работы этой нам не нужен. Данные, которые пойдут
# в таблицу, уже обработаны (очищены от запрещенных символов и приведены
# к требуемому "стандарту", скажем так (catalog/suppliers/imperial/ и т.д.)
# Поэтому заниматься фактическим переименованием директорий мы будем уже
# после того, как данные собраны и записаны в таблицу.

main.rename_os_items(
    root, main.clean_string_from_forbidden_symbols, raw_directories, raw_files
)
