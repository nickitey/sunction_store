import sys

sys.path.append("../imperial")

from main import test_data_dict

test_asset = {
    "IB-Boris N. :Black :Black-Clear Gradient :Flex ": [
        "-Boris N.",
        "Black",
        "Black-Clear Gradient",
        "Flex",
    ],
    "IB-Boris N. :Chrome :Black :BlackClear :Flex": [
        "-Boris N.",
        "Chrome",
        "Black",
        "BlackClear",
        "Flex",
    ],
    "IB-Boris N. :GunMetal :Black :BrownSand :Flex": [
        "-Boris N.",
        "GunMetal",
        "Black",
        "BrownSand",
        "Flex",
    ],
    "IB-Carla L. :Off-White :Warm Grey :Summerhaze :Flex": [
        "-Carla L.",
        "Off-White",
        "Warm Grey",
        "Summerhaze",
        "Flex",
    ],
}

output_example = {
    "title": {
        0: "IB-Boris N. :Black :Black-Clear Gradient :Flex ",
        1: "IB-Boris N. :Chrome :Black :BlackClear :Flex",
        2: "IB-Boris N. :GunMetal :Black :BrownSand :Flex",
        3: "IB-Carla L. :Off-White :Warm Grey :Summerhaze :Flex",
    },
    "first part": {
        0: "-Boris N.",
        1: "-Boris N.",
        2: "-Boris N.",
        3: "-Carla L.",
    },
    "second part": {0: "Black", 1: "Chrome", 2: "GunMetal", 3: "Off-White"},
    "third part": {
        0: "Black-Clear Gradient",
        1: "Black",
        2: "Black",
        3: "Warm Grey",
    },
    "fourth part": {
        0: "Flex",
        1: "BlackClear",
        2: "BrownSand",
        3: "Summerhaze",
    },
    "fifth part": {1: "Flex", 2: "Flex", 3: "Flex"},
}


def prepare_data_for_pandas(data, keys_list):

    def clear_empty_keys(dictionary):
        return {
            key: dictionary[key]
            for key in dictionary
            if len(dictionary[key]) != 0
        }

    data_keys = list(data.keys())
    prepared_data = {key: {} for key in keys_list}
    parameters_amount = len(data)
    for i in range(parameters_amount):
        prepared_data[keys_list[0]][i] = data_keys[i]
        for y in range(1, len(data[data_keys[i]]) + 1):
            prepared_data[keys_list[y]][i] = data[data_keys[i]][y - 1]
    return clear_empty_keys(prepared_data)


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

for_test = prepare_data_for_pandas(test_asset, target_keys)
test_data_dict(for_test, output_example)
