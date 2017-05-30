import numpy as np
import matplotlib.pyplot as plt
from shoot_game import Game, Status
from q_learning import Agent,  train, game_to_state, agent_exists
import json
from ast import literal_eval
from os.path import isfile
import os

def play_game(agent, game, duration):
    for i in range(duration):
        action = agent.choose_best_action(game_to_state(game))
        game.tick(action)
    return game.nb_hit / game.shot_bullets if game.shot_bullets > 0 else 0

def load_test(path, agent_list):
    file = open("saves/" + path + ".json", "r")
    data = json.loads(file.read())

    training_params = data["options"]["training_params"]
    
    test_params = data["options"]["test_params"]
    probability = float(test_params["probability"])
    steps_nb =int(test_params["steps_nb"])
    agents_nb = int(test_params["agents_nb"])
    test_duration = int(test_params["duration"])

    for i in range(agents_nb):
        dic = {}
        load_data = data["data"+str(i)]
        for k, v in load_data.items():
            dic[literal_eval(k)] = v
        agent_list[i].actions_value = dic
    

def test(agents_nb, steps_nb = 10, probability = 0.33, test_duration = 50, training_params={'cycle_nb': 50, 'prob_step': 10, 'game_duration': 20}):
    hits = np.zeros((steps_nb, agents_nb))
    agent_list = [Agent() for i in range(agents_nb)]
#    if agent_exists("stat2d"+str(agents_nb)):
 #       load_test("stat2d"+str(agents_nb), agent_list)

    game = Game(probability, 5)

    for agent_id in range(agents_nb):
        agent = agent_list[agent_id]
        for step in range(steps_nb):
            game.reset()
            hits[step, agent_id] = play_game(agent, game, test_duration)

            agent =  train(agent = agent, training_params=training_params, show_prints=False)
            
        print("Agent", agent_id+1)

    file = open ("saves/stat2d"+str(agents_nb)+".json", "w")
    
    to_write = json.dumps({

        'data'+str(i): {str(k): v for k,v in agent_list[i].actions_value.items()} for i in range(agents_nb)
    })
    file.write(to_write)
    file.close()

    return hits


def show_plot(array, rows):
    plt.plot([np.mean(array[row]) for row in range(rows)], "r-")
    ##for i in range(cycle_nb):
    ##    plt.plot([i, i], [np.mean(hits[i]) - np.std(hits[i]), np.mean(hits[i]) + np.std(hits[i])], "b-", linewidth = 1.0)
    plt.plot([np.std(array[row]) for row in range (rows)], "b-")
    plt.show()

values = test(15)
show_plot(values, steps_nb)
