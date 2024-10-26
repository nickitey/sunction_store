from main import read_from_excel
import requests
import sys
import logging

date_format = "%d/%m/%Y"
time_format = "%H:%M:%S"

logging.basicConfig(
    filemode="w",
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt=f"{date_format} {time_format}",
    filename="link_checker.log",
    encoding="utf-8",
    level=logging.INFO,
)


def link_checker(link):
    r = requests.get(link)
    allowed = ['application/octet-stream',
                'image/jpeg',
                'image/png',
                'image/webp',
                'image/tiff']
    return r.status_code == 200 and r.headers['Content-Type'] in allowed
    
    
def check_links_in_key(data_dict, key):
    work_dict = data_dict[key]
    counter = len(work_dict)
    std = 'https://storage.yandexcloud.net/sunction/'
    with open(rf'{key}.txt', 'w', encoding='UTF-8') as out:
        for subkey in work_dict:
            link = work_dict[subkey]
            msg = f'Я получил {link}, разбираюсь. Осталось {counter} элементов'
            print(msg)
            logging.info(msg)
            counter -= 1
            if isinstance(link, str):
                if link_checker(std + link):
                    msg = 'Все хорошо, тут есть картинка.'
                    print(msg)
                    logging.info(msg)
                    continue
                else:
                    msg = f'Непорядок c {link}. Запишем эти данные в файл'
                    logging.info(msg)
                    print(msg)
                    try:
                        out.write(link + '\n')
                        msg = f'Ссылка {link} записана в файл'
                        print(msg)
                        logging.info(msg)
                        continue
                    except UnicodeEncodeError:
                        msg = f'Что-то пошло не так с записью {link}, но мы сейчас разберемся'
                        logging.info(msg)
                        print(msg)
                        if '\u0301' in link:
                            if 'Berlin' in link:
                                msg = 'Опять этот Айс Берлин ебучий!'
                                logging.info(msg)
                                print(msg)
                                link = link.replace('\u0301', '')
                                out.write(link + ' здесь был знак ударения\n\n')
                            else:
                                msg = f'Это не Берлин, и записать я это не могу. Проблема с {link}'
                                logging.warning(msg)
                                print(msg)
                            continue
                        else:
                            raise UnicodeEncodeError
            else:
                msg = 'Упс, это не ссылка. Пропускаем.'
                logging.info(msg)
                print(msg)
            
        
    
file = r'C:\Users\Никита\Downloads\Telegram Desktop\imperial vision SUN.xlsx'
sheet = 'Готовый'
cols = range(94, 97)

data = read_from_excel(file, sheet, cols)
# dict_keys(['Фото. Основной ракурс', 'Фото. Фронтальынй ракурс', 'Фото. Допольнительный ракурс'])

keys = list(data.keys())

confirm = input(f'Колонки для обработки {keys}. Подтверждаете? ')

if confirm != 'yes':
    sys.exit()
    

for key in keys:
    check_links_in_key(data, key)
    if key != keys[-1]:
        msg = (f'Обработаны ссылки в колонке {key}. Продолжить? Введите yes,'
               ' чтобы продолжить, любую другую клавишу, чтобы прекратить выполнение '
               'программы. ')
        logging.info(f'Обработаны ссылки в колонке {key}. Спросил у пользователя, будем ли продолжать.')
        inp = input(msg)
        if inp == 'yes':
            logging.info('Пользователь ответил согласием.')
            print('Отлично, продолжаем!')
            continue
        else:
            logging.info('Пользователь ответил отказом.')
            print('Спасибо, что воспользовались услугами нашей авиакомпании.')
            sys.exit()
    else:
        msg = 'А на сегодня все. До новых встреч.'
        logging.info('Программа заканчивает работу.')
        print(msg)
