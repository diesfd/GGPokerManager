import os
import re


def extend_list(nums):
    nums.append(nums[len(nums) - 1])


def find_blind(hand):
    blinds = re.findall(r'Hero: posts [a-z]+ blind \$(\d+).(\d+)', hand)
    result = 0
    for i in blinds:
        result += float(i[0]) + float(i[1]) * 0.01
    return result


def find_bet(hand):
    bets = re.findall(r'Hero: bets \$(\d+).(\d+)', hand)
    result = 0
    for i in bets:
        result += float(i[0]) + float(i[1]) * 0.01
    return result


def find_call(hand):
    calls = re.findall(r'Hero: calls \$(\d+).(\d+)', hand)
    result = 0
    for i in calls:
        result += float(i[0]) + float(i[1]) * 0.01
    return result


def find_raise(hand):
    raises = re.findall(r'Hero: raises \$(\d+).(\d+) to \$(\d+).(\d+)', hand)
    result = 0
    for i in raises:
        result += float(i[2]) + float(i[3]) * 0.01
    return result


def analyze_hands(base_dir, win_with_showdown, win_without_showdown, total):
    for folder_name in os.listdir(base_dir):
        if not os.path.isdir(base_dir + folder_name):
            continue

        for file_name in os.listdir(base_dir + folder_name):
            f = open(base_dir + folder_name + '/' + file_name, "r")
            content = f.read().split('Poker Hand #')

            for hand in content:
                extend_list(win_with_showdown)
                extend_list(win_without_showdown)
                extend_list(total)

                win = re.search('Hero', hand.split('*** SHOWDOWN ***')[1].split('*** SUMMARY ***')[0]) is not None
                showdown = re.search('showed', hand.split('*** SUMMARY ***')[1]) is not None

                if win:
                    potStr = re.findall(r'Total pot \$(.*) \| Rake')
                    pot = float(potStr[0])
                    if showdown:
                        win_with_showdown[len(win_with_showdown) - 1] += pot
                    else:
                        win_without_showdown[len(win_without_showdown) - 1] += pot
                    total[len(total) - 1] += pot

                else:
                    casualty = 0
                    casualty += find_blind(hand)
                    casualty += find_bet(hand)
                    casualty += find_call(hand)
                    casualty += find_raise(hand)

                    if showdown:
                        win_with_showdown[len(win_with_showdown) - 1] -= casualty
                    else:
                        win_without_showdown[len(win_without_showdown) - 1] -= casualty
                    total[len(total) - 1] -= casualty

def draw_graph(win_with_showdown, win_without_showdown, total):


if __name__ == '__main__':
    win_with_showdown = [0]
    win_without_showdown = [0]
    total = [0]
    analyze_hands('/Users/zhangyunxuan/myshit/扑克/handData', win_with_showdown, win_without_showdown, total)
    draw_graph(win_with_showdown, win_without_showdown, total)
