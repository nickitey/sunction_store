import logging
import math
import os.path
from datetime import datetime
from os import path, rename, walk
from typing import Any, Callable

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


def read_from_excel(path_to_file: str, sheet: str, cols: list) -> dict:
    """

    Функция парсит xlsx-файл и возвращает словарь словарей, где ключи -
    названия столбцов, значения - словари, где ключи - номера строк,
    значения - соответствующие значения из ячеек таблицы.

    :param path_to_file: Путь к файлу в формате *.xlsx
    :param sheet: Название листа, на котором находятся требуемые данные.
    :param cols: Список колонок, которые необходимо собрать
    :return: Словарь словарей описанного формата

    """
    xl = pd.ExcelFile(path_to_file)
    dataframe = pd.read_excel(xl, sheet, usecols=cols)
    return dataframe.to_dict()


def write_to_excel(
    data_dict: dict, path_to_file: str, sheet: str = "python"
) -> None:
    """

    Функция принимает подготовленные данные и записывает их в файл *.xlsx.

    :param data_dict: Словарь данных для записи в файл.
    :param path_to_file: Путь к файлу. Если такого файла нет, он будет создан.
    Если файл есть - перезапишется без сожаления и возможности восстановления
    :param sheet: Название листа, на который будут записаны данные.
    По-умолчанию - "python".
    :return: Ничего.

    """
    to_write_db = pd.DataFrame.from_dict(data_dict)
    try:
        to_write_db.to_excel(path_to_file, sheet_name=sheet)
    except Exception as e:
        logging.exception(e)
    else:
        day = datetime.now().strftime("%d-%m-%Y")
        time = datetime.now().strftime("%H:%M:%S")
        message = f"Запись в файл {path_to_file} завершена {day} в {time}."
        logging.info(message)
        print(message)


