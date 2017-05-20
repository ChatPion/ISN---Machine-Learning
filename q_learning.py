import random as rand
from shoot_game import Game, Status, Actions
import json
from ast import literal_eval


# state : ((bullet1, bullet2, bullet3, bullet4), (shield1, shield2))
# bullet : [0, 5] (6 : too far)
# shield1 : [0, 2] (0 : on)
# shield2 : [0, 4]

# TODO : Add simulation parameters in the savefile

def save_agent(path, agent, game):
    file = open(path, "w")
    data = json.dumps({
        'data': {str(k): v for k, v in agent.actions_value.items()},
        'options': {
            'width': game.width,
            'probability': game.probability,
            'shields_cooldown': game.shields_cooldown
        }
    })
    file.write(data)
    file.close()


def load_agent(path):
    file = open(path, "r")
    data = json.loads(file.read())

    options = data['options']

    probability = float(options['probability'])
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
            ret = ret[action.value]
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
    def __init__(self, alpha, gamma, agent):
        """
        alpha: learning rate
        gamme: discount rate
        """
        self.alpha = alpha
        self.gamma = gamma
        self.agent = agent

    def learn(self, state_1, action_1, state_2, reward):
        current = self.agent.get_value(state_1, action_1)
        max_t2_val = max(self.agent.get_value(state_2))
        new_val = current + self.alpha * (reward + self.gamma * max_t2_val - current)
        self.agent.set_value(state_1, action_1, new_val)

    def choose_action(self, state, real):
        if real or rand.uniform(0, 1) < 0.8:  # GREEDY
            return self.agent.choose_best_action(state)
        # exploration
        return self.agent.explore()


def bullet_pos(bullets, index):
    if index >= len(bullets):
        return MAX_VISION
    return min(abs(bullets[index][0]), MAX_VISION)


def game_to_state(game):
    b = game.bullets
    watched_bullets = (
    bullet_pos(b, 0), bullet_pos(b, 1), bullet_pos(b, 2), bullet_pos(b, 3), bullet_pos(b, 4), bullet_pos(b, 5))
    shields = tuple(game.shields)
    return (watched_bullets, shields)


MAX_VISION = 5


## GAME LOOP
def train(file_name, games_nb, probability, width, learn_rate=0.3, discount_rate=0.8):
    q = QLearning(learn_rate, discount_rate, Agent())

    game_duration = 100

    for a in range(games_nb):
        game = Game(probability, width)

        for i in range(game_duration):
            state1 = game_to_state(game)
            chosen_action = q.choose_action(state1, False)
            reward = 0
            first = True

            action = chosen_action
            while first or game.is_jumping > 0:
                first = False
                game.tick(action)
                v = game.player_status
                action = Actions.STAND
                if v == Status.HIT:
                    reward += -100
                elif v == Status.DODGED:
                    reward += 10
                elif v == Status.SHIELD_HIT:
                    reward += 1
            q.learn(state1, chosen_action, game_to_state(game), reward)
        print(a)

    save_agent(file_name + ".json", q.agent, game)