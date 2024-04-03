from text_generator import TextGenerator
from state import Training
from blessed import keyboard
from gamemodes import Gamemode
from exceptions import WrongCharacter


class TextOverseer:
    '''
    Class that handles text input for training.
    Contains TextGenerator for generating text.
    Also contains strings "input", "current_word", "error"
    and Training to which is bound.
    '''
    def __init__(self, textgen: TextGenerator, training: Training):
        self.textgen: TextGenerator = textgen
        self.training: Training = training
        self.current_word: str = self.textgen.current_word()
        self.input: str = ''
        self.error: str = ''

    def __handle_backspace(self):
        '''
        Tries to erase last character from error
        if backspace was pressed
        '''
        if len(self.error) > 0:
            self.error = self.error[:-1]

    def __complete_word(self):
        '''
        Is called when current_word is fully typed by user.
        Modifies training.statistics and sets current_word to next word.
        Clears input.
        '''
        self.training.statistics.add_word(self.current_word)
        self.input = ''
        self.textgen.next_word()
        self.current_word = ' ' + self.textgen.current_word()

    def __try_add(self, key: keyboard.Keystroke) -> bool:
        '''
        Tries to add character into input if it is correct.
        Returns True if added, False otherwise
        '''
        needed_char = self.current_word[len(self.input)]
        if needed_char == key:
            self.input += key
            if self.input == self.current_word:
                self.__complete_word()

            return True
        return False

    def __handle_no_errors(self, key: keyboard.Keystroke):
        '''
        Is called if gamemode is NO_ERRORS
        '''
        self.__try_add(key)

    def __handle_fix_errors(self, key: keyboard.Keystroke):
        '''
        Is called if gamemode is FIX_ERRORS.
        Adds key to error if error is not empty
        or key does not match with current key from text.
        '''
        if self.training.gamemode == Gamemode.FIX_ERRORS and \
           len(self.error) > 0:
            self.error += key
            return

        if not self.__try_add(key):
            self.error += key

    def __handle_die_errors(self, key):
        '''
        Is called if gamemode is DIE_ERRORS.
        Raises WrongCharacter if key is incorrect.
        '''
        if not self.__try_add(key):
            raise WrongCharacter

    def handle_char(self, key: keyboard.Keystroke):
        '''
        Handles character from keyboard.
        Ignores everything except backspace, delete and printable.
        If backspace or delete, calls __handle_backspace().
        Otherwise calls respective handler for current gamemode.
        '''
        if key.name == 'KEY_BACKSPACE' or key.name == 'KEY_DELETE':
            self.__handle_backspace()
            return

        if key.is_sequence:
            return

        match self.training.gamemode:
            case Gamemode.NO_ERRORS:
                self.__handle_no_errors(key)
            case Gamemode.DIE_ERRORS:
                self.__handle_die_errors(key)
            case Gamemode.FIX_ERRORS:
                self.__handle_fix_errors(key)
            case _:
                raise ValueError("Unknown gamemode")
