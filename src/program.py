from blessed import Terminal

import src


class Program:

    def __init__(self):
        self.term = Terminal()
        self.state = src.state.MainMenu(self)
