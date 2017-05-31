from shoot_game import Actions
from ui import start_simulation


def choose_action(state):
    return Actions.JUMP

start_simulation(choose_action)
