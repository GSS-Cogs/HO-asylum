import glob

py_files = [i for i in glob.glob('*.{}'.format('py'))]

for i in py_files:
    file = "'" + i + "'"
    if 'main' in file:
        pass
    %run $file
