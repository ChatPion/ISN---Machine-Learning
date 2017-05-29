import random as rand
from shoot_game import Game, Status, Actions
import json
from ast import literal_eval
from os.path import isfile


# state : ((bullet1, bullet2, bullet3, bullet4, bullet5, bullet6), (shield1, shield2))
# bullet : [0, 5] (6 : too far)
# shield1 : [0, 6] (0 : on; 1-6 : off)
# shield2 : [0, 4]
# keys : ((bullet1, bullet2, bullet3, bullet4, bullet5, bullet6), (shield1, shield2))
# values : [value of STAND, value of JUMP]


def save_agent(path, agent, game):
    file = open(path + ".json", "w")
    data = json.dumps({
        'data': {str(k): v for k, v in agent.actions_value.items()},
        'options': {
            'width': game.width,
            'shields_cooldown': game.shields_cooldown
        }
    })
    file.write(data)
    file.close()


def load_agent(path):
    file = open(path + '.json', "r")
    data = json.loads(file.read())

    options = data['options']

    probability = 0.33
    width = int(options['width'])
    shields_cd = options['shields_cooldown']

    dict = {}
    learn_data = data['data']
    for k, v in learn_data.items():
        dict[literal_eval(k)] = v
    return Agent(dict), Game(probability, width, shields_cd)


class Agent:
    def __init__(self, actions_values=None):
        self.actions_value = {}
        if actions_values is not None: 
            self.actions_value = actions_values #if loading an already trained machine

    def get_value(self, state, action=None):
        if state not in self.actions_value:
            self.actions_value[state] = [0, 0] # if encountering an unknown state
        ret = self.actions_value[state]
        if action is not None:
            ret = ret[action.value] # if wanting the value of STAND or JUMP
        return ret

    def set_value(self, state, action, value):
        self.actions_value[state][action.value] = value

    def choose_best_action(self, state):
        stand_val = self.get_value(state, Actions.STAND)
        jump_val = self.get_value(state, Actions.JUMP)
        if stand_val >= jump_val:
            return Actions.STAND
        return Actions.JUMP

    def explore(self):
        return rand.choice([Actions.STAND, Actions.JUMP])


class QLearning:
    def __init__(self, alpha, gamma, agent, epsilon):
        """
        alpha: learning rate
        gamma: discount rate
        epsilon: exploration rate [0; 1]
        """
        self.alpha = alpha
        self.gamma = gamma
        self.agent = agent
        self.epsilon = epsilon

    def learn(self, state_1, action_1, state_2, reward):  # Apply Q Learning formula
        current = self.agent.get_value(state_1, action_1)
        max_t2_val = max(self.agent.get_value(state_2))
        new_val = current + self.alpha * (reward + self.gamma * max_t2_val - current)
        self.agent.set_value(state_1, action_1, new_val)

    def choose_action(self, state, real):
        if real or rand.uniform(0, 1) < self.epsilon:
            return self.agent.choose_best_action(state) # Greedy
        return self.agent.explore() # Exploration


def bullet_pos(bullets, index):
    if index >= len(bullets):
        return MAX_VISION # If there are less than 6 bullets, it thinks the others are out of range.
    return min(abs(bullets[index][0]), MAX_VISION) # It sees only bullets that are within range of his MAX_VISION


def game_to_state(game): # Returns a tuple describing the game at the current state
    b = game.bullets
    watched_bullets = tuple(bullet_pos(b, i) for i in range(6)) # It sees the 6 nearest bullets
    shields = tuple(game.shields)
    return (watched_bullets, shields)


MAX_VISION = 5

def set_parameters(training_params, game_params):
    if training_params is None:
        training_params = {}
    if game_params is None:
        game_params = {}
    
    default_training_params = {'cycle_nb': 100, 'game_duration': 100, 'prob_step': 2}
    default_game_params = {'width': 5, 'shields_cd': None}
    
    default_training_params.update(training_params)
    default_game_params.update(game_params)
    
    return default_training_params, default_game_params


def tick_and_learn(game, q):
    state1 = game_to_state(game)
    chosen_action = q.choose_action(state1, False)
    reward = 0
    first = True
                
    action = chosen_action
    while first or game.is_jumping > 0: # Ticks until the end of the chosen action (1 tick if STAND, 2 ticks if JUMP)
        first = False
        game.tick(action)
        v = game.player_status
        action = Actions.STAND # Default action
        if v == Status.HIT:
            reward += -100
        elif v == Status.DODGED:
            reward += 10
        elif v == Status.SHIELD_HIT:
            reward += 1
            
    q.learn(state1, chosen_action, game_to_state(game), reward)


def train(file_name, training_params=None, game_params=None, learn_rate=0.3, discount_rate=0.8, show_prints=True):
    """
    
    :param show_prints: 
    :param file_name:
    :param training_params: cycle_nb: 100, game_duration: 100, prob_step: 2
    :param game_params: width: 5, shields_cd: None
    :param learn_rate: 
    :param discount_rate: 
    :return: 
    """
    
    training_params, game_params = set_parameters(training_params, game_params)

    agent = Agent() # Creates new agent
    if isfile(file_name + '.json'): # Loads agent if exists
        agent, _ = load_agent(file_name)
        if show_prints:
            print('Successfully loaded', file_name, '.json')


    q = QLearning(learn_rate, discount_rate, agent, 0.8)

    cycle_nb = training_params['cycle_nb']
    game_duration = training_params['game_duration']
    probability_step = training_params['prob_step']

    shields_cd = game_params['shields_cd']
    width = game_params['width']

    # Cycle : training for all probabilities [0, 1]
    # Training : plays the game during "game_duration" ticks
    for a in range(cycle_nb): 
        for p in range(0, 100 + probability_step, probability_step):
            probability = p/100
            game = Game(probability, width, shields_cd)

            for i in range(game_duration):
                tick_and_learn(game, q)

        if show_prints:
            print("Cycle", a+1, 'of', cycle_nb)

    save_agent(file_name, q.agent, game)
