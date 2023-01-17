import math

from utils import *
import numpy as np
import tqdm
import random
import time

id_to_int = {
    "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "T":10, "J":11, "Q":12, "K":13, "A":14
}
int_to_id = {
    1:"A", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"T", 11:"J", 12:"Q", 13:"K", 14:"A"
}

def is_royal_flush(cards, color):
    if "A" + color in cards:
        if "K" + color in cards:
            if "Q" + color in cards:
                if "J" + color in cards:
                    if "T" + color in cards:
                        return True, [0]
    return False, 0


assert is_royal_flush(["JH", "9S", "QH", "TH", "6D", "AH", "KH"], "H")[0]
assert not is_royal_flush(["JH", "9S", "QH", "TH", "6D", "AH", "KD"], "H")[0]
assert not is_royal_flush(["JH", "9S", "QH", "TH", "6D", "9H", "KH"], "H")[0]


def is_straight_flush(cards, color):
    converted_cards = [id_to_int[c[0]] for c in cards if c[1] == color]
    if len(converted_cards) < 5:
        return False, 0
    converted_cards.sort()

    if converted_cards[-1] == 14 and converted_cards[-2] != 13:
        tmp = converted_cards[:-1]
        converted_cards = [1]
        converted_cards.extend(tmp)

    for i, j in zip(converted_cards[:-1], converted_cards[1:]):
        if j - i != 1:
            return False, 0
    return True, [max(converted_cards)]


assert is_straight_flush(["7H", "9S", "8H", "6H", "6D", "TH", "9H"], "H")[0]
assert is_straight_flush(["JH", "9S", "QH", "TH", "6D", "AH", "KH"], "H")[0]
assert not is_straight_flush(["7H", "9S", "8H", "6S", "6D", "TH", "9H"], "H")[0]
assert is_straight_flush(["5H", "9S", "3H", "4H", "6D", "AH", "2H"], "H")[0]
assert not is_straight_flush(["KH", "9S", "3H", "4H", "6D", "AH", "2H"], "H")[0]
assert is_straight_flush(["5H", "9S", "3H", "4H", "6D", "AH", "2H"], "H")[1][0] == 5

def is_quads(cards):
    cards = [id_to_int[c[0]] for c in cards]
    card = most_frequent([c for c in cards])
    quad = [c for c in cards if c == card]
    kicker = [c for c in cards if c != card]
    return len(quad) == 4, [int(card), max(kicker)]


assert is_quads(["5H", "9S", "2C", "2S", "6D", "2D", "2H"])[0]
assert not is_quads(["5H", "9S", "2C", "3S", "6D", "2D", "2H"])[0]
assert is_quads(["5H", "9S", "2C", "2S", "6D", "2D", "2H"])[1][0] == 2
assert is_quads(["5H", "9S", "2C", "2S", "6D", "2D", "2H"])[1][1] == 9


def is_full_house(cards):
    tmp = [c[0] for c in cards]
    freq = {c: tmp.count(c) for c in tmp}
    trips = []
    for k, v in freq.items():
        if v == 3:
            trips.append(id_to_int[k])

    if len(trips) == 0:
        return False, 0

    trips = max(trips)

    # reste 4 cartes avec soit un trip, un/deux doubles ou que des unitaires
    reste = [id_to_int[c[0]] for c in tmp if id_to_int[c[0]] != trips]

    best_pair = 0
    for i in range(3):
        for j in range(i+1, 3):
            if reste[i] == reste[j]:
                best_pair = max(best_pair, reste[i])

    if best_pair == 0:
        return False, 0

    return True, [trips, best_pair]

assert is_full_house(["7S", "8H", "6D", "7H", "6S", "6C", "TC"])[0]
assert is_full_house(["7S", "8H", "6D", "7H", "6S", "6C", "7C"])[0]
assert not is_full_house(["7S", "8H", "6D", "7H", "6S", "9C", "3C"])[0]
assert not is_full_house(["7S", "8H", "6D", "7H", "KS", "2C", "7C"])[0]
assert is_full_house(["7S", "8H", "6D", "7H", "6S", "6C", "7C"])[1] == [7, 6]

def is_flush(cards, color):
    cards_of_the_color = [id_to_int[c[0]] for c in cards if c[1] == color]
    if len(cards_of_the_color) <= 4:
        return False, 0
    cards_of_the_color.sort(reverse=True)
    return True, cards_of_the_color[:5]