def test_data_dict(data_dict: dict, test_asset: dict) -> bool:
    """

    Функция тестирует ассеты с данными: проверяет переданный есть
    на тестирование словарь 'data_dict' и сверяет его с эталонным
    словарем 'test_asset'.

    :param data_dict: Проверяемый словарь с данными.
    :param test_asset: Проверочный, эталонный словарь. Количество
    элементов в нем меньше или равно таковому в проверяемом словаре.
    Проверка происходит именно по ключам тестового словаря.
    :return: Булево значение: True, если тест пройден, False в обратном
    случае.

    """
    def compare_details(item1, item2):
        """

        Функция для глубокой сверки двух объектов на идентичность.
        В ходе разработки обнаружилась небольшая особенность:
        два nan не равны друг другу, хотя оба вроде бы Not a Number
        типа float. Соответственно, два любых других элемента (списки,
        словари и др.), которые содержат nan, будут не равны друг другу,
        поскольку в них есть как минимум один отличающийся друг от друга
        элемент nan. Поэтому функция вызывается только в сложных случаях
        и проводит более подробное сравнение двух элементов, включая проверку
        на nan.
        Поддерживается как сравнение двух объектов типа float, так и двух
        объектов типа list.

        :param item1: Сверяемый элемент № 1.
        :param item2: Сверяемый элемент № 2.
        :return: True, если объекты равны, False в обратном случае.

        """
        if isinstance(item1, float) and isinstance(item2, float):
            # Если оба объекта типа float...
            if not (math.isnan(item1) and math.isnan(item2)):
                # Но при этом оба одновременно не nan...
                print("nan and nan")
                # Они не равны.
                return False
            return True
        elif isinstance(item1, list) and isinstance(item2, list):
            # Если оба объекта типа list...
            if len(item1) != len(item2):
                # Но при этом разной длины...
                print("different length")
                # Они не равны.
                return False
            for i in range(len(item1)):
                # Если все же они одной длины...
                if isinstance(item1[i], float) and isinstance(item2[i], float):
                    # Грубо нарушется принцип "DON'T REPEAT YOURSELF"
                    # и повторяется проверка равенства двух float.
                    if not (math.isnan(item1[i]) and math.isnan(item2[i])):
                        print("nan and nan in list")
                        # Принципиальная разница в том, что здесь хоть
                        # программа подсказывает, что объекты типа list
                        # не равны, потому что в них есть nan.
                        return False
                elif item1[i] != item2[i]:
                    # Ну или если просто есть два списка с разными элементами
                    print("different elements in list")
                    # Мы об этом узнаем
                    print(f"{item1[i]} with type {type(item1[i])} differs "
                          f"from {item2[i]} with type {type(item2[i])}")
                    # А еще узнаем, что за элементы и какого они типа данных
                    return False
        else:
            # Ну или просто два разных типа данных переданы в функцию
            print("different types")
            # Как же они могут быть равны
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

    Небольшая функция, которая принимает строку, разделяет ее на список
    подстрок по подстроке 'delimiter', после чего каждую зачищает методом
    strip(), если необходимо, заменяет какой-то паттерн 'replace_from'
    на 'replace_to' и возвращает список подстрок.

    :param string: Строка для обработки.
    :param delimiter: Подстрока, по которой происходит разделение.
    :param replace_from: Если использовано, определяет, какая подстрока
    будет заменена в каждой подстроке в получившемся списке.
    :param replace_to: Если использовано, определяет, на какую подстроку
    будет заменена подстрока 'replace_from' в каждой подстроке в получившемся
    списке.
    :return: Список из подстрок оригинальной строки.

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

    Функция очищает словарь от ключей с "пустыми" значениями.

    :param dictionary: Словарь с произвольным количеством ключей.
    :return: Тот же словарь, но без ключей, значения которых имеют
    значение с "нулевой" длиной: строки, словари, списки, множества,
    кортежи.

    NB! Если у значения какого-либо ключа нет атрибута "длина" (int, float,
    bool, None), поднимается исключение, основанное на TypeError.

    """
    try:
        return {
            key: dictionary[key]
            for key in dictionary
            if len(dictionary[key]) != 0
        }
    except TypeError:
        err_message = (
            "The type of data in dictionary has no length,"
            " so cannot be empty."
        )
        logging.exception(err_message)
        raise SunctionStoreScriptError(err_message)


def prepare_data_for_pandas(dataset: dict, keys_list: list) -> dict:
    """

    После чтения данных из файлов данные, содержащиеся в них, представлены
    в виде словаря словарей, где ключи "первого уровня" - заголовки столбцов,
    их значения - словари данных из столбца. В словарях "второго уровня" ключи
    представляют собой номера строк, а значения - данные из соответствующих
    ячеек.
    Функция подготавливает переданный словарь в словарь, подготовленный
    для записи с помощью pandas в *.xlsx-файл: в нем данные в словаре
    произвольного вида преобразуются в словарь словарей вида, аналогичного
    тому, который появляется в результате чтения файла.

    :param dataset: Словарь данных, в котором ключи - итерируемые объекты.
    :param keys_list: Список ключей, которые будут заголовками столбцов
    итоговой таблицы.
    :return: Словарь, где ключи - элементы списка 'keys_list', значения -
    словари, в которых ключи - номера строк будущей таблицы, значения -
    данные в ячейках на пересечении столбца из списка 'keys_list' и номера
    строки.

    """
    data_keys = list(dataset.keys())
    prepared_data = {key: {} for key in keys_list}
    parameters_amount = len(dataset)
    for i in range(parameters_amount):
        list_in_dataset = dataset[data_keys[i]]
        if isinstance(list_in_dataset, set):
            list_in_dataset = list(list_in_dataset)
        # На случай если обрабатываемые параметры артикулов будут представлены
        # множеством, здесь мы преобразуем их в список, чтобы не напороться
        # на IndexError в попытке получить элемент множества по индексу
        prepared_data[keys_list[0]][i] = data_keys[i]
        for y in range(1, len(dataset[data_keys[i]]) + 1):
            try:
                prepared_data[keys_list[y]][i] = list_in_dataset[y - 1]
            except IndexError as e:
                error_message = (
                    f"{e} with index = {y},\n"
                    f"last value before error = {list_in_dataset[y - 1]},\n"
                    f"common dataset length = {len(list_in_dataset)},\n"
                    f"keys prepared = {len(keys_list)}"
                )
                logging.exception(error_message)
                raise SunctionStoreScriptError(error_message)
    return clear_empty_keys(prepared_data)


def string_proceed_casual(proc_string: str) -> str:
    """
    Простой обработчик строк, убирает запятые, апострофы (одинарные кавычки),
    заменяет слэши, пробелы, точки с запятой, и точки на нижние подчеркивания.

    :param proc_string: Обрабатываемая строка
    :return: Обработанная строка
    """
    return (
        proc_string.lower()
        .replace(" ", "_")
        .replace(",", "")
        .replace(";", "_")
        .replace("'", "")
        .replace(".", "_")
        .replace("/", "_")
    )


def string_proceed_universal(
    proc_string: str,
    replacements_dict: dict,
    lower: bool = False,
    upper: bool = False,
) -> str:
    """

    Гибкий обработчик строк, заменит любые символы на любые в строке.
    Альтернатива длинной цепочке вызовов метода replace().

    :param proc_string: Обрабатываемая строка.
    :param replacements_dict: Словарь, где ключи - заменяемые символы
    (их комбинации), а значения - символы (их комбинации), на которые
    будет происходить замена.
    :param lower: Если True, переводит строку в нижний регистр.
    :param upper: Если True, переводит строку в верхний регистр.
    :return: Обработанная строка.

    NB! Функция проверяет наличие символов (комбинаций), которые нужно
    заменить, по очереди их вхождения в словарь. Поэтому если в словаре
    замен сначала встретится {'.': ';'}, а потом {';': ' '}, то в обработанной
    строке не останется ни одной точки с запятой.

    """
    if lower and upper:
        message = "Ты уж определись как-то, что ты хочешь со строкой сделать."
        raise SunctionStoreScriptError(message)
    if lower:
        proc_string = proc_string.lower()
    if upper:
        proc_string = proc_string.upper()
    for replace_pattern in replacements_dict:
        proc_string = proc_string.replace(
            replace_pattern, replacements_dict[replace_pattern]
        )
    return proc_string


def process_string_except_extension(
    string: str,
    handler: Any = None,
    extensions: list = None,
) -> str:
    """

    Функция принимает на вход строку - имя файла, разбивает ее на подстроки:
    название и расширение, обратаывает переданной функцией только название,
    после чего возвращает склеенные обработанную строку и расширение
    (расшириение возвращается в нижнем регистре, независимо от того,
    в каком оно было в исходном имени файла).

    :param string: Исходная строка (как правило, имя файла)
    :param handler: Функция-обработчик строк (замена символов, изменение
    регистра и др.)
    :param extensions: Итерируемый объект, содержащий возможные расширения
    файлов, которые не подлежат обработке.
    Расширения, не переданные явно в функцию, воспринимаются как часть строки
    и обрабатываются по общим правилам функции 'handler'.
    :return: Обработанная строка (как правило, обработанное имя файла
    и расшиирение).

    """
    if extensions:
        file_extension = string[-5:]
        for extension in extensions:
            if file_extension.endswith(extension):
                string_parts = string.split(extension)
                proceeded_parts = list(map(handler, string_parts))
                return extension.lower().join(proceeded_parts)
    return handler(string)


def convert_image_to_jpg(file_path: str) -> str:
    """

    Используя возможности пакета Pillow, преобразовывает изображения форматов
    *.heic, *.webp, *.bmp, *.tiff в изображение формата *.jpg. Качество
    изображения при этом не изменяется.
    Попытка конвертировать изображение другого формата вызовет ошибку.

    :param file_path: Полный путь к исходному файлу изображения.
    :return: Полный путь к преобразованному изображению.
    Само преобразованное изображение появляется в одной директории с исходным.

    """
    if file_path.endswith(".heic") or file_path.endswith(".HEIC"):
        new_file_name = file_path.strip(".heicHEIC")
        new_file_path = f"{new_file_name}.jpg"
    elif file_path.endswith(".webp") or file_path.endswith(".WEBP"):
        new_file_name = file_path.strip(".webmWEBM")
        new_file_path = f"{new_file_name}.jpg"
    elif file_path.endswith(".bmp") or file_path.endswith(".BMP"):
        new_file_name = file_path.strip(".bmpBMP")
        new_file_path = f"{new_file_name}.jpg"
    elif file_path.endswith(".tif") or file_path.endswith(".tif"):
        new_file_name = file_path.strip(".tifTIF")
        new_file_path = f"{new_file_name}.jpg"
    else:
        splitted_file_path = file_path.split(".")
        extension = splitted_file_path[-1]
        error_message = f"Files with .{extension} are not supported."
        logging.exception(error_message)
        raise SunctionStoreScriptError(error_message)
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


def collect_paths_from_tree(
    root_path: str, collect_files: bool = False
) -> tuple:
    """

    Используя возможности функции path() из модуля os стандартной библиотеки,
    функция осуществляет рекурсивный обход по директории, путь к которой
    передан в функцию, а также по всем вложенным директориям, собирая адреса
    указанных директорий и, если в параметр collect_files передан аргумент
    True, всех содержащихся в них файлов.

    :param root_path: Адрес корневой директории, с которой начинается обход.
    :param collect_files: Булево значение: если True, функция собирает адреса
    файлов по пути рекурсивного обхода, если False - не собирает.
    :return: Кортеж списков, первый - список адресов всех директорий,
    второй - список адресов всех файлов внутри корневой директории и всех
    дочерних.

    """
    if not os.path.exists(root_path):
        err_message = (
            f"{root_path} does not exist. Check the path is correct "
            f"and retry."
        )
        logging.exception(err_message)
        raise SunctionStoreScriptError(err_message)
    dirs_list = []
    files_list = []
    for cur_dir, subdirs, files in walk(root_path):
        dirs_list.append(path.abspath(cur_dir))
        if collect_files:
            for file in files:
                path_to_file = f"{cur_dir}/{file}"
                files_list.append(path_to_file)
    del dirs_list[0]
    # Первый путь в списке - это имя самой папки, с которой начинается
    # рекурсивный обход. Нам он не нужен, потому что менять имя исходной
    # папки вряд ли нужно, в крайнем случае, это всегда можно сделать
    # позже вручную.
    return dirs_list, files_list


def rename_os_items(
    source: str, handler: Callable, *lists_to_handle: list
) -> tuple:
    """

    Функция принимает список адресов объектов (файлы, директории),
    обрабатывает указанные адреса переданной функцией "handler()",
    после чего фактически их переименовывает.

    :param source: Адрес корневой директории, в которой находятся все
    объекты, подлежащие переименованию.
    :param handler: Функция-обработчик, определяющая изменения, которым
    будут подвергнуты переданные основной функции адреса объектов.
    :param lists_to_handle: Списки объектов, которые необходимо переименовать.
    :return: Результат работы функции collect_paths_from_tree: списки новых
    адресов переименованных объектов.

    """
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
                return rename_os_items(source, handler, *lists_to_handle)
            else:
                logging.info(f"{old_item_name} renamed to {new_item_name}")
    return collect_paths_from_tree(source, True)
