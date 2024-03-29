from abc import ABC, abstractmethod
from src.gamemodes import Gamemode
from src.statistics import Statistics
from blessed.keyboard import Keystroke
from blessed import Terminal
from src.text_generator import FileTextGenerator, \
                               RandomTextGenerator, TextgenType
from src.program import Program
from src.exceptions import *
from threading import Timer
from src.widgets import Widget, Button, TextInput, Switch
from typing import List, Tuple


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

    @abstractmethod
    def handle_key(self, key: Keystroke):
        '''
        Handles pressed key.
        '''

    @abstractmethod
    def tick(self):
        '''
        Does something that needs to be done every program tick.
        '''

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

    def handle_key(self, key: Keystroke):
        pass

    def tick(self):
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
                 gamemode: Gamemode, train_filename: str, user: str,
                 textgen_type: TextgenType, timeout: float):
        '''
        Initializes stats, overseer.
        '''
        super().__init__(program)
        self.__updated_since = False
        # Variable to redraw everything when necessary, not every tick

        self.timeout: float = timeout
        self.gamemode: Gamemode = gamemode
        self.user: str = user
        if textgen_type == TextgenType.RANDOM:
            self.statistics = Statistics(
                user=self.user,
                text_tag='RANDOM.' + train_filename,
                mode=gamemode,
                timeout=self.timeout,
            )
            textgen = RandomTextGenerator(train_filename, 4)
        else:
            self.statistics = Statistics(
                user=self.user,
                text_tag=train_filename,
                mode=gamemode,
                timeout=self.timeout
            )
            textgen = FileTextGenerator(train_filename)

        from src.text_overseer import TextOverseer
        self.text_overseer = TextOverseer(textgen, self)

    def __early_finish(self):
        '''
        Is called when training was forcefully stopped
        due to making an error when gamemode is NO_ERRORS.
        Does not save stats, just exits
        '''
        self.statistics.freeze()
        self.switch(AfterTraining(self.program, self.statistics, True))

    def __finish(self):
        '''
        Is called when training was stopped
        due to finishing text file or timer expiring.
        Saves stats to stats file.
        '''
        self.statistics.freeze()
        self.statistics.save_to_file('stats.csv')
        self.switch(AfterTraining(self.program, self.statistics, False))

    def handle_key(self, key: Keystroke):
        '''
        Redirects key to text_overseer.
        Catches all exceptions from it.
        '''
        try:
            self.text_overseer.handle_char(key)
            self.__updated_since = False
            # We try to redraw words only after user pressed a key
        except WrongCharacter:
            self.__early_finish()
        except EndOfFile:
            self.__finish()

    def visualize(self):
        if not self.__updated_since:
            # We try not to revisualize everthing if not necessary
            self.__updated_since = True
            self.__visualize_words()
        self.__visualize_timer()
        # Although we need to redraw timer every tick so it is relevant

    def __visualize_timer(self):
        '''
        Only resets timer in the left top corner.
        '''
        term = Terminal()
        # Terminal object that prints special characters
        print(term.home)

        elapsed_str = format(self.statistics.get_elapsed_s(), '.2f')

        if self.timeout != 0.0:
            elapsed_str += ' / ' + format(self.timeout, '.2f')

        print(term.white(elapsed_str) + ' s')

    def __check_time(self):
        '''
        If time is up, finish training.
        '''
        if self.timeout != 0:
            if self.statistics.get_elapsed_s() > self.timeout:
                self.__finish()

    def tick(self):
        '''
        Only asks timer if time is up.
        '''
        self.__check_time()

    def __visualize_words(self):
        '''
        Visualizes training state.
        '''
        term = Terminal()
        # Terminal object that prints special characters

        print(term.home + term.clear)
        # Moves cursor clears

        self.__visualize_timer()
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