assert is_flush(["JH", "9S", "QH", "TH", "6D", "AH", "KH"], "H")[0]
assert is_flush(["JH", "7S", "QH", "TH", "6D", "5H", "KH"], "H")[0]
assert not is_flush(["JH", "7S", "QC", "TH", "6D", "5H", "KH"], "H")[0]
assert is_flush(["JH", "7S", "QH", "TH", "6D", "5H", "KH"], "H")[1] == [13, 12, 11, 10, 5]
assert is_flush(["2C", "3C", "TC", "4C", "KC", "JC", "8C"], "C")[1] == [13, 11, 10, 8, 4]

def is_straight(cards):
    converted_cards = list(set([id_to_int[c[0]] for c in cards]))

    if len(converted_cards) < 5:
        return False, 0
    converted_cards.sort()

    if converted_cards[-1] == 14 and converted_cards[0] == 2 and converted_cards[1] == 3 and converted_cards[2] == 4 and converted_cards[3] == 5:
        tmp = converted_cards[:-1]
        converted_cards = [1]
        converted_cards.extend(tmp)

    diffs = [None] * (len(converted_cards) - 1)
    for k in range(len(converted_cards)-1):
        diffs[k] = converted_cards[1:][k] - converted_cards[:-1][k]

    conseq = 0

    for d in diffs:
        if d == 1:
            conseq += 1
        else:
            conseq = 0
        if conseq >= 4:
            if conseq == 4:
                if diffs[-1] == 1 and diffs[-2] == 1:
                    return True, [converted_cards[-1]]
                if diffs[-1] == 1:
                    return True, [converted_cards[-3]]
                if diffs[-2] == 1:
                    return True, [converted_cards[-2]]
                return True, [converted_cards[-3]]

            if conseq == 5:
                if diffs[-1] == 1:
                    return True, [converted_cards[-1]]
                return True, [converted_cards[-2]]

            if conseq == 6:
                return True, [max(converted_cards)]

    return False, 0


assert is_straight(["7H", "9S", "8H", "6H", "6D", "TH", "9H"])[0]
assert is_straight(["JH", "9S", "QH", "TH", "6D", "AH", "KH"])[0]
assert is_straight(["7H", "9S", "8H", "6S", "6D", "TH", "9H"])[0]
assert is_straight(["5H", "9S", "3H", "4H", "KD", "AH", "2H"])[0]
assert not is_straight(["KH", "9S", "3H", "4H", "6D", "AH", "2H"])[0]
assert not is_straight(["KH", "9S", "3H", "4H", "4D", "6H", "5H"])[0]
assert is_straight(["5H", "9S", "3H", "4H", "KD", "AH", "2H"])[1] == [5]
assert is_straight(["5H", "6S", "3H", "4H", "KD", "AH", "2H"])[1] == [6]
assert is_straight(["7H", "8S", "5H", "6H", "9D", "3H", "4H"])[1] == [9]

def is_set(cards):
    tmp = [c[0] for c in cards]
    freq = {c: tmp.count(c) for c in tmp}
    trips = []
    for k, v in freq.items():
        if v == 3:
            trips.append(id_to_int[k])

    if len(trips) == 0:
        return False, 0

    trips = max(trips)
    reste = [id_to_int[c[0]] for c in tmp if c != trips]
    reste.sort()
    return True, [trips, reste[-1], reste[-2]]


assert is_set(["7S", "8H", "6D", "7H", "6S", "6C", "TC"])[0]
assert is_set(["7S", "8H", "6D", "7H", "6S", "6C", "7C"])[0]
assert is_set(["AS", "8H", "6D", "7H", "6S", "6C", "KC"])[0]
assert not is_set(["7S", "8H", "6D", "7H", "6S", "9C", "3C"])[0]
assert is_set(["AS", "8H", "6D", "7H", "6S", "6C", "KC"])[1] == [6, 14, 13]

