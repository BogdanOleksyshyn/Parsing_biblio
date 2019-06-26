import glob
from functools import partial
import json
from multiprocessing.dummy import Pool
import csv
import re

def main():
    columns = [['word','examples','alternative']]

    with open('examples.json', 'r') as f:
        result = json.load(f)

    books = 'books'
    all_files = [f for f in glob.glob(books + "**/*.txt", recursive=True)]
    all_files = [all_files[i] for i in range(500)]
    rows = [get_data_for_csv(word, result, all_files) for word in result]
    for row in rows:
        columns.append(row)
    add_to_csv(columns, 'dictionary.csv')


def find_patterns(text, word):
    for_examples = f"(\s*[\w\d]+)([(),\s\w\d\-\%\$]*)\s([\w\d]+)(\s*{word}\s*)([\w\d]+)([(),\s\w\d\-\%\$]*[.\?!])"
    try:
        res = re.findall(for_examples, text)
        if res != []:
            for i in range(len(res)):
                pattern = (res[i][2], res[i][4])
                if pattern:
                    return pattern
    except TypeError:
        pass


def add_to_csv(data, path):
    """
    Write data to a CSV file path
    """
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=':')
        for line in data:
            writer.writerow(line)


def get_data_for_csv(word, result, all_files):
    patterns = [find_patterns(example, word) for example in result[word]['examples'] if find_patterns(example, word) is not None]
    f = partial(find_examples, patterns)
    pool = Pool(200)
    results = pool.map(f, all_files)
    for_row = []
    for res in results:
        if res != []:
            for i in res:
                for_row.append(i)
    row = [word, result[word]['examples'], for_row]
    return row


def find_examples(patterns, file):
    try:
        with open(file, 'r') as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(file, 'rb') as f:
            text = f.read()

    alternatives = []
    for pattern in patterns:
        for_alternatives = f'([A-Z][\w\d\s]+([\s]+{pattern[0]}\s+(\w+)\s+{pattern[1]}[\s]+)[\w\d\s]+[.?!])'
        try:
            result = re.findall(for_alternatives, text)
            if result != []:
                alternatives.append(result[0])
            else:
                pass
        except TypeError:
            pass

    print(f'check {file}')
    return alternatives

if __name__ == '__main__':
    main()
