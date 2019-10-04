import random

import numpy as np


def create_players(n_players):
    players = []
    for i in range(n_players):
        player = {'id': i,
                  'strategy': random.choice(["c", "d"]),
                  'fitness': 0}
        players.append(player)
    return players


class ListGraph(object):
    def __init__(self, num_nodes):
        self.matrix = [[0] * num_nodes for _ in range(num_nodes)]

    def add_edge(self, v1, v2, value):
        self.matrix[v1][v2] = value
        self.matrix[v2][v1] = value


def make_groups(n_players, k=5):
    if n_players % k != 0:
        print("number of gamers is not a multiple of the size of the group")
        return 1
    groups = []
    num_gr = n_players//k
    for i in range(num_gr):
        groups.append(list(range(i*k, i*k+k)))
    return groups


def internal_communications(players_graph, player_groups,
                            low_w=0.5, high_w=0.9):
    for gr_num, group in enumerate(player_groups):
        for i in group:
            if i % 5 == 0:
                players_graph.add_edge(i, i+1,
                                       round(random.uniform(low_w, high_w), 3))
                players_graph.add_edge(i, i+2,
                                       round(random.uniform(low_w, high_w), 3))
                players_graph.add_edge(i, i+3,
                                       round(random.uniform(low_w, high_w), 3))
                players_graph.add_edge(i, i+4,
                                       round(random.uniform(low_w, high_w), 3))
            elif i % 5 == 2:
                players_graph.add_edge(i, (i+1),
                                       round(random.uniform(low_w, high_w), 3))
                players_graph.add_edge(i, (i-1),
                                       round(random.uniform(low_w, high_w), 3))
            elif i % 5 == 4:
                players_graph.add_edge(i, (i-1),
                                       round(random.uniform(low_w, high_w), 3))
                players_graph.add_edge(i, (i-3),
                                       round(random.uniform(low_w, high_w), 3))

    return players_graph


def sublist(lst1, lst2):
    return all(elem in lst1 for elem in lst2)


def sublist_in_group(pair, groups):
    s = False
    for gr in groups:
        s = s or sublist(gr, pair)
    return s


def external_communications(players_graph, player_groups,
                            w_low=0.2, w_high=0.4):
    non_zero_to_int = (np.array(players_graph.matrix) != 0).astype(int)
    list_of_idxs = np.where(np.sum(non_zero_to_int, axis=1) < 4)[0]
    while len(list_of_idxs) > 3:
        n1 = 0
        n2 = 0
        while n1 == n2 or sublist_in_group([n1, n2], player_groups):
            n1 = random.choice(list_of_idxs)
            n2 = random.choice(list_of_idxs)

        players_graph.add_edge(n1, n2, round(random.uniform(w_low, w_high), 3))
        non_zero_to_int = (np.array(players_graph.matrix) != 0).astype(int)
        list_of_idxs = np.where(np.sum(non_zero_to_int, axis=1) < 4)[0]
    return players_graph


def play(str1, str2):
    if str1 == str2:
        if str1 == "c":
            return 3, 3
        else:
            return 1, 1
    else:
        if str1 == "c":
            return 0, 5
        else:
            return 5, 0


def play_game(players, p_1_id, p_2_id):
    p_1_strategy = players[p_1_id]["strategy"]
    p_2_strategy = players[p_2_id]["strategy"]

    p1_fit, p2_fit = play(p_1_strategy, p_2_strategy)
    players[p_1_id]["fitness"] = p1_fit
    players[p_2_id]["fitness"] = p2_fit
    return players


def play_one_round(players, players_graph, n_players):
    players_id = list(range(n_players))
    while len(players_id) > 0:
        p_1_id = random.choice(players_id)
        p_1_vec = players_graph.matrix[p_1_id]

        rand = np.random.uniform(low=0.0, high=1.0, size=n_players)
        opponents = np.argsort(p_1_vec*rand)[::-1]

        idx = 0
        p_2_id = opponents[idx]
        while p_2_id not in players_id or p_2_id == p_1_id:
            idx += 1
            p_2_id = opponents[idx]

        players_id.remove(p_1_id)
        players_id.remove(p_2_id)

        players = play_game(players, p_1_id, p_2_id)
    return players


def update_strategies(players, players_graph, noise=0):
    for player_id, p in enumerate(players_graph.matrix):
        p = np.array(p)
        neighbour_idxs = np.where(p > 0)[0]
        probs = []
        strategies = []
        for p_i in neighbour_idxs:
            w = players[p_i]["fitness"] * p[p_i]
            probs.append(w * np.random.uniform(low=0.0, high=1.0))
            strategies.append(players[p_i]["strategy"])
        new_strategy = strategies[np.argmax(np.array(probs))]
        if noise != 0:
            prob = np.random.uniform(low=0.0, high=1.0)
            if prob < noise:
                new_strategy = random.choice(["c", "d"])

        players[player_id]["strategy"] = new_strategy
    return players


def num_coopers(players):
    n_cooperators = 0
    for p in players:
        if p['strategy'] == "c":
            n_cooperators += 1
    return n_cooperators
