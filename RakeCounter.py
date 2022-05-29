import os
import re


def count():
    rake = 0

    base_dir = '/Users/zhangyunxuan/myshit/扑克/handData/'

    for file_name in os.listdir(base_dir):
        _, file_extension = os.path.splitext(base_dir + file_name)
        if file_extension != '.txt':
            continue

        f = open(base_dir + file_name, "r")
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
