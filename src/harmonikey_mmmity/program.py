from blessed import Terminal

class Program:

    def __init__(self):
        self.term = Terminal()

        import state
        self.state = state.MainMenu(self)
