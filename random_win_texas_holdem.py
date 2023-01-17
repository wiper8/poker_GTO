import numpy as np
import copy
import matplotlib.pyplot as plt
from utils import *
from texas_holdem import *

#probabilités de Win/Split/loss (et proxy de l'equity (force de la main)) si tous jouaient toujours leurs mains.

for n in range(2, 10):
    NB_PLAYERS = n
    NB_RANDOM_GAMES_PER_13X13_HANDS = 10000
    POSSIBLE_HANDS_A_EVALUER = generate_13x13_pairs()
    DECK = [
            "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH",
            "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "TS", "JS", "QS", "KS", "AS",
            "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "TD", "JD", "QD", "KD", "AD",
            "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "TC", "JC", "QC", "KC", "AC"
        ]

    probs = np.zeros((3, len(POSSIBLE_HANDS_A_EVALUER)))
    possible_hands_copy = copy.deepcopy(POSSIBLE_HANDS_A_EVALUER)

    for h, hand in tqdm.tqdm(enumerate(possible_hands_copy), total=len(possible_hands_copy)):
        #toutes les combinaisons des cartes de mes adversaires et des community cards

        other_cards = generate_some_plays_from_my_hand(hand, NB_PLAYERS, NB_RANDOM_GAMES_PER_13X13_HANDS, DECK.copy())

        for possibilite in other_cards:
            #determiner si win, split ou loss
            possibilite[0].append(hand)

            winners = determining_winning_hand(copy.deepcopy(possibilite[0]), copy.deepcopy(possibilite[1]))

            if len(winners) == 1:
                if (NB_PLAYERS-1) in winners:
                    probs[0, h] += 1
                else:
                    probs[2, h] += 1
            elif (NB_PLAYERS-1) in winners:
                probs[1, h] += 1
            else:
                probs[2, h] += 1

    probs = probs / probs.sum(axis=0)

    #pour voir les probs brutes win/split/loss
    #print(probs)


    proxy_equity = [None] * len(POSSIBLE_HANDS_A_EVALUER)
    base_equity = probs[0, :]+probs[1, :]/2
    for i, id in enumerate(reversed(np.argsort(base_equity))):
        proxy_equity[i] = [POSSIBLE_HANDS_A_EVALUER[id], base_equity[id]]

    equity_grid = np.zeros((13, 13))

    for hand in proxy_equity:

        value_carte_1 = id_to_int[hand[0][0][0]]

        #pair
        if hand[0][0][0] == hand[0][1][0]:
            n = 12 - (value_carte_1 - 2)
            equity_grid[n, n] = hand[1]
        else:
            value_carte_2 = id_to_int[hand[0][1][0]]

            #suited
            if hand[0][0][1] == hand[0][1][1]:
                equity_grid[12 - (max(value_carte_1, value_carte_2) - 2), 12 - (min(value_carte_1, value_carte_2) - 2)] = hand[1]

            else:
                #off-suit
                equity_grid[12 - (min(value_carte_1, value_carte_2) - 2), 12 - (max(value_carte_1, value_carte_2) - 2)] = hand[1]


    fig, ax = plt.subplots(figsize=(10,10))

    grid = ax.imshow(equity_grid, cmap='OrRd', interpolation='nearest')

    grid.set_clim(0, 1)

    for hand in proxy_equity:
        value_carte_1 = id_to_int[hand[0][0][0]]
        #pair
        if hand[0][0][0] == hand[0][1][0]:
            n = 12 - (value_carte_1 - 2)
            plt.text(n, n, f'{hand[0][0][0]}{hand[0][0][0]}\n{equity_grid[n, n]:.2f}',
                     horizontalalignment='center',
                     verticalalignment='center',
                     )
        else:
            value_carte_2 = id_to_int[hand[0][1][0]]

            #suited
            if hand[0][0][1] == hand[0][1][1]:
                x = 14 - min(value_carte_1, value_carte_2)
                y = 14 - max(value_carte_1, value_carte_2)
                plt.text(x,
                         y,
                         f'{int_to_id[max(value_carte_1, value_carte_2)]}{int_to_id[min(value_carte_1, value_carte_2)]}s\n{equity_grid[y, x]:.2f}',
                         horizontalalignment='center',
                         verticalalignment='center',
                         )
            else:
                #off-suit
                x = 14 - max(value_carte_1, value_carte_2)
                y = 14 - min(value_carte_1, value_carte_2)
                plt.text(x,
                         y,
                         f'{int_to_id[max(value_carte_1, value_carte_2)]}{int_to_id[min(value_carte_1, value_carte_2)]}0\n{equity_grid[y, x]:.2f}',
                         horizontalalignment='center',
                         verticalalignment='center',
                         )

    plt.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False,
        right=False,
        left=False,
        labelleft=False
    )

    plt.savefig('images/proxy_equity_random_'+str(NB_PLAYERS)+'players.png')
