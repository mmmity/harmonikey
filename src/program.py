from src.gamemodes import Gamemode
from src.text_generator import TextgenType

import src


class Program:

    def __init__(self):
        self.state = src.state.Training(
            program=self,
            gamemode=Gamemode.NO_ERRORS,
            train_filename='assets/texts/sample_text',
            textgen_type=TextgenType.FILE,
            timeout=15.0
        )
