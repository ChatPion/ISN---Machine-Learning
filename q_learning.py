import random as rand
from shoot_game import Game, Status

# state : ((bullet1, bullet2, bullet3, bullet4), (shield1, shield2))
# bullet : [0, 5] (6 : too far)
# shield1 : [0, 2] (0 : on)
# shield2 : [0, 4]

STAND = 0
JUMP = 1

class QLearning:
    
    def __init__(self, alpha, gamma, actions_value=None):
        """
        alpha: learning rate
        gamme: discount rate
        """
        self.alpha = alpha
        self.gamma = gamma
        self.actions_value = {}
        if actions_value is not None:
            self.actions_value = actions_value
    
    def get_value(self, state, action=None):
        if state not in self.actions_value:
            self.actions_value[state] = [0, 0]
        ret = self.actions_value[state]
        if action is not None:
            ret = ret[action]
        return ret
        
    def set_value(self, state, action, value):
        self.actions_value[state][action] = value
        
    def learn(self, state_1, action_1, state_2, reward):
        current = self.get_value(state_1, action_1)
        max_t2_val = max(self.get_value(state_2))
        new_val = current + self.alpha * (reward + self.gamma * max_t2_val - current)
        self.set_value(state_1, action_1, new_val)
                
    def choose_action(self, state, real):
        if real or rand.uniform(0, 1) < 0.8: # GREEDY
            stand_val = self.get_value(state, STAND)
            jump_val = self.get_value(state, JUMP)
            if stand_val >= jump_val:
                return STAND
            return JUMP
        # exploration
        return rand.choice([STAND, JUMP])
        
        
MAX_VISION = 5

def bullet_pos(bullets, index):
    if index >= len(bullets):
        return MAX_VISION
    return min(abs(bullets[index][0]), MAX_VISION)

def game_to_state(game):
    b = game.bullets
    watched_bullets = (bullet_pos(b, 0), bullet_pos(b, 1), bullet_pos(b, 2), bullet_pos(b, 3))
    shields = tuple(game.shields)
    return (watched_bullets, shields)
    
        
## GAME LOOP
game = Game(1, 10)
q = QLearning(0.3, 0.8)

hit_nb = [0] * 10

for i in range(10000):

    state1 = game_to_state(game)
    chosen_action = q.choose_action(state1, False)
    reward = 0
    first = True

    action = chosen_action
    while first or game.is_jumping > 0:
        first = False
        game.tick(action)
        v = game.player_status
        action = STAND
        if v == Status.HIT:
            reward += -100
        else:
            reward += 10
    q.learn(state1, chosen_action, game_to_state(game), reward)

for i in range(1000):
    state1 = game_to_state(game)
    chosen_action = q.choose_action(state1, True)
    first = True

    action = chosen_action
    while first or game.is_jumping > 0:
        first = False
        game.tick(action)
        v = game.player_status
        action = STAND
        if v == Status.HIT:
            hit_nb[i // 1000] += 1
    
print(hit_nb)
print(q.actions_value)
