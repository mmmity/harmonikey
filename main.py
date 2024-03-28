from src.program import Program
from blessed import Terminal
from src.state import Exit

if __name__ == '__main__':

    term = Terminal()

    program = Program()
    program.state.visualize()
    with term.cbreak(), term.hidden_cursor():
        # Makes terminal catch all keyboard keys without printing them

        while True:
            key = term.inkey(timeout=0.05)
            # Reloads terminal every 0.05 s
            # to update timer

            if key != '':
                program.state.handle_key(key)

            program.state.visualize()

            if isinstance(program.state, Exit):
                break
