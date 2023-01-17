import numpy as np
from utils import *

#probabilités de Win/Split/loss (et proxy de l'equity (force de la main)) si tous jouaient toujours leurs mains.

NB_PLAYERS = 3
POSSIBLE_HANDS_A_EVALUER = [[0], [1], [2], [3], [4]]
DECK = [0, 1, 2, 3, 4]

probs = np.zeros((3, len(POSSIBLE_HANDS_A_EVALUER)))

for hand in POSSIBLE_HANDS_A_EVALUER:
    #toutes les combinaisons des cartes de mes adversaires et des community cards
    other_cards = generate_all_plays_from_my_hand(hand, NB_PLAYERS, DECK.copy(), community_size=1)


    for possibilite in other_cards:
        #determiner si win, split ou loss

        me = max(hand[0], possibilite[1][0])

        best_adversaire = possibilite[1][0]
        for i in range(NB_PLAYERS-1):
            best_adversaire = max(best_adversaire, possibilite[0][i][0])

        if me > best_adversaire:
            probs[0, hand] += 1
        elif me == best_adversaire:
            probs[1, hand] += 1
        else:
            probs[2, hand] += 1

probs = probs / probs.sum(axis=0)
print(probs)
