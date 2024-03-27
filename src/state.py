from abc import ABC, abstractmethod
from src.gamemodes import Gamemode
from src.statistics import Statistics
from blessed.keyboard import Keystroke
from blessed import Terminal
from src.text_generator import *
from src.program import Program
from src.exceptions import *


class State(ABC):
    '''
    Abstract class, represents current state of program.
    Is inherited by classes Training, AfterTraining, MainMenu, BeforeTraining
    '''
    def __init__(self, program: Program):
        '''
        Contains program to which is bound.
        '''
        self.program = program

    @abstractmethod
    def visualize(self):
        '''
        Visualization of current state.
        '''
        pass

    @abstractmethod
    def handle_key(self, key: Keystroke):
        '''
        Handles pressed key.
        '''
        pass

    def switch(self, state):
        '''
        Switches state of self.program.
        '''
        self.program.state = state


class Exit(State):
    '''
    If program is in this state, it is ended.
    '''
    def __init__(self, program: Program):
        super().__init__(program)

    def visualize(self):
        '''
        Clears everything before exiting.
        '''
        term = Terminal()
        print(term.home + term.clear)
        pass

    def handle_key(self, key: Keystroke):
        pass


class Training(State):
    '''
    State representing training process.
    Attributes are:
        gamemode - gamemode of the training
        statistics - Statistics class for counting current stats
        text_overseer - TextOverseer for controlling typing
    '''
    def __init__(self, program: Program,
                 gamemode: Gamemode, train_filename: str,
                 textgen_type: TextgenType):
        '''
        Initializes stats, overseer.
        '''
        super().__init__(program)
        self.gamemode = gamemode
        if textgen_type == TextgenType.RANDOM:
            self.statistics = Statistics('mmmity',
                                         'RANDOM.' + train_filename, gamemode)
            textgen = RandomTextGenerator(train_filename + '.txt', 4)
        else:
            self.statistics = Statistics('mmmity', train_filename, gamemode)
            textgen = FileTextGenerator(train_filename + '.txt')
        import src.text_overseer
        self.text_overseer = src.text_overseer.TextOverseer(textgen, self)

    def __early_finish(self):
        '''
        Is called when training was forcefully stopped
        due to making an error when gamemode is NO_ERRORS.
        Does not save stats, just exits
        '''
        self.switch(Exit())

    def __finish(self):
        '''
        Is called when training was stopped
        due to finishing text file or timer expiring.
        Saves stats to stats file.
        '''
        self.statistics.save_to_file('stats.csv')
        self.switch(Exit(self.program))

    def handle_key(self, key: Keystroke):
        '''
        Redirects key to text_overseer.
        Catches all exceptions from it.
        '''
        try:
            self.text_overseer.handle_char(key)
        except WrongCharacter:
            self.__early_finish()
        except EndOfFile:
            self.__finish()

    def visualize(self):
        '''
        Visualizes training state.
        '''
        term = Terminal()
        # Terminal object that prints special characters

        print(term.hidden_cursor)
        print(term.home + term.clear + term.color_black())
        # Sets background color to black, clears, hides cursor

        print(term.white(str(round(self.statistics.get_elapsed_s(),
                                   2)) + ' s'))
        print(term.white(str(self.statistics.word_count) + ' words'))
        # Prints elapsed time and number of words typed

        words_before = self.text_overseer.textgen.words_before(2)
        words_before_text = term.gold3(' '.join(words_before))
        # To display two words before the current one
        # Is slightly dimmer than current word's color

        words_after = self.text_overseer.textgen.words_after(2)
        words_after_text = term.mistyrose4(' '.join(words_after))
        # To display two words after the current one
        # Is slightly dimmer than current word's color

        current_inputed = self.text_overseer.input
        current_error = self.text_overseer.error
        current_word = self.text_overseer.current_word
        current_left = current_word[len(current_inputed) + len(current_error):]
        # We want to display error characters atop untyped ones

        next_char = ''
        if current_error == '':
            next_char = current_left[0]
            current_left = current_left[1:]
        # If there is no error, we want to highlight current character

        word_center_text = \
            term.gold(current_inputed) + \
            term.tomato2(current_error) + \
            term.mistyrose3_on_white(next_char) + \
            term.mistyrose3(current_left)
        # Already typed characters are gold
        # Wrong characters are red
        # Highlighted character has white background
        # Untyped characters are gray (mistyrose)

        center_position = term.width // 2
        start_position = max(0, center_position -
                             len(self.text_overseer.current_word) // 2 -
                             term.length(words_before_text))
        # We want current word to be at the very center

        output = words_before_text + word_center_text + ' ' + words_after_text
        print(term.move_xy(start_position, term.height // 2) + output)