def is_two_pairs(cards):
    tmp = [c[0] for c in cards]
    freq = {c: tmp.count(c) for c in tmp}
    pairs = []
    for k, v in freq.items():
        if v == 2:
            pairs.append(id_to_int[k])

    if len(pairs) >= 2:
        pair1 = max(pairs)

        reste = [id_to_int[c[0]] for c in tmp if c[0] != int_to_id[pair1]]
        pairs = []
        freq = {id_to_int[c[0]]: reste.count(id_to_int[c[0]]) for c in tmp}

        for k, v in freq.items():
            if v == 2:
                pairs.append(k)
        pair2 = max(pairs)

        reste = [c for c in reste if c != pair2]
        return True, [pair1, pair2, reste[0]]
    return False, 0


assert is_two_pairs(["7S", "8H", "6D", "7H", "TS", "6C", "TC"])[0]
assert is_two_pairs(["7S", "8H", "6D", "7H", "6S", "2C", "5C"])[0]
assert not is_two_pairs(["7S", "8H", "2D", "7H", "6S", "9C", "3C"])[0]
assert is_two_pairs(["7S", "8H", "6D", "7H", "6S", "2C", "5C"])[1] == [7, 6, 8]

def is_pair(cards):
    tmp = [c[0] for c in cards]
    freq = {c: tmp.count(c) for c in tmp}
    pairs = []
    for k, v in freq.items():
        if v == 2:
            pairs.append(id_to_int[k])

    if len(pairs) == 1:
        pair1 = max(pairs)

        kickers = [id_to_int[c[0]] for c in tmp if c != int_to_id[pair1]]
        kickers.sort()

        return True, [pair1, kickers[-1], kickers[-2], kickers[-3]]
    return False, 0


assert is_pair(["7S", "8H", "6D", "7H", "TS", "AC", "KC"])[0]
assert not is_pair(["7S", "8H", "2D", "5H", "6S", "9C", "3C"])[0]
assert is_pair(["7S", "8H", "6D", "7H", "TS", "AC", "KC"])[1] == [7, 14, 13, 10]

def is_high(cards):
    tmp = [id_to_int[c[0]] for c in cards]
    tmp.sort()
    return True, [tmp[-1], tmp[-2], tmp[-3], tmp[-4], tmp[-5]]

assert is_high(["7S", "8H", "6D", "2H", "TS", "AC", "KC"])[1] == [14, 13, 10, 8, 7]

def find_hand(cards):
    col = most_frequent([c[1] for c in cards])

    tmp = is_straight(cards)
    if tmp[0]:
        tmp2 = is_straight_flush(cards, col)
        if tmp2[0]:
            tmp3 = is_royal_flush(cards, col)
            if tmp3[0]:
                return 9, tmp2[1]
            return 8, tmp2[1]
        return 4, tmp[1]

    tmp = is_flush(cards, col)
    if tmp[0]:
        return 5, tmp[1]

    tmp = is_full_house(cards)
    if tmp[0]:
        return 6, tmp[1]

    tmp = is_pair(cards)
    if tmp[0]:
        return 1, tmp[1]

    tmp = is_quads(cards)
    if tmp[0]:
        return 7, tmp[1]

    tmp = is_set(cards)
    if tmp[0]:
        return 3, tmp[1]

    tmp = is_two_pairs(cards)
    if tmp[0]:
        return 2, tmp[1]

    tmp = is_high(cards)
    return 0, tmp[1]

assert find_hand(["JH", "9S", "QH", "TH", "6D", "AH", "KH"])[0] == 9
assert find_hand(["7H", "9S", "8H", "6H", "6D", "TH", "9H"])[0] == 8
assert find_hand(["5H", "9S", "2C", "2S", "6D", "2D", "2H"])[0] == 7
assert find_hand(["7S", "8H", "6D", "7H", "6S", "6C", "7C"])[0] == 6
assert find_hand(["7S", "8H", "6D", "7H", "6S", "6C", "TC"])[0] == 6
assert find_hand(["JH", "7S", "QH", "TH", "6D", "5H", "KH"])[0] == 5
assert find_hand(["2C", "3C", "TC", "4C", "KC", "JC", "8C"])[0] == 5
assert find_hand(["7H", "9S", "8H", "6H", "6D", "TH", "9C"])[0] == 4
assert find_hand(["7H", "9S", "8H", "6S", "6D", "TH", "9C"])[0] == 4
assert find_hand(["5H", "9S", "3H", "4H", "KD", "AH", "2C"])[0] == 4
assert find_hand(["7S", "8H", "6D", "QH", "6S", "6C", "TC"])[0] == 3
assert find_hand(["7S", "8H", "6D", "QH", "6S", "6C", "KC"])[0] == 3
assert find_hand(["AS", "8H", "6D", "QH", "6S", "6C", "KC"])[0] == 3
assert find_hand(["7S", "8H", "6D", "7H", "TS", "6C", "TC"])[0] == 2
assert find_hand(["7S", "8H", "6D", "7H", "6S", "2C", "5C"])[0] == 2
assert find_hand(["7S", "8H", "6D", "7H", "TS", "AC", "KC"])[0] == 1
assert find_hand(["7S", "8H", "6D", "2H", "TS", "AC", "KC"])[0] == 0

