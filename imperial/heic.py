import os

from main import read_from_excel, write_to_excel
from os import walk, system, path
from subprocess import run

root = f'{os.getcwd()}/opravy'
command = 'heif-convert -q 100 {} {}.jpg'

for cur_dir, subdirs, files in walk(root):
    print(os.getcwd())
    for file in files:
        if 'heic' in file:
            if os.getcwd() != path.abspath(cur_dir):
                os.chdir(path.abspath(cur_dir))
            #file = f'{path.abspath(cur_dir)}/{file}'
            result = run(command.format(file, file).split(), capture_output=True, text=True)
            print(result.stderr, result.stdout)
            os.chdir(root)
