from src.gamemodes import Gamemode
from src.text_generator import TextgenType
from src.statistics import Statistics
from blessed import Terminal

import src


class Program:
    
    def __init__(self):
        self.term = Terminal()
        self.state = src.state.MainMenu(self)
