from blessed import Terminal
from blessed.keyboard import Keystroke
from abc import ABC, abstractmethod
from typing import Callable
from enum import Enum, EnumType
from typing_extensions import override
from string import digits


class Widget(ABC):
    '''
    This class represents a single widget: button or text input.
    '''

    @abstractmethod
    def visualize_str(is_active: bool) -> str:
        '''
        Returns formatted str for blessed terminal interface.
        It is then printed in state widget belongs to.
        '''

    @abstractmethod
    def handle_key(key: Keystroke):
        '''
        Handles key given from parent state.
        '''


class Button(Widget):
    '''
    Represents a button, which has a press handler on_press.
    Also has a title str.
    '''
    def __init__(self, on_press: Callable, title: str):
        '''
        Initializes on_press and title.
        '''
        self.on_press: Callable = on_press
        self.title: str = title

    def visualize_str(self, is_active: bool) -> str:
        '''
        Returns title.
        If button is active, text is highlighted with cyan.
        '''
        term = Terminal()
        if is_active:
            return term.on_cyan3(self.title)
        return self.title

    def handle_key(self, key: Keystroke):
        '''
        If key is Enter, calls on_press.
        Does nothing otherwise.
        '''
        if key.name == 'KEY_ENTER':
            self.on_press()


class TextInput(Widget):
    '''
    Represents a one-row text input field.
    Has currently inputted text as 'input' str.
    Also has limited length of input.
    '''
    def __init__(self, limit: int, title: str = ''):
        '''
        Initializes input with empty string and limit with number
        '''
        self.input: str = ''
        self.limit: int = limit
        self.title: str = title

    def visualize_str(self, is_active: bool) -> str:
        '''
        Returns input.
        If active, text is highlighted with cyan
        and the cursor is also highlighted.
        '''
        term = Terminal()
        text = self.title + self.input
        if is_active:
            return term.on_cyan3(text) + term.on_white(' ')
        return text

    def handle_key(self, key: Keystroke):
        '''
        If key is printable char, adds it to input.
        If it is Backspace|Delete, removes last char from input.
        Otherwise does nothing.
        '''

        if key.name == 'KEY_BACKSPACE' or key.name == 'KEY_DELETE':
            self.input = self.input[:-1]

        if key.is_sequence:
            return

        if len(self.input) < self.limit:
            self.input += key


class NumberInput(TextInput):
    '''
    Like TextInput, but accepts only numbers.
    Has int_input method, that returns int(input).
    Also has default str, which is visualized instead of input
    if latter is empty.
    '''
    def __init__(self, limit: int, title: str = '', default: str = ''):
        '''
        Just initializes TextInput.
        '''
        super().__init__(limit, title)
        self.default: str = default

    @override
    def handle_key(self, key: Keystroke):
        '''
        Like from TextInput, but accepts only numeric characters.
        '''

        if key.name == 'KEY_BACKSPACE' or key.name == 'KEY_DELETE':
            self.input = self.input[:-1]

        if key.is_sequence or key not in digits:
            return

        if len(self.input) < self.limit:
            self.input += key

    @override
    def visualize_str(self, is_active: bool) -> str:
        '''
        Returns input, or default if former is empty.
        If active, text is highlighted with cyan
        and the cursor is also highlighted.
        '''
        term = Terminal()
        if self.input == '':
            text = self.title + self.default
        else:
            text = self.title + self.input

        if is_active:
            return term.on_cyan3(text) + term.on_white(' ')
        return text

    def int_input(self) -> int:
        '''
        Returns int(input)
        '''
        if self.input == '':
            return int(self.default)
        return int(self.input)


class Switch(Widget):
    '''
    This class represents switch widget.
    Has Enum of options and current option.
    Can switch back and forth using keys 'z' and 'x'
    '''
    def __init__(self, options: EnumType, title: str = ''):
        '''
        Initializes options and current_option
        '''
        self.options: EnumType = options
        self.current_option: int = 1
        self.title: str = title

    def visualize_str(self, is_active: bool) -> str:
        '''
        Returns name of current_option.
        If is_active == True, it is highlighted with cyan
        '''
        term = Terminal()
        text = self.title + str(self.options(self.current_option))
        if is_active:
            return term.on_cyan3(text)
        return text

    def __move_forth(self):
        '''
        Switches current_option to next
        '''
        self.current_option %= len(self.options)
        self.current_option += 1

    def __move_back(self):
        '''
        Switches current_option to previous
        '''
        self.current_option -= 1
        self.current_option += len(self.options) - 1
        self.current_option %= len(self.options)
        self.current_option += 1

    def handle_key(self, key: Keystroke):
        '''
        If key is z, switches back, x - forth.
        Otherwise does nothing
        '''
        if key == 'z':
            self.__move_back()
        elif key == 'x':
            self.__move_forth()

    def get_current_option(self):
        return self.options(self.current_option)
