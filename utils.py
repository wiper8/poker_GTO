import math
import random

import tqdm

def most_frequent(List):
    return max(set(List), key = List.count)

def expand_grid(a, b):
    return [[a, b] for i in a for j in b]


def combinaisons(list_n, k):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    pool = tuple(list_n)
    n = len(pool)
    if k > n:
        return
    indices = list(range(k))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(k)):
            if indices[i] != i + n - k:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, k):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)



def combins_all_k(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in combins_all_k(a[1:]):
        cs += [c, c+[a[0]]]
    return cs

def generate_all_community_from_hands(list_of_hands, community_size=5, deck = [
        "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH",
        "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS",
        "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
        "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC"
    ]):

    for hand in list_of_hands:
        for card in hand:
            deck.remove(card)

    res = [None] * math.comb(len(deck), community_size)
    for i, combin in tqdm.tqdm(enumerate(combinaisons(deck, community_size)), total=len(res)):
        res[i] = list(combin)

    return res

def generate_all_plays_from_my_hand(my_hand, nb_players=2, deck = [
        "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH",
        "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS",
        "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
        "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC"
    ], community_size=5):

    hand_size = len(my_hand)

    for card in my_hand:
        deck.remove(card)


    def recurse(deck, hands, number):
        if number > 0:
            for combin in combinaisons(deck, hand_size):
                # retirer les cartes des adversaires
                for c in combin:
                    deck.remove(c)
                hands.append(combin)
                hands = recurse(deck, hands, number - 1)[1]

                # remettre la carte dans le jeu
                for c in hands[-1]:
                    deck.append(c)
                # retirer la carte de la main
                hands = hands[:-1]
        else:
            for combin_commun in combinaisons(deck, community_size):
                res.append([hands, combin_commun].copy())

        return res, hands

    res = []

    return recurse(deck, [], nb_players - 1)[0]


def generate_some_plays_from_my_hand(my_hand, nb_players=2, n_plays = 1000, deck = [
        "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH",
        "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS",
        "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
        "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC"
    ], community_size=5):

    hand_size = len(my_hand)

    for card in my_hand:
        deck.remove(card)
    deck_og = deck.copy()

    random.shuffle(deck)

    res = []
    for i in range(n_plays):
        hands = []

        for p in range(nb_players-1):
            hands.append([deck[0], deck[1]])
            deck = deck[2:]
        deck = deck_og.copy()
        random.shuffle(deck)
        res.append([hands, deck[0:5]])

    return res