#pour mesurer la vitesse de find_hand
#start=time.time()
#for i in range(10000):
#    find_hand(["AC", "TD", "6C", "6H", "2S", "3C", "4C"])
#print(time.time() - start)


def determining_winning_hand(list_of_hands, community):
    #liste de listes de 2

    for hand in list_of_hands:
        hand.extend(community)

    result = [None] * len(list_of_hands)

    for i in range(len(list_of_hands)):
        result[i] = find_hand(list_of_hands[i])

    count = 0
    best_level = max([res[0] for res in result])
    for res in result:
        if res[0] == best_level:
            count += 1
    if count == 1:
        return [np.argmax([res[0] for res in result])]

    result = [[i, hand] for i, hand in enumerate(result)]

    #egalite
    best_hands = []
    for i in range(len(result)):
        if result[i][1][0] == best_level:
            best_hands.append(result[i])
    try:
        len(best_hands[0][1][1])
    except:
        print(best_hands)
    for j in range(len(best_hands[0][1][1])):
        tmp = [hand[1][1][j] for hand in best_hands]
        freq = {c: tmp.count(c) for c in tmp}
        tmp = list(freq.keys())
        tmp.sort()
        best_hands = [hand for hand in best_hands if hand[1][1][j] == tmp[-1]]

        if len(best_hands) == 1:
            return [best_hands[0][0]]

    #il faut split le pot
    return [h[0] for h in best_hands]


assert determining_winning_hand([["AS", "JS"], ["KH", "4D"]], ["5H", "AH", "7D", "8H", "8C"]) == [0]
assert determining_winning_hand([["AS", "JS"], ["AC", "4C"], ["KH", "4D"]], ["5H", "AH", "7D", "8H", "8C"]) == [0]
assert determining_winning_hand([["AC", "4C"], ["AS", "JS"], ["KH", "4D"]], ["5H", "AH", "7D", "8H", "8C"]) == [1]
assert determining_winning_hand([["AC", "4C"], ["AS", "4S"], ["KH", "4D"]], ["5H", "AH", "7D", "8H", "8C"]) == [0, 1]
assert determining_winning_hand([["KH", "4D"], ["AC", "4C"], ["AS", "4S"]], ["5H", "AH", "7D", "8H", "8C"]) == [1, 2]
assert determining_winning_hand([["AC", "4C"], ["AS", "4S"], ["AD", "4D"]], ["5H", "AH", "7D", "8H", "8C"]) == [0, 1, 2]
assert determining_winning_hand([["2C", "3C"], ["KS", "3H"]], ["TC", "4C", "KC", "JC", "8C"]) == [0, 1]


def generate_13x13_pairs():
    # grouper les suited et off-suit
    possible_hands = []
    # utilisons uniquement le pique et le coeur pour simplifier par 12 les combinaisons (si j'ai TC, 7D, on n'aurait qu'à échanger C pour S et D pour H)
    tmp1 = ["AS", "KS", "QS", "JS", "TS", "9S", "8S", "7S", "6S", "5S", "4S", "3S", "2S"]
    tmp2 = ["AH", "KH", "QH", "JH", "TH", "9H", "8H", "7H", "6H", "5H", "4H", "3H", "2H"]
    for i in range(len(tmp1)):
        for j in range(i, len(tmp2)):
            possible_hands.append([tmp1[i], tmp2[j]])

    possible_hands.extend(generate_all_community_from_hands([], 2,
                                                            ["AS", "KS", "QS", "JS", "TS", "9S", "8S", "7S", "6S", "5S",
                                                             "4S", "3S", "2S"]))
    # on a donc tous les combins de notre grille 13x13
    return possible_hands
