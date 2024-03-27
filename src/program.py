from src.gamemodes import Gamemode
from src.text_generator import TextgenType

import src


class Program:

    def __init__(self):
        self.state = src.state.Training(self,
                                        Gamemode.NO_ERRORS,
                                        'assets/texts/sample_text',
                                        TextgenType.FILE)
