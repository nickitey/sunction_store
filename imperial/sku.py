import math

from main import read_from_excel, write_to_excel

file = 'Imperial_optic_fin.xlsx'
sheet = 'SKU_SLUG'
cols = list(range(2))


data = read_from_excel(file, sheet, cols)
# dict_keys(['Артикул', 'Бренд'])


def remove_and_glue(str1, str2):
    if isinstance(str2, float):
        if math.isnan(str2):
            return ''.join(str1.split()).replace('™', '')
    try:
        return ''.join(str1.split()).replace('™', '') + str(int(str2))
    except ValueError:
        return ''.join(str1.split()).replace('™', '') + str(str2)


def prepare_slug(str1, str2):
    return ('-'.join([str1.lower(), str2.lower()]).replace(' ', '-')
            .replace('/', '-').replace('™', ''))


skus = {i: remove_and_glue(data['Артикул'][i], "")
        for i in data['Артикул'].keys()}

slugs = {i: prepare_slug(data['Бренд'][i], data['Артикул'][i])
         for i in data['Артикул'].keys()}

to_write = {**data, 'SKU': skus, 'чпу ссылка': slugs}


write_to_excel(to_write, 'imperial_sku_and_slug_python.xlsx')

