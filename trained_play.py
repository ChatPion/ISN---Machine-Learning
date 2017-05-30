from q_learning import load_agent, agent_exists, Agent, train
from ui import start_simulation

if agent_exists('save_file'):
    agent, _ = load_agent('save_file')
else:
    agent = Agent()

want_to_train = bool(input('Train ? '))
if want_to_train:
    agent = train(agent, 'save_file')

def choose_action(state):
    global agent
    return agent.choose_best_action(state)

start_simulation(choose_action)