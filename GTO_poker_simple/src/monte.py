import sys
import json
import numpy as np

from copy import deepcopy
from itertools import permutations
from tqdm import tqdm
from leduc.best_response import exploitability
from leduc.node import MNode as Node
from leduc.card import Card
from leduc.hand_eval import leduc_eval
from leduc.util import expected_utility, bias

STRAT_INTERVAL = 100
PRUNE_THRESH = 200
DISCOUNT = 10
LCFR_INTERVAL = 400
REGRET_MIN = -300000


def learn(iterations, cards, num_cards, node_map, action_map):
    if len(cards) > 4:
        from leduc.state import Leduc as State
        from leduc.hand_eval import leduc_eval as eval
    else:
        from leduc.state import State
        from leduc.hand_eval import kuhn_eval as eval

    all_combos = [list(t) for t in set(permutations(cards, num_cards))]
    num_players = len(node_map)
    for i in tqdm(range(1, iterations + 1), desc="learning"):
        card = np.random.choice(len(all_combos))
        for player in range(num_players):
            state = State(all_combos[card], num_players, eval)
            if i % STRAT_INTERVAL == 0:
                update_strategy(player, state, node_map, action_map)

            if i > PRUNE_THRESH:
                chance = np.random.rand()
                if chance < .05:
                    accumulate_regrets(player, state, node_map, action_map)
                else:
                    accumulate_regrets(player, state, node_map, action_map,
                                       prune=True)
            else:
                accumulate_regrets(player, state, node_map, action_map)

        if i < LCFR_INTERVAL and i % DISCOUNT == 0:
            discounted = (i/DISCOUNT)/(i/(DISCOUNT) + 1)
            for player in node_map:
                player_nodes = node_map[player]
                for key, node in player_nodes.items():
                    node.regret_sum = {key: value * discounted for
                                       key, value in node.regret_sum.items()}
                    node.strategy_sum = {key: value * discounted for
                                         key, value in node.strategy_sum.items()}


def update_strategy(traverser, state, node_map, action_map):
    if state.terminal:
        return

    turn = state.turn
    info_set = state.info_set()

    if info_set not in action_map[turn]:
        action_map[turn][info_set] = {'actions': state.valid_actions()}

    valid_actions = action_map[turn][info_set]['actions']

    if info_set not in node_map[turn]:
        node_map[turn][info_set] = Node(valid_actions)

    node = node_map[turn][info_set]
    strategy = node.strategy()

    if turn == traverser:
        actions = list(strategy.keys())
        probs = list(strategy.values())
        random_action = actions[np.random.choice(len(actions), p=probs)]
        node.strategy_sum[random_action] += 1
        new_state = state.take(random_action, deep=True)

        update_strategy(traverser, new_state, node_map, action_map)

    else:
        for action in valid_actions:
            new_state = state.take(action, deep=True)
            update_strategy(traverser, new_state, node_map, action_map)


def accumulate_regrets(traverser, state, node_map, action_map, prune=False):
    if state.terminal:
        util = state.utility()
        return util

    turn = state.turn
    info_set = state.info_set()

    if info_set not in action_map[turn]:
        action_map[turn][info_set] = {'actions': state.valid_actions()}

    valid_actions = action_map[turn][info_set]['actions']

    if info_set not in node_map[turn]:
        node_map[turn][info_set] = Node(valid_actions)

    node = node_map[turn][info_set]
    strategy = node.strategy()

    if turn == traverser:
        util = {a: 0 for a in valid_actions}
        node_util = np.zeros(len(node_map))
        explored = set(valid_actions)

        for action in valid_actions:
            if prune is True and node.regret_sum[action] <= REGRET_MIN:
                explored.remove(action)
            else:
                new_state = state.take(action, deep=True)
                returned = accumulate_regrets(traverser, new_state, node_map,
                                              action_map, prune=prune)

                util[action] = returned[turn]
                node_util += returned * strategy[action]

        for action in explored:
            regret = util[action] - node_util[turn]
            node.regret_sum[action] += regret

        return node_util

    else:
        actions = list(strategy.keys())
        probs = list(strategy.values())
        random_action = actions[np.random.choice(len(actions), p=probs)]
        new_state = state.take(random_action, deep=True)
        return accumulate_regrets(traverser, new_state, node_map, action_map,
                                  prune=prune)

