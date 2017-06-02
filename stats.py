import os
from os.path import isfile

import matplotlib.pyplot as plt
import numpy as np

from q_learning import Agent, load_agent, train, game_to_state
from shoot_game import Game

plt.xkcd()


def play_game(agent, game, duration):
    for i in range(duration):
        action = agent.choose_best_action(game_to_state(game))
        game.tick(action)
    return game.nb_hit / game.shot_bullets if game.shot_bullets > 0 else 0

cycle_nb = 20
prob_step = 10

print("Training start")
hits = np.zeros((cycle_nb, prob_step))
max_hits = np.zeros((cycle_nb, prob_step))
min_hits = np.zeros((cycle_nb, prob_step))
min_hits.fill(2)
agent_list = [Agent() for i in range(10)]
game = Game(0, 5)
for agent_id in range(len(agent_list)):
    if isfile('stats'+str(agent_id)+'.json'):
        os.remove('stats'+str(agent_id)+'.json')
    agent = agent_list[agent_id]
    for cycle in range(cycle_nb):
        for i in range(prob_step):
            game.reset()
            game.probability = float(i) / prob_step
            nb_hits = play_game(agent, game, 100)
            hits[cycle, i] += nb_hits
            max_hits[cycle, i] = max(max_hits[cycle, i], nb_hits)
            min_hits[cycle, i] = min(min_hits[cycle, i], nb_hits)
        train(training_params={'cycle_nb': 5, 'prob_step': 10, 'game_duration': 10}, show_prints=False)
        agent, game = load_agent('stats' + str(agent_id))
        print("Cycle", cycle+1)

hits /= len(agent_list)

X, Y = np.meshgrid(np.arange(0, prob_step, 1), np.arange(0, cycle_nb, 1))
Xmax, Ymax = np.meshgrid(np.arange(0, prob_step, 1), np.arange(0, cycle_nb, 1))
Xmin, Ymin = np.meshgrid(np.arange(0, prob_step, 1), np.arange(0, cycle_nb, 1))
ax = plt.figure().add_subplot(111, projection="3d")
ax.plot_surface(X, Y, hits, rstride=1, cstride=1, cmap='summer')
#ax.plot_surface(Xmax, Ymax, max_hits, rstride=1, cstride=1, cmap='hot')
#ax.plot_surface(Xmin, Ymin, min_hits, rstride=1, cstride=1, cmap='cool')
plt.show()
