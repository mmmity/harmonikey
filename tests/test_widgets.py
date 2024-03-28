import unittest
from blessed import Terminal
from blessed.keyboard import Keystroke
from src.widgets import Button, TextInput


class TestButton(unittest.TestCase):

    def test_visualize(self):
        btn = Button(None, 'button')
        self.assertEqual(btn.visualize_str(False), 'button')

        term = Terminal()
        active_ans = term.on_cyan3('button')
        self.assertEqual(btn.visualize_str(True), active_ans)

    def test_handle(self):

        def fn(self):
            self.dummy = 'dummy'

        self.dummy = ''
        btn = Button(lambda: fn(self), 'button')
        btn.handle_key(Keystroke('4'))
        self.assertEqual(self.dummy, '')
        btn.handle_key(Keystroke('\n', name='KEY_ENTER'))
        self.assertEqual(self.dummy, 'dummy')


class TestTextInput(unittest.TestCase):

    def test_handle(self):
        text_input = TextInput()

        text_input.handle_key(Keystroke('a'))
        text_input.handle_key(Keystroke('b'))
        self.assertEqual(text_input.input, 'ab')

        text_input.handle_key(Keystroke(name='KEY_BACKSPACE'))
        self.assertEqual(text_input.input, 'a')
        text_input.handle_key(Keystroke(name='KEY_DELETE'))
        self.assertEqual(text_input.input, '')

    def test_visualize(self):
        text_input = TextInput()
        text_input.handle_key(Keystroke('a'))

        self.assertEqual(text_input.visualize_str(False), 'a')

        term = Terminal()
        active_ans = term.on_deepskyblue3('a') + term.on_white(' ')
        self.assertEqual(text_input.visualize_str(True), active_ans)
