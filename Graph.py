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


def find_profit(hand):
    pot = re.findall(r'Hero collected \$(\d*)\.?(\d+|\d+) from pot', hand)
    return str_to_float(pot[0])


def find_rake(hand):
    rake = re.findall(r'\| Rake \$(\d*)\.?(\d+|\d+) \|', hand)
    return str_to_float(rake[0])


def find_uncalled_bet(hand):
    uncalled_bet = re.findall('Uncalled bet \(\$(\d*)\.?(\d+|\d+)\) returned to Hero', hand)
    return str_to_float(uncalled_bet[0])


def find_jackpot(hand):
    rakeback = re.findall('\| Jackpot \$(\d*)\.?(\d+|\d+) \|', hand)
    return str_to_float(rakeback[0])


def get_date(file_name):
    return file_name[2:10]


def get_time(hand):
    time = re.findall('- \d+/\d+/\d+ ([0-9:]+)\nTable', hand)
    return time


def merge_hand_lists(list1, list2):
    i = 0
    j = 0
    new_list = []
    while i < len(list1) and j < len(list2):
        time1 = get_time(list1[i])[0]
        time2 = get_time(list2[j])[0]
        if time1 < time2:
            new_list.append(list1[i])
            i += 1
        else:
            new_list.append(list2[j])
            j += 1

    if i < len(list1):
        new_list += list1[i:]
    else:
        new_list += list2[j:]
    return new_list


def analyze_hands(base_dir, start_time, end_time, win_with_showdown, win_without_showdown, total, total_after_rake):
    session_list = os.listdir(base_dir)
    session_list.sort()

    i = 0
    while i < len(session_list):
        _, file_extension = os.path.splitext(base_dir + session_list[i])
        if file_extension != '.txt':
            del session_list[i]
        else:
            i += 1

    slow = 0
    while slow < len(session_list):
        file_name = session_list[slow]

        date = get_date(file_name)
        if len(start_time) > 0 and date < start_time:
            slow += 1
            continue
        if len(end_time) > 0 and date > end_time:
            return

        f = open(base_dir + file_name, "r")
        hand_list = list(reversed(f.read().split('Poker Hand #')[1:]))
        fast = slow + 1
        while fast < len(session_list) and get_date(session_list[fast]) == date:
            new_hand_list = list(reversed(open(base_dir + session_list[fast], "r").read().split('Poker Hand #')[1:]))
            hand_list = merge_hand_lists(hand_list, new_hand_list)
            fast += 1
        slow = fast

        for hand in hand_list:
            if len(hand) == 0:
                continue

            extend_list(win_with_showdown)
            extend_list(win_without_showdown)
            extend_list(total)
            extend_list(total_after_rake)
            cur = len(total) - 1

            win = re.search('Hero', hand.split('SHOWDOWN ***')[1].split('*** SUMMARY ***')[0]) is not None
            is_showdown = re.search('Hero \(?[a-z]* ?[a-z]*\)? ?showed \[',
                                 hand.split('*** SUMMARY ***')[1]) is not None

            casualty = 0
            casualty += find_blind(hand)
            casualty += find_bet(hand)
            casualty += find_call(hand)
            casualty += find_raise(hand)

            total[cur] -= casualty
            total_after_rake[cur] -= casualty
            if is_showdown:
                win_with_showdown[cur] -= casualty
            else:
                win_without_showdown[cur] -= casualty

            if win:
                rake = find_rake(hand)
                showdown = hand.split('*** SHOWDOWN ***')[1].split('*** SUMMARY ***')[0]
                jackPot = find_jackpot(hand)
                profit = find_profit(showdown) + rake + jackPot
                if is_showdown:
                    win_with_showdown[cur] += profit
                else:
                    profit += find_uncalled_bet(hand)
                    win_without_showdown[cur] += profit
                total[cur] += profit
                total_after_rake[cur] += profit - rake - jackPot


def draw_graph(win_with_showdown, win_without_showdown, total, total_after_rake):
    x = range(len(total))
    vert = [0] * len(total)
    plt.plot(x, total, color='g', label='Net won')
    plt.plot(x, total_after_rake, color='yellow', label='Net won (after rake)')
    plt.plot(x, win_with_showdown, color='b', label='Won with showdown')
    plt.plot(x, win_without_showdown, color='r', label='Won without showdown')
    plt.plot(x, vert, color='black')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    win_with_showdown = [0.0]
    win_without_showdown = [0.0]
    total = [0.0]
    total_after_rake = [0.0]
    analyze_hands('', '', win_with_showdown,
                  win_without_showdown, total,
                  total_after_rake)
    draw_graph(win_with_showdown, win_without_showdown, total, total_after_rake)