class Search:
    def __init__(self, state, blueprint, actions, cards, num_cards):                                  
        self.blueprint = blueprint
        self.action_map = actions
        self.cards = cards
        self.num_cards = num_cards
        self.num_players = len(blueprint)

        self.state = state
        self.all_combos = [list(t) for t in set(permutations(self.cards, self.num_cards))]

    def search(self):

        starting_state = deepcopy(self.state)
        node_map = deepcopy(self.blueprint)
        action_map = deepcopy(self.action_map)

        continuations = {i: {} for i in range(len(node_map))}

        for i in tqdm(range(1, 1001), desc="searching"):
            card_choice = np.random.choice(len(self.all_combos))
            starting_state.cards = self.all_combos[card_choice]
            for player in range(self.num_players):
                if i % STRAT_INTERVAL == 0:
                    self.update_strategy_search(player, starting_state, node_map, action_map, continuations)

                if i > PRUNE_THRESH:
                    chance = np.random.rand()
                    if chance < .05:
                        self.accumulate_regrets_search(player, starting_state, node_map, action_map, continuations)
                    else:
                        self.accumulate_regrets_search(player, starting_state, node_map, action_map,
                                                       continuations, prune=True)
                else:
                    self.accumulate_regrets_search(player, starting_state, node_map, action_map, continuations)

            if i < LCFR_INTERVAL and i % DISCOUNT == 0:
                discounted = (i/DISCOUNT)/(i/(DISCOUNT) + 1)
                for player in node_map:
                    player_nodes = node_map[player]
                    for key, node in player_nodes.items():
                        node.regret_sum = {key: value * discounted for
                                        key, value in node.regret_sum.items()}
                        node.strategy_sum = {key: value * discounted for
                                            key, value in node.strategy_sum.items()}
        return node_map 


    def update_strategy_search(self, traverser, state, node_map, action_map, continuation, leaf=False):
        if state.terminal:
            return

        turn = state.turn
        info_set = state.info_set()

        if info_set not in action_map[turn]:
            action_map[turn][info_set] = {'actions': state.valid_actions()}

        valid_actions = action_map[turn][info_set]['actions']

        if leaf is True:
            if info_set not in continuation[turn]:
                continuation[turn][info_set] = Node([i for i in range(4)])

            node = continuation[turn][info_set]
        else:
            if info_set not in node_map[turn]:
                node_map[turn][info_set] = Node(valid_actions)

            node = node_map[turn][info_set]

        strategy = node.strategy()

        if turn == traverser:
            actions = list(strategy.keys())
            probs = list(strategy.values())
            random_action = actions[np.random.choice(len(actions), p=probs)]
            node.strategy_sum[random_action] += 1
            new_state = state.take(random_action, deep=True)

            if leaf is False:
                self.update_strategy_search(traverser, new_state, node_map, action_map, continuation,
                                    leaf=new_state.round!=state.round)

        else:
            if leaf is False:
                for action in valid_actions:
                    new_state = state.take(action, deep=True)
                    self.update_strategy_search(traverser, new_state, node_map, action_map, continuation,
                                    leaf=new_state.round!=state.round)


    def accumulate_regrets_search(self, traverser, state, node_map, action_map, continuations, prune=False, leaf=False):
        if state.terminal:
            util = state.utility()
            return util

        turn = state.turn
        info_set = state.info_set()

        if info_set not in action_map[turn]:
            action_map[turn][info_set] = {'actions': state.valid_actions()}

        valid_actions = action_map[turn][info_set]['actions']
        if 'fixed' in valid_actions:
            valid_actions = [action_map[turn][info_set]['fixed']]

        if leaf is True:
            if info_set not in continuations[turn]:
                continuations[turn][info_set] = Node(["NULL", "F", "C", "4R"])

            node = continuations[turn][info_set]
            valid_actions = ["NULL", "F", "C", "4R"]
        else:
            if info_set not in node_map[turn]:
                node_map[turn][info_set] = Node(valid_actions)

            node = node_map[turn][info_set]

        strategy = node.strategy()

        if turn == traverser:
            util = {a: 0 for a in valid_actions}
            node_util = np.zeros(len(node_map))
            explored = set(valid_actions)

            for action in valid_actions:
                if prune is True and leaf is False and node.regret_sum[action] <= REGRET_MIN:
                    explored.remove(action)
                else:
                    if leaf is True:
                        returned = self.rollout(traverser, state, action)
                    else:
                        new_state = state.take(action, deep=True)
                        returned = self.accumulate_regrets_search(traverser, new_state, node_map, action_map, continuations,
                                                                  prune=prune, leaf=new_state.round!=state.round) 
                    util[action] = returned[turn]
                    node_util += returned * strategy[action]

            for action in explored:
                regret = util[action] - node_util[turn]
                node.regret_sum[action] += regret

            return node_util

        else:
            if leaf is True:
                return self.rollout(traverser, state, "NULL") 

                
            actions = list(strategy.keys())
            probs = list(strategy.values())
            random_action = actions[np.random.choice(len(actions), p=probs)]
            new_state = state.take(random_action, deep=True)
            return self.accumulate_regrets_search(traverser, new_state, node_map, action_map, continuations,
                                                  prune=prune, leaf=new_state.round!=state.round)
    def rollout(self, player, state, contin_strat):
        node_map = self.blueprint
        action_map = self.action_map

        util = np.zeros(len(node_map))
        starting_state = deepcopy(state)

        indistinguishable_states = [combo for combo in self.all_combos if combo[player] == state.cards[player]] 

        num_rollouts = 5
        for _ in range(num_rollouts):
            card_choice = np.random.choice(len(indistinguishable_states))
            starting_state.cards = indistinguishable_states[card_choice]

            util += self.playout(player, contin_strat, starting_state, node_map, action_map)

        return util / num_rollouts

    def playout(self, player, contin_strat, hand, node_map, action_map):
        if hand.terminal:
            utility = hand.utility()
            return utility

        info_set = hand.info_set()
        node = node_map[hand.turn][info_set]

        strategy = node.avg_strategy()
        if player == hand.turn:
            strategy = bias(strategy, contin_strat)

        util = np.zeros(len(node_map))
        valid_actions = action_map[hand.turn][info_set]['actions']
        for action in valid_actions:
            new_hand = hand.take(action, deep=True)
            util += self.playout(player, contin_strat, new_hand, node_map, action_map) * strategy[action]

        return util
                                         

if __name__ == '__main__':
    num_players = 2
    node_map = {i: {} for i in range(num_players)}
    action_map = {i: {} for i in range(num_players)}
    cards = [Card(14, 1), Card(13, 1), Card(12, 1), Card(14, 2), Card(13, 2), Card(12, 2)]
    learn(50000, cards, 3, node_map, action_map)

    for player in node_map:
        print(f"Player {player}")
        print('Number of info sets', len(node_map[player]))
        for info_set, node in node_map[player].items():
            avg_strat = node.avg_strategy()
            print(f"{info_set}: {avg_strat}")
        

    util = expected_utility(cards, 3, 2, node_map, action_map)
    print(util)