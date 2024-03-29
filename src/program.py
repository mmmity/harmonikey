from src.gamemodes import Gamemode
from src.text_generator import TextgenType
from src.statistics import Statistics

import src


class Program:

    def __init__(self):
        self.state = src.state.BeforeTraining(self)
