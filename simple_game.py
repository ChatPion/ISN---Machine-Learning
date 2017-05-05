import random as rand

def clamp(a, b, p):
    return min(max(p, a), b)

class Game:
    def __init__(self):
        self.pos = rand.choice([-2, -1, 0, 1, 2])

    def move(self, dir):
        self.pos += dir
        self.pos = clamp(-2, 2, self.pos)

    def has_lost(self):
        return int(abs(self.pos)) == 2


def choose_action(values, pos, real):
    if real or rand.uniform(0, 1) < 0.8: # GREEDY
        dir = 1
        left = values[clamp(0, 4, pos + 1)]
        right = values[clamp(0, 4, pos + 3)]
        if left > right:
            dir = -1
        return dir
    return rand.choice([-1, 1])


states_values = [0 for x in range(5)]

nb_games = 1000

for i in range(nb_games):
    game = Game()
    for t in range(1000):
        alpha = 0.3
        gamma = 0.8

        dir = choose_action(states_values, game.pos, False)
        game.move(dir)
        reward = 0
        if game.has_lost():
            reward = -10

        states_values[game.pos + 2 - dir] += alpha * (reward + gamma * states_values[game.pos + 2] - states_values[game.pos + 2 - dir])

print(states_values)

game = Game()
print(game.pos)
for t in range(10):
    game.move(choose_action(states_values, game.pos, True))
    print(game.pos)