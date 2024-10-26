import logging
from datetime import datetime
from functools import partial
from typing import Callable

import main

# Здесь мы настраиваем логирование, почти все ошибки и другая служебная
# информация будут записаны в лог-файл. Очень удобно потом смотреть какие-то
# рабочие моменты
# Здесь настройки на мой вкус, но в принципе, лучше их не трогать без особой
# нужды

date_format = "%d/%m/%Y"
time_format = "%H:%M:%S"

logging.basicConfig(
    filemode="w",
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt=f"{date_format} {time_format}",
    # Здесь можно задать имя будущего лог-файла
    filename="heic_converter.log",
    encoding="utf-8",
    level=logging.INFO,
)


# Определяем одну из функций, которая будет работать в этой программе


def fill_table_with_links(
    processed_data: list, data_template: dict, handler: Callable = None
) -> dict:
    """

    :param processed_data: Коллекция обрабатываемых данных, словарь, где
    ключ - артикул или иная индивидуальная характеристика товара
    :param data_template: Заготовка итоговой коллекции, которая будет
    преобразована в датафрейм для записи в *.xlsx-файл.
    :param handler: Функция-обработчик данных, если есть, то применяется
    на обрабатываемых данных (например, обработка строк от посторонних
    и запрещенных символов). Значение по-умолчанию: None
    :return: Заполненная данными итоговая коллекция.

    Предполагается, что data-template представляет собой словарь. Ключами
    в нем ключами выступают артикулы товаров (или иные индивидуальные
    характеристики), а значениями - коллекции параметров, которые впоследствии
    будут рассортированы по столбцам таблицы. То есть, в итоговой таблице
    одному товару будет соответствовать строка, в которой в первом столбце
    будет артикул (как индивидуальная характеристика), а в остальных столбцах
    по одной характеристике, в данном случае - ссылки. Подходящих коллекций
    может быть две: множество (set) и список (list).
    Использование set сомнительно, поскольку это неиндексируемая коллекция,
    поэтому при подготовке данных для pandas необходима конвертация в list,
    но при этом не гарантируется, что в списке элементы будут в том же
    порядке, в каком они были в множестве.
    Необходимо подумать о целесообразности изначального выбора в качестве
    коллекции списка и последующей проверке на каждой итерации наличия в нем
    дубликата добавляемого элемента
    """
    for filename in processed_data:
        if ".heic" in filename:
            continue
        splitted_filename = filename.split(root)
        parts_of_way = splitted_filename[-1].split("/")
        if handler:
            parts_of_way = list(map(handler, parts_of_way))
        model_folder = parts_of_way[-2]
        link_template = "catalog/suppliers/imperial"
        for subpath in range(len(parts_of_way)):
            link_template += "/{}"
        link = link_template.format(*parts_of_way)
        if model_folder not in data_template:
            # Если все же будет list, необходимо поменять тип данных здесь...
            # data_template[model_folder] = list()
            data_template[model_folder] = set()
        # ... и добавить проверку вхождения ссылки в обрабатываемый список
        # if link not in data_template[model_folder]:
        #    data_template[model_folder].append(link)
        # Мне это не нравится, потому что алгоритм становится квадратичной
        # сложности: каждый элемент списка сравнивается с другими элементами
        # списка эквивалентное длине списка раз
        data_template[model_folder].add(link)
    return data_template


# По большому счету, работа нашей программы по-настоящему начинается
# где-то здесь. Запишем время (просто по-приколу, замерим, сколько будет
# идти весь процесс)

start_day = datetime.now()
start_time = datetime.now()
message = (
    f"Работа начата {start_day.strftime(date_format)} "
    f"в {start_time.strftime(time_format)}"
)
logging.info(message)
print(message)

# Исходный файл, из которого мы возьмем артикулы,
# нам нужны его имя, лист и колонка (считается от нуля)

input_table_file = "work_table.xlsx"
sheet = "Лист1"
cols = [1]

# Читаем данные...
input_data = main.read_from_excel(input_table_file, sheet, cols)

# ... и забираем из них то, что нам нужно: список артикулов
# (если быть точным, то не список, а словарь, но это техническая деталь)
model = input_data["Характеристика"]

# Первоначально я пытался привязать ссылки на изображения к артикулам,
# как наиболее адекватным и уникальным значениям. Но столкнулся с тем,
# что формулировки и, что самое главное, оформление артикулов не совпадает
# с именами папок, поэтому сначала я утонул в информации и фактических дублях

# Сейчас будет попытка сократить работу по отлову и сопоставлению ссылок
# артикулам: мы сначала составим словарь настоящих артикулов и того,
# как эти артикулы могли бы выглядеть после преобразования текста,
# чтобы затем попробовать привязать ссылки к тому, как артикулы могли бы
# выглядеть после переименования. Идея в том, что после переименования
# артикулы более вероятно, что будут выглядеть, как названия папок


# Словарь: слева - недопустимые символы (и их комбинации), справа - то,
# на что их нужно заменить
# Настройка гибкая, здесь я их подобрал скорее эмпирически, полистав папки

