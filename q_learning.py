import random as rand
from shoot_game import Game, Status, Actions
import json
from ast import literal_eval
from os.path import isfile


# state : ((bullet1, bullet2, bullet3, bullet4, bullet5, bullet6, bullet7, bullet8), (shield1, shield2))
# bullet : [0, MAX_VISION]
# shield1 : [0, 6] (0 : on; 1-6 : off)
# shield2 : [0, 4]

# keys : ((bullet1, bullet2, bullet3, bullet4, bullet5, bullet6, bullet7, bullet8), (shield1, shield2))
# values : [value of STAND, value of JUMP]


def agent_exists(path):
    return isfile('saves/' + path + '.json')


def save_agent(path, agent, game):
    file = open("saves/" + path + ".json", "w")
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
    file = open("saves/" + path + '.json', "r")
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
            self.actions_value = actions_values

    def get_value(self, state, action=None):
        if state not in self.actions_value:
            self.actions_value[state] = [0, 0]
        ret = self.actions_value[state]
        if action is not None:
            ret = ret[action.value] # Si l'on ne veut la valeur que d'une seule des actions
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

    def learn(self, state_1, action_1, state_2, reward):  # Appliquer la formule de Q Learning
        current = self.agent.get_value(state_1, action_1)
        max_t2_val = max(self.agent.get_value(state_2))
        new_val = current + self.alpha * (reward + self.gamma * max_t2_val - current)
        self.agent.set_value(state_1, action_1, new_val)

    def choose_action(self, state, real):
        if real or rand.uniform(0, 1) < self.epsilon:
            return self.agent.choose_best_action(state) # Politique Greedy
        return self.agent.explore() # Politique d'exploration


def bullet_pos(bullets, index):
    if index >= len(bullets):
        return MAX_VISION # S'il y a moins que 8 balles, il fait comme si d'autres étaient trop loin pour sa vision.
    return min(abs(bullets[index][0]), MAX_VISION) # Il ne voit que les balles situées dans [-MAX_VISION, MAX_VISION]


def game_to_state(game): # Renvoie un tuple décrivant la partie à l'instant présent
    b = game.bullets
    watched_bullets = tuple(bullet_pos(b, i) for i in range(8)) # Le joueur voit les 8 balles les plus proches
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
    
    default_training_params.update(training_params) # Fusionne les deux bibliothèques en utilisant les valeurs de training_params lorsqu'il y a un conflit
    default_game_params.update(game_params) # Idem avec game_params
    
    return default_training_params, default_game_params


def tick_and_learn(game, q):
    state1 = game_to_state(game)
    chosen_action = q.choose_action(state1, False)
    reward = 0
    first = True
                
    action = chosen_action
    while first or game.is_jumping > 0: # Tick jusqu'à la fin de l'action choisie (1 tick si STAND, 3 ticks si JUMP)
        first = False
        game.tick(action)
        s = game.player_status
        action = Actions.STAND #Action par défaut, elle n'est pas appliquée car le joueur est en l'air
        if s == Status.HIT:
            reward += -100
        elif s == Status.DOUBLE_HIT:
            reward += -200
        elif s == Status.DODGED:
            reward += 10
        elif s == Status.SHIELD_HIT:
            reward += 1
            
    q.learn(state1, chosen_action, game_to_state(game), reward)


def train(agent=None, save_file=None, training_params=None, game_params=None, learn_rate=0.3, discount_rate=0.8, show_prints=True):
    """
    
    :param agent: agent to train
    :param save_file: string : name of the save file
    :param training_params: cycle_nb: 100, game_duration: 100, prob_step: 2
    :param game_params: width: 5, shields_cd: None
    :param learn_rate: 
    :param discount_rate:
    :param show_prints: 
    :return: 
    """
    
    training_params, game_params = set_parameters(training_params, game_params)

    if agent is None:
        agent = Agent()

    q = QLearning(learn_rate, discount_rate, agent, 0.8)

    cycle_nb = training_params['cycle_nb']
    game_duration = training_params['game_duration']
    probability_step = training_params['prob_step']

    shields_cd = game_params['shields_cd']
    width = game_params['width']

    # Cycle : entraînement balayant les probabilités de 0 à 1
    # Pour chaque probabilité, il joue pendant "game_duration" ticks
    for a in range(cycle_nb): 
        for p in range(0, 100 + probability_step, probability_step):
            probability = p/100
            game = Game(probability, width, shields_cd)

            for i in range(game_duration):
                tick_and_learn(game, q)

        if show_prints:
            print("Cycle", a+1, 'of', cycle_nb)

    if save_file is not None:
        save_agent(save_file, q.agent, game)

    return q.agent
