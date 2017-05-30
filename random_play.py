import random

from shoot_game import Actions
from ui import start_simulation


def choose_action(state):
    return random.choice([Actions.STAND, Actions.JUMP])

start_simulation(choose_action)