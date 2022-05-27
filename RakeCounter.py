import os
import re


def count():
    rake = 0

    base_dir = ''
    for folder_name in os.listdir(base_dir):
        if not os.path.isdir(base_dir + folder_name):
            continue

        for file_name in os.listdir(base_dir + folder_name):
            f = open(base_dir + folder_name + '/' + file_name, "r")
            content = f.read().split('Poker Hand #')

            for hand in content:
                result = re.search('Hero \([A-Za-z][A-Za-z\s]*\) collected', hand)
                if result is None:
                    result = re.search('Hero \([A-Za-z][A-Za-z\s]*\) won', hand)
                if result is None:
                    result = re.search('Hero \([A-Za-z][A-Za-z\s]*\) showed \[[A-Za-z1-9\s]*\] and won', hand)

                if result is None:
                    continue

                rakeStr = re.findall(r'Rake \$(.*) \| Jackpot', hand)
                rake += float(rakeStr[0])

    return rake


if __name__ == '__main__':
    print(count())