class AfterTraining(State):
    '''
    Class that represents state user gets directly after training.
    Just shows some statistics about training.
    Has two buttons: retry and main menu.
    Also has statistics from training
    and boolean 'is_early', which is True if training
    ended prematurely (due to error if mode was DIE_ERRORS).
    '''
    def __main_menu(self):
        '''
        Is called when 'Main menu' button is pressed.
        '''
        self.switch(Exit(self.program))

    def __restart(self):
        '''
        Is called when 'Restart' button is pressed.
        Restarts training with same parameters.
        '''
        textgen_type = TextgenType.FILE
        filename = self.stats.text_tag
        if self.stats.text_tag.startswith('RANDOM'):
            textgen_type = TextgenType.RANDOM
            filename = self.stats.text_tag[self.stats.text_tag.find('.') + 1:]

        new_training = Training(
            program=self.program,
            gamemode=self.stats.mode,
            user=self.stats.user,
            train_filename=filename,
            textgen_type=textgen_type,
            timeout=self.stats.timeout
        )

        self.switch(new_training)

    def __init__(self, program: Program, stats: Statistics, is_early: bool):
        '''
        Initializes all parameters
        '''
        super().__init__(program)
        self.stats: Statistics = stats
        self.is_early: bool = is_early
        self.widgets: List[Widget] = [
            Button(self.__restart, 'Restart'),
            Button(self.__main_menu, 'Main menu')
        ]
        self.active_widget: int = 0
        self.__updated_since: bool = False
        # This is used to optimize number of redraws

    def visualize(self):
        '''
        Prints statistics in center of screen.
        Prints two buttons in left-bottom and right-bottom corners.
        '''
        if not self.__updated_since:
            self.__updated_since = True
            term = Terminal()
            text_to_print = ''
            y_offset = 3

            if self.is_early:
                msg = term.red('GAME OVER')
                text_to_print += term.center(term.bold(msg))
            else:
                msg = term.green('TRAINING DONE')
                text_to_print += term.center(term.bold(msg))
            text_to_print += '\n'

            text_to_print += term.center(
                'On text ' + term.bold(self.stats.text_tag) +
                ' for user ' + term.bold(self.stats.user) +
                ' with mode ' + term.bold(str(self.stats.mode))
            )

            wpm_cpm = term.bold(format(self.stats.get_wpm(), '.2f'))
            wpm_cpm += ' wpm, '
            wpm_cpm += term.bold(format(self.stats.get_cpm(), '.2f'))
            wpm_cpm += ' cpm'
            text_to_print += term.center(wpm_cpm) + '\n'

            words_chars = term.bold(str(self.stats.word_count))
            words_chars += ' words, '
            words_chars += term.bold(str(self.stats.character_count))
            words_chars += ' characters'
            text_to_print += term.center(words_chars) + '\n'

            elapsed = term.bold(format(self.stats.get_elapsed_s(), '.2f'))
            text_to_print += term.center(elapsed + ' seconds')

            widgets_str = ''
            if self.active_widget == 0:
                widgets_str += term.ljust(self.widgets[0].visualize_str(True))
                widgets_str += term.rjust(self.widgets[1].visualize_str(False))
            else:
                widgets_str += term.ljust(self.widgets[0].visualize_str(False))
                widgets_str += term.rjust(self.widgets[1].visualize_str(True))

            print(term.clear + term.move_y(term.height // 2 - y_offset))
            print(text_to_print)
            print(term.move_y(term.height - 2))
            print(widgets_str)

    def handle_key(self, key: Keystroke):
        '''
        If key is left or right arrow, switches active button.
        Otherwise does nothing.
        '''
        match key.name:
            case 'KEY_LEFT':
                self.active_widget -= 1
                self.active_widget += len(self.widgets)
                self.active_widget %= len(self.widgets)
            case 'KEY_RIGHT':
                self.active_widget += 1
                self.active_widget %= len(self.widgets)
            case _:
                self.widgets[self.active_widget].handle_key(key)

        self.__updated_since = False

    def tick(self):
        pass


class BeforeTraining(State):
    '''
    State where training configuration is carried out
    Has two textInputs for player name and text file path
    Has two switches for choosing Gamemode and TextgenType
    Has two buttons: begin training and return to main menu
    Widgets are composed in grid, can be navigated left-right and top-bottom.
    '''
    MAX_SWITCH_WIDTH = 25
    # Is used for rjusting switches in visualize()

    def __begin_training(self):
        '''
        Switches program to new training with inputted parameters.
        '''
        match self.textgentype_switch.get_current_option():
            case TextgenType.FILE:
                filename = 'assets/texts/' + self.text_filepath.input
            case TextgenType.RANDOM:
                filename = 'assets/vocabs/' + self.text_filepath.input
            case _:
                raise TypeError("Unknown TextgenType")

        training = Training(
            program=self.program,
            gamemode=self.gamemode_switch.get_current_option(),
            user=self.player_name.input,
            train_filename=filename,
            textgen_type=self.textgentype_switch.get_current_option(),
            timeout=0.0,
        )
        self.switch(training)

    def __main_menu(self):
        '''
        Returns to main menu
        '''
        self.switch(Exit(self.program))

    def __init__(self, program: Program):
        '''
        Initializes all present widgets.
        Also groups them into grid for navigation.
        '''
        super().__init__(program)

        player_name_title = 'Input name:'
        self.player_name = TextInput(50, player_name_title)
        text_filepath_title = 'Input text file:assets/texts/'
        self.text_filepath = TextInput(50, text_filepath_title)
        gamemode_switch_title = 'Choose gamemode(z/x):'
        self.gamemode_switch = Switch(Gamemode, gamemode_switch_title)
        textgentype_switch_title = 'Choose text type(z/x):'
        self.textgentype_switch = Switch(TextgenType, textgentype_switch_title)
        begin_button_title = 'Begin'
        self.begin_button = Button(self.__begin_training, begin_button_title)
        return_button_title = 'Main menu'
        self.return_button = Button(self.__main_menu, return_button_title)

        self.grid: List[List[Widget]] = [
            [self.player_name, self.gamemode_switch],
            [self.text_filepath, self.textgentype_switch],
            [self.begin_button, self.return_button],
        ]
        self.active_widget_x: int = 0
        self.active_widget_y: int = 0

        self.__updated_since: bool = False

    def active_widget(self) -> Tuple[int, int]:
        '''
        Returns active widget coordinates in grid.
        '''
        return (self.active_widget_x, self.active_widget_y)

    def visualize(self):
        '''
        Prints all widgets except buttons in center left and center right.
        Prints buttons in left bottom and right bottom.
        '''
        if not self.__updated_since:
            self.__updated_since = True
            term = Terminal()
            text_to_print = term.move_y(term.height // 2)

            player_name = self.player_name.visualize_str(
                self.active_widget() == (0, 0)
            )
            text_to_print += term.ljust(player_name)

            gamemode_switch = self.gamemode_switch.visualize_str(
                self.active_widget() == (1, 0)
            )
            gamemode_switch = term.ljust(gamemode_switch,
                                         self.MAX_SWITCH_WIDTH)
            text_to_print += term.rjust(gamemode_switch)

            text_to_print += '\n\n'

            text_filepath = self.text_filepath.visualize_str(
                self.active_widget() == (0, 1)
            )
            text_to_print += term.ljust(text_filepath)

            textgentype_switch = self.textgentype_switch.visualize_str(
                self.active_widget() == (1, 1)
            )
            textgentype_switch = term.ljust(textgentype_switch,
                                            self.MAX_SWITCH_WIDTH)
            text_to_print += term.rjust(textgentype_switch)

            text_to_print += term.move_xy(0, term.height - 2)

            begin_button = self.begin_button.visualize_str(
                self.active_widget() == (0, 2)
            )
            text_to_print += term.ljust(begin_button)

            return_button = self.return_button.visualize_str(
                self.active_widget() == (1, 2)
            )
            text_to_print += term.rjust(return_button)

            print(term.clear + text_to_print)

    def handle_key(self, key: Keystroke):
        match key.name:
            case 'KEY_LEFT':
                self.active_widget_x -= 1
                self.active_widget_x += len(self.grid[0])
                self.active_widget_x %= len(self.grid[0])
            case 'KEY_RIGHT':
                self.active_widget_x += 1
                self.active_widget_x %= len(self.grid[0])
            case 'KEY_UP':
                self.active_widget_y -= 1
                self.active_widget_y += len(self.grid)
                self.active_widget_y %= len(self.grid)
            case 'KEY_DOWN':
                self.active_widget_y += 1
                self.active_widget_y %= len(self.grid)
            case _:
                widget = self.grid[self.active_widget_y][self.active_widget_x]
                widget.handle_key(key)

        self.__updated_since = False

    def tick(self):
        match self.textgentype_switch.get_current_option():
            case TextgenType.FILE:
                self.text_filepath.title = 'Input text file:assets/texts/'
            case TextgenType.RANDOM:
                self.text_filepath.title = 'Input text file:assets/vocabs/'