replacement_patterns = {
    ". :": " ",
    " :": " ",
    "   ": " ",
    "  ": " ",
    " - ": "-",
    " -": "-",
    " ": "_",
    "/": "-",
    ":": "_",
    ", ": "_",
    ".": "_",
    ";": "_",
    "__": "_",
    "_-": "-",
    "'": "",
    ",": "",
    "²": "",
}

# Как видно, в расширении файлов тоже есть точка, которая не должна быть
# в основном имени файла. Поэтому мы перечислим типы файлов, которые у нас
# существуют в проекте (хотя бы примерный список), чтобы потом сказать
# программе, чтобы она вот эти кусочки имен не трогала

extensions = [
    ".jpg",
    ".heic",
    ".webm",
    ".jpeg",
    ".JPG",
    ".HEIC",
    ".JPEG",
    ".WEBM",
    ".PNG",
    ".png",
    ".webp",
    ".WEBP",
    ".bmp",
    ".BMP",
]

# Пожалуй здесь требуется какая-то ревизия кода что ли, потому что,
# ну, 2 partial? Серьезно? Не слишком ли сложно в данной ситуации?

partial_string_processor = partial(
    main.string_proceed_universal,
    replacements_dict=replacement_patterns,
    lower=True,
)

partial_string_cleaner = partial(
    main.process_string_except_extension,
    handler=partial_string_processor,
    extensions=extensions,
)

# Здесь у нас появятся артикулы транслитерированные в необходимый формат

proc_articles = {}
for name in model.values():
    proc_articles[name] = list()
    proc_articles[name].append(partial_string_cleaner(name))

# Это останется для готовых данных
prep_data = {}
for value in proc_articles.values():
    # Чуз ё файтер, как говорится (см. docstring к fill_table_with_links)
    prep_data[value[0]] = set()
    # prep_data[value] = list()

# Здесь мы укажем адрес папки со всеми фотографиями, в которой наша программа
# будет работать
root = "/home/nikita/Desktop/Медицинские оправы/"
# root = "/home/nikita/Desktop/Империал/imperial/opravy/"


# Соберем все имена файлов и папок, которые у нас есть
raw_directories, raw_files = main.collect_paths_from_tree(root, True)

# Конвертируем изображения в формат .jpg
converted_file_list = [
    (
        main.convert_image_to_jpg(file)
        if file.endswith(".heic")
        or file.endswith(".HEIC")
        or file.endswith(".webp")
        or file.endswith(".WEBP")
        or file.endswith(".bmp")
        or file.endswith(".BMP")
        or file.endswith(".tif")
        or file.endswith(".TIF")
        else file
    )
    for file in raw_files
]

# Заполним наши подготовленные данные (словарь, где ключи - обработанные
# от недопустимых символов артикулы

prepared_for_conversion = fill_table_with_links(
    converted_file_list, prep_data, partial_string_cleaner
)

"""
# Для того, чтобы корректно перенести данные в xlsx-файл, нам нужны заголовки
# наших будущих столбцов таблицы.
# Раньше я задавал их вручную.
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
# Я не ожидал, что в папке может быть так много файлов (в какой-то из папок
# их вообще штук 700 оказалось), поэтому вручную прописывать названия столбцов
# уже не получится, нужно автоматизированное решение

keys_list = []
for i in range(1000):
    keys_list.append(f"column no. {i}")

# Подготовим данные к записи в файл
main_data = main.prepare_data_for_pandas(prepared_for_conversion, keys_list)

articles_dict = main.prepare_data_for_pandas(
    proc_articles, ["Артикул", "Перевод"]
)

# Для удобства записи объединим их в один объект

main_data = {**articles_dict, **main_data}

# Запишем данные в файл. Имя будущего файла - тоже гибкая настройка,
# можно выбрать любое.
# Если быть точным, мы здесь выбираем не имя файла, а путь к нему, включая
# имя самого файла. Если файл существует, он будет перезаписан, если нет -
# создан.

main.write_to_excel(main_data, "imperial_optic_links_ver2.xlsx")

# Напоследок физически переименуем все папки и файлы, опять же, зачистив имена
# от недопустимых символов и грязи

main.rename_os_items(root, partial_string_cleaner, raw_directories, raw_files)

# Хотя функция и возвращает список переименованных директорий и файлов,
# Фактически результат работы этой нам не нужен. Данные, которые пойдут
# в таблицу, уже обработаны (очищены от запрещенных символов и приведены
# к требуемому "стандарту", скажем так (catalog/suppliers/imperial/ и т.д.))
# Поэтому заниматься фактическим переименованием директорий мы будем уже
# после того, как данные собраны и записаны в таблицу.

# Оставим себе сообщение, когда работа закончилась.
finish_day = datetime.now()
finish_time = datetime.now()
message = (
    f"Работа завершена {finish_day.strftime(date_format)} "
    f"в {finish_time.strftime(time_format)}. "
    f"Продолжительность работы составила {finish_time - start_time} "
    f"часов/минут/секунд."
)
logging.info(message)
print(message)
