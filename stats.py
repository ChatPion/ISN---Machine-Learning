import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from q_learning import Agent, load_agent, train, game_to_state
from shoot_game import Game, Status
from os.path import isfile
import os


def play_game(agent, game, duration):
    hit_counter = 0
    for i in range(duration):
        action = agent.choose_best_action(game_to_state(game))
        game.tick(action)
        if game.player_status == Status.HIT:
            hit_counter += 1
    return hit_counter

print("Training start")
hits = np.zeros((10, 10))
for cycle in range(10):
    train('stats', training_params={'cycle_nb': 20, 'prob_step': 10, 'game_duration': 10}, show_prints=False)
    agent, game = load_agent('stats')
    for i in range(10):
        game.reset()
        game.probability = float(i) / 10
        hits[cycle, i] = play_game(agent, game, 100)
    print("Cycle", cycle+1)

os.remove('stats.json')

X, Y = np.meshgrid(np.arange(0, 10, 1), np.arange(0, 10, 1))
ax = plt.figure().add_subplot(111, projection="3d")
ax.plot_surface(X, Y, hits, rstride=1, cstride=1, cmap='hot')
plt.show()
