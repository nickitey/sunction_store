from main import (
    read_from_excel,
    write_to_excel,
    split_and_clean_strings,
    prepare_data_for_pandas,
)

file = r"Наличие склада на 16.01.2024 .xlsx"
sheet = "Лист2"
cols = list(range(3))

data = read_from_excel(file, sheet, cols)

# dict_keys(['Бренд', 'Вид', 'Характеристика'])
brand = data["Бренд"]
product_type = data["Вид"]
specs = data["Характеристика"]


lc_berlin = {
    specs[i]: split_and_clean_strings(specs[i], ":", "IB ", "")
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
