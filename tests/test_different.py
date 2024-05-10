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
    count = 0
    prepared_data = {}
    for key in keys_list:
        prepared_data[key] = {}
    for i in range(len(data)):
        prepared_data[keys_list[0]][i] = keys_list[0]
        for y in range(1, len(data[keys_list[i]])):
            try:
                data[keys_list[i][y]][i] = lc_berlin[lc_berlin_keys[i]][0]
                to_write["second part"][i] = lc_berlin[lc_berlin_keys[i]][1]
                to_write["third part"][i] = lc_berlin[lc_berlin_keys[i]][2]
                to_write["fourth part"][i] = lc_berlin[lc_berlin_keys[i]][3]
                to_write["fifth part"][i] = lc_berlin[lc_berlin_keys[i]][4]
                to_write["sixth part"][i] = lc_berlin[lc_berlin_keys[i]][5]
                to_write["seventh part"][i] = lc_berlin[lc_berlin_keys[i]][6]
                to_write["eighth part"][i] = lc_berlin[lc_berlin_keys[i]][7]
            except IndexError:
                print(
                    f"{count}: Elements in {lc_berlin_keys[i]} have run out."
                )
                count += 1
                continue
