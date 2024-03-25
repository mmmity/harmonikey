from abc import ABC
from src.gamemodes import Gamemode
from src.statistics import Statistics


class State(ABC):
    pass


class Training(State):

    def __init__(self, gamemode: Gamemode):
        self.gamemode = gamemode
        self.statistics = Statistics('mmmity', 'RANDOM.vocab', '')
