from blessed import Terminal

class Program:

    def __init__(self):
        self.term = Terminal()

        import harmonikey_mmmity.state
        self.state = harmonikey_mmmity.state.MainMenu(self)
