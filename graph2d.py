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
    steps_nb = int(test_params['steps_nb'])
    agents_nb = int(test_params["agents_nb"])
    test_duration = int(test_params["duration"])
    
    for i in range(agents_nb):
        dic = {}
        load_data = data["data"]["data"+str(i)]
        for k, v in load_data.items():
            dic[literal_eval(k)] = v
        agent_list[i].actions_value = dic
    
        return training_params, probability, steps_nb, agents_nb, test_duration, data['old_results'], agent_list

def test(agents_nb, continued = False, steps_nb = 100, probability = 0.66, test_duration = 10000, training_params={'cycle_nb': 1, 'prob_step': 10, 'game_duration': 20}):
    agent_list = [Agent() for i in range(agents_nb)]
    old_results = []
    if continued and agent_exists("stat2d"+str(agents_nb)):
        training_params, probability, steps_nb, agents_nb, test_duration, old_results, agent_list = load_test("stat2d"+str(agents_nb), agent_list)
    hits = old_results + [[0 for i in range(agents_nb)] for j in range(steps_nb)]
    
    game = Game(probability, 5)

    for agent_id in range(agents_nb):
        agent = agent_list[agent_id]
        for step in range(steps_nb):
            game.reset()
            hits[len(hits) - steps_nb + step][agent_id] = play_game(agent, game, test_duration)

            agent =  train(agent = agent, training_params=training_params, show_prints=False)
            
        print("Agent", agent_id+1)
        
    file = open ("saves/stat2d"+str(agents_nb)+".json", "w")
    data = {}
    for i in range(agents_nb):
        data["data"+str(i)] = {str(k): v for k,v in agent_list[i].actions_value.items()}
    to_write = json.dumps({
        'data': data,
        'options': {
            'training_params': training_params,
            'test_params': {
                'probability': probability,
                'steps_nb': steps_nb,
                'agents_nb': agents_nb,
                'duration': test_duration
            }
        },
        'old_results': hits
    })
    file.write(to_write)
    file.close()
    file = open ("saves/stat2d"+str(agents_nb)+".json", "r")
    return hits

def show_plot(array, rows, columns):
##    for i in range(columns):
##        plt.plot([array[j][i] for j in range(rows)], "r-", linewidth = 1.0)
## #   plt.plot([np.mean(array[row]) for row in range(rows)], "g-")
## #   for i in range(rows):
###        plt.plot([i, i], [np.mean(array[i]) - np.std(array[i]), np.mean(array[i]) + np.std(array[i])], "b-", linewidth = 1.0)
##    plt.plot([np.std(array[row]) for row in range (rows)], "b-", linewidth = 0.5)
##    plt.axis([0, rows, 0, 0.6])
##    plt.show()
    
 #   for i in range(columns):
#        plt.plot([array[j][i] for j in range(rows)], "r-")
    plt.plot([np.mean(array[row]) for row in range(rows)], "g-")
    for i in range(rows):
        plt.plot([i, i], [np.mean(array[i]) - np.std(array[i]), np.mean(array[i]) + np.std(array[i])], "b-", linewidth = 0.5)
    plt.plot([np.std(array[row]) for row in range (rows)], "b-", linewidth = 0.5)
    plt.axis([0, rows, 0, 0.6])
    plt.show()
    
values = test(4, continued = False)
show_plot(values, len(values), len(values[0]))
