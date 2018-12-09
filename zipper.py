import zipfile

words_apkg = zipfile.ZipFile('words.apkg', 'r')
files = words_apkg.filelist
for file in files:
    print(file.filename)
words_apkg.extractall()
###

###
with zipfile.ZipFile('words.apkg', 'w') as myzip:
    for file in files[:-1]:
        myzip.write(file.filename)

