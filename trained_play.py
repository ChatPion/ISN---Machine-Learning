from q_learning import load_agent
from ui import start_simulation

agent, _ = load_agent('save_file')

def choose_action(state):
    global agent
    return agent.choose_best_action(state)

start_simulation(choose_action)