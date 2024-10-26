from main import read_from_excel, write_to_excel, nan


file = 'moscot_05_2024.xlsx'
sheet = 'sizes_raw'
cols = list(range(5))

content = read_from_excel(file, sheet, cols)
# dict_keys(['Артикул', 'lens', 'frame', 'bridge', 'temple'])

for key in content:
    if key != 'Артикул':
        for subkey in content[key]:
            value = content[key][subkey]
            if value == '-':
                content[key][subkey] = nan
                continue
            value = value.replace(' ', '')
            value = value.replace('\xa0', '')
            content[key][subkey] = int(value.strip('m\n'))


write_to_excel(content, 'moscot_sizes_python.xlsx')

