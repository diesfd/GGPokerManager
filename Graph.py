import os
import re
import matplotlib.pyplot as plt


def extend_list(nums):
    nums.append(nums[len(nums) - 1])


def str_to_float(s):
    if len(s[0]) == 0:
        if len(s[1]) == 0:
            return 0
        return float(s[1])
    else:
        offset = len(s[1])
        return float(s[0]) + float(s[1]) / pow(10, offset)


def find_blind(hand):
    blinds = re.findall(r'Hero: posts [a-z]+ blind \$(\d*).?(\d+|\d+)', hand)
    result = 0
    for i in blinds:
        result += str_to_float(i)
    return result


def find_bet(hand):
    bets = re.findall(r'Hero: bets \$(\d*).?(\d+|\d+)', hand)
    result = 0
    for i in bets:
        result += str_to_float(i)
    return result


def find_call(hand):
    calls = re.findall(r'Hero: calls \$(\d*).?(\d+|\d+)', hand)
    result = 0
    for i in calls:
        result += str_to_float(i)
    return result


def find_raise(hand):
    raises = re.findall(r'Hero: raises \$(\d*)\.?(\d+|\d+) to \$(\d*)\.?(\d+|\d+)', hand)
    result = 0
    for i in raises:
        result += str_to_float(i[2:])
    return result


def find_pot(hand):
    pot = re.findall(r'Total pot \$(\d*)\.?(\d+|\d+) \| Rake', hand)
    return str_to_float(pot[0])


def find_rake(hand):
    rake = re.findall(r'\| Rake \$(\d*)\.?(\d+|\d+) \|', hand)
    return str_to_float(rake[0])


def find_uncalled_bet(hand):
    uncalled_bet = re.findall('Uncalled bet \(\$(\d*)\.?(\d+|\d+)\) returned to Hero', hand)
    return str_to_float(uncalled_bet[0])


def get_time(file_name):
    return file_name[2:10]


def analyze_hands(base_dir, start_time, end_time, win_with_showdown, win_without_showdown, total, total_after_rake):
    session_list = os.listdir(base_dir)
    session_list.sort()
    for file_name in session_list:
        _, file_extension = os.path.splitext(base_dir + file_name)
        if file_extension != '.txt':
            continue

        time = get_time(file_name)
        if len(start_time) > 0 and time < start_time:
            continue
        if len(end_time) > 0 and time > end_time:
            return

        f = open(base_dir + file_name, "r")
        content = f.read().split('Poker Hand #')

        for hand in content:
            if len(hand) == 0:
                continue

            extend_list(win_with_showdown)
            extend_list(win_without_showdown)
            extend_list(total)
            extend_list(total_after_rake)
            cur = len(total) - 1

            win = re.search('Hero', hand.split('SHOWDOWN ***')[1].split('*** SUMMARY ***')[0]) is not None
            showdown = re.search('Hero \(?[a-z]* ?[a-z]*\)? ?showed \[',
                                 hand.split('*** SUMMARY ***')[1]) is not None

            casualty = 0
            casualty += find_blind(hand)
            casualty += find_bet(hand)
            casualty += find_call(hand)
            casualty += find_raise(hand)

            total[cur] -= casualty
            total_after_rake[cur] -= casualty
            if showdown:
                win_with_showdown[cur] -= casualty
            else:
                win_without_showdown[cur] -= casualty

            if win:
                rake = find_rake(hand)
                pot = find_pot(hand)
                if showdown:
                    win_with_showdown[cur] += pot
                else:
                    pot += find_uncalled_bet(hand)
                    win_without_showdown[cur] += pot
                total[cur] += pot
                total_after_rake[cur] += pot - rake


def draw_graph(win_with_showdown, win_without_showdown, total, total_after_rake):
    x = range(len(total))
    plt.plot(x, total, color='g', label='Net won')
    plt.plot(x, total_after_rake, color='yellow', label='Net won (after rake)')
    plt.plot(x, win_with_showdown, color='b', label='Won with showdown')
    plt.plot(x, win_without_showdown, color='r', label='Won without showdown')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    win_with_showdown = [0.0]
    win_without_showdown = [0.0]
    total = [0.0]
    total_after_rake = [0.0]
    analyze_hands('#dir', '20220511', '20220517', win_with_showdown,
                  win_without_showdown, total,
                  total_after_rake)
    draw_graph(win_with_showdown, win_without_showdown, total, total_after_rake)
