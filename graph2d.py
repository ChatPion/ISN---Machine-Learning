import numpy as np
import matplotlib.pyplot as plt
from shoot_game import Game, Status
from q_learning import Agent, load_agent, train, game_to_state
from os.path import isfile
import os

def play_game(agent, game, duration):
    hit_counter = 0
    for i in range(duration):
        action = agent.choose_best_action(game_to_state(game))
        game.tick(action)
    return game.nb_hit / game.shot_bullets if game.shot_bullets > 0 else 0

cycle_nb = 100
agents_nb = 50
probability = float(input("probability ?"))

hits = np.zeros((cycle_nb, agents_nb))
agent_list = [Agent() for i in range(agents_nb)]
game = Game(probability, 5)

for agent_id in range(agents_nb):
    if isfile('stats2d'+str(agent_id)+'.json'):
        os.remove('stats2d'+str(agent_id)+'.json')
    agent = agent_list[agent_id]
    for cycle in range(cycle_nb):
        game.reset()
        hits[cycle, agent_id] = play_game(agent, game, 200)

        agent =  train('stats2d' + str(agent_id), training_params={'cycle_nb': 1, 'prob_step': 10, 'game_duration': 10}, show_prints=False, save_to_file = False)
        # agent, game = load_agent('stats2d' + str(agent_id))
        
        print("Cycle", cycle+1)

plt.plot([np.mean(hits[i]) for i in range(cycle_nb)], "r-")
##for i in range(cycle_nb):
##    plt.plot([i, i], [np.mean(hits[i]) - np.std(hits[i]), np.mean(hits[i]) + np.std(hits[i])], "b-", linewidth = 1.0)
plt.plot([np.std(hits[i]) for i in range (cycle_nb)], "b-")
plt.show()
