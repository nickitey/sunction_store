import pandas as pd
import math

nan = float('nan')


def read_from_excel(path, sheet, cols):
    xl = pd.ExcelFile(path)
    dataframe = pd.read_excel(xl, sheet, usecols=cols)
    return dataframe.to_dict()


def write_to_excel(data_dict, path, sheet='python'):
    to_write_db = pd.DataFrame.from_dict(data_dict)
    to_write_db.to_excel(path, sheet_name=sheet)


def test_data_dict(data_dict, test_asset):
    def compare_details(item1, item2):
        if isinstance(item1, float) and isinstance(item2, float):
            if not (math.isnan(item1) and math.isnan(item2)):
                print('nan and nan')
                return False
            return True
        elif isinstance(item1, list) and isinstance(item2, list):
            if len(item1) != len(item2):
                print('different length')
                return False
            for i in range(len(item1)):
                if isinstance(item1[i], float) and isinstance(item2[i], float):
                    if not (math.isnan(item1[i]) and math.isnan(item2[i])):
                        print('nan and nan in list')
                        return False
                elif item1[i] != item2[i]:
                    print('different elements in list')
                    print(type(item1[i]), type(item2[i]))
                    print(item1[i], item2[i])
                    return False
        else:
            print('different types')
            return False
        return True

    test_status = True
    for item in test_asset:
        try:
            checker = test_asset[item]
            checked = data_dict[item]
        except KeyError:
            print(f'Test failed with {item}.')
            print(f'Key {item} is absent in tested dictionary.')
            return False
        try:
            assert checker == checked
        except AssertionError:
            if compare_details(checker, checked):
                continue
            test_status = False
            print(f'Test failed with {item}.')
            print(f'Expected: {test_asset[item]}, '
                  f'type - {type(test_asset[item])}.')
            print(f"Received: {data_dict[item]}, "
                  f"type - {type(data_dict[item])}.")
    if test_status:
        print("All tests passed")
    return test_status
