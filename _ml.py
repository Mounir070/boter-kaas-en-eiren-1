from collections import defaultdict
from typing import Dict, Tuple, List

import jsons
import matplotlib.pyplot as plt

from _core import start
from _agent import RandomAgent, MLAgent, Agent
from _typing import PLAYER_X, PLAYER_O
from _ui import HEADLESS


def train(agent: Agent, iterations: int):
    for _ in range(iterations):
        start(player_x=agent, player_o=agent, ui=HEADLESS)


def validate(agent_x: Agent, agent_o: Agent, iterations: int) -> Dict[str, float]:
    winners = defaultdict(int)
    for i in range(iterations):
        winner = start(player_x=agent_x, player_o=agent_o, ui=HEADLESS)
        winners[winner] += 1
    winners[PLAYER_X] /= iterations
    winners[PLAYER_O] /= iterations
    winners[None] /= iterations
    return winners


def train_and_validate(
        agent: Agent,
        validation_agent: Agent,
        iterations=1000,
        trainings=20,
        validations=100) -> Tuple[list, list, list, list]:
    data_epochs = []
    data_agent_wins = []
    data_validation_agent_wins = []
    data_evens = []

    for i in range(iterations + 1):
        # Validate first, so we can capture the initial performance of the agent.
        agent.learning = False

        winners1 = validate(agent_x=agent, agent_o=validation_agent, iterations=int(validations / 2))
        winners2 = validate(agent_x=validation_agent, agent_o=agent, iterations=int(validations / 2))

        data_agent_wins.append((winners1[PLAYER_X] + winners2[PLAYER_O]) / 2)
        data_validation_agent_wins.append((winners1[PLAYER_O] + winners2[PLAYER_X]) / 2)
        data_evens.append((winners1[None] + winners2[None]) / 2)

        data_epochs.append(i * trainings)

        # Next, start the training.
        agent.learning = True
        train(agent, trainings)

        print(f'Finished iteration {i}/{iterations}')

    return data_agent_wins, data_validation_agent_wins, data_evens, data_epochs


def plot_validation(validation: dict):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'x wins', 'o wins', 'even'
    sizes = [
        validation[PLAYER_X] * 100,
        validation[PLAYER_O] * 100,
        validation[None] * 100
    ]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()


def plot_validations(data_agent_wins: List[float],
                     data_validation_agent_wins: List[float],
                     data_evens: List[float],
                     data_epochs: List[float]):
    fig, ax = plt.subplots()

    l_evens = ax.plot(data_epochs, data_evens)
    l_loses = ax.plot(data_epochs, data_validation_agent_wins)
    l_wins = ax.plot(data_epochs, data_agent_wins)
    ax.legend((l_wins[0], l_loses[0], l_evens[0]),
              ('win rate', 'loss rate', 'even rate'), loc='right', shadow=True)
    plt.title('Training Progress')
    plt.xlabel('Trainings')
    plt.ylabel('Rating')
    ax.grid()
    plt.show()


def train_and_plot(
        agent: Agent,
        validation_agent: Agent,
        iterations=1000,
        trainings=20,
        validations=100):
    train_results = train_and_validate(agent,
                                       validation_agent,
                                       iterations,
                                       trainings,
                                       validations)
    plot_validations(*train_results)


def save(agent: MLAgent, path: str):
    if not isinstance(agent, MLAgent):
        raise AttributeError(f'agent must be an MLAgent, got {type(agent)} instead')
    dumped = jsons.dumps(agent, verbose=jsons.Verbosity.WITH_CLASS_INFO)
    with open(path, 'w') as f:
        f.write(dumped)


def load(path: str) -> MLAgent:
    with open(path, 'r') as f:
        return jsons.loads(f.read())
