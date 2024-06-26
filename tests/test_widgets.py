import unittest
from blessed import Terminal
from blessed.keyboard import Keystroke
from harmonikey_mmmity.widgets import Button, TextInput, NumberInput, Switch
from enum import Enum


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
        text_input = TextInput(50)

        text_input.handle_key(Keystroke('a'))
        text_input.handle_key(Keystroke('b'))
        self.assertEqual(text_input.input, 'ab')

        text_input.handle_key(Keystroke(name='KEY_BACKSPACE'))
        self.assertEqual(text_input.input, 'a')
        text_input.handle_key(Keystroke(name='KEY_DELETE'))
        self.assertEqual(text_input.input, '')

    def test_visualize(self):
        text_input = TextInput(50)
        text_input.handle_key(Keystroke('a'))

        self.assertEqual(text_input.visualize_str(False), 'a')

        term = Terminal()
        active_ans = term.on_cyan3('a') + term.on_white(' ')
        self.assertEqual(text_input.visualize_str(True), active_ans)

    def test_limit(self):
        text_input = TextInput(2)
        text_input.handle_key(Keystroke('a'))
        text_input.handle_key(Keystroke('b'))
        text_input.handle_key(Keystroke('c'))
        text_input.handle_key(Keystroke('d'))
        self.assertEqual(text_input.input, 'ab')


class TestNumberInput(unittest.TestCase):

    def test_handle(self):
        number_input = NumberInput(50)

        number_input.handle_key(Keystroke('1'))
        number_input.handle_key(Keystroke('2'))
        self.assertEqual(number_input.input, '12')
        self.assertEqual(number_input.int_input(), 12)

        number_input.handle_key(Keystroke('a'))
        self.assertEqual(number_input.input, '12')
        self.assertEqual(number_input.int_input(), 12)

        number_input.handle_key(Keystroke(name='KEY_BACKSPACE'))
        self.assertEqual(number_input.input, '1')

    def test_visualize(self):
        term = Terminal()
        number_input = NumberInput(50, 'title', '12')
        self.assertEqual(number_input.visualize_str(False), 'title12')

        number_input.handle_key(Keystroke('1'))
        self.assertEqual(number_input.visualize_str(False), 'title1')

        active_exp = term.on_cyan3('title1') + term.on_white(' ')
        self.assertEqual(number_input.visualize_str(True), active_exp)

    def test_int_input(self):
        number_input = NumberInput(50, 'title', '12')
        self.assertEqual(number_input.int_input(), 12)
        number_input.handle_key(Keystroke('1'))
        self.assertEqual(number_input.int_input(), 1)


class TestSwitch(unittest.TestCase):

    def setUp(self):
        self.enum = Enum('Test', ['opt1', 'opt2', 'opt3'])
        self.switch = Switch(self.enum)

    def test_visualize(self):
        term = Terminal()
        self.assertEqual(self.switch.visualize_str(False), 'Test.opt1')

        active_expected = term.on_cyan3('Test.opt1')
        self.assertEqual(self.switch.visualize_str(True), active_expected)

    def test_handle_key(self):
        self.assertEqual(self.switch.get_current_option(), self.enum.opt1)
        self.switch.handle_key(Keystroke('x'))
        self.assertEqual(self.switch.get_current_option(), self.enum.opt2)
        self.switch.handle_key(Keystroke('x'))
        self.assertEqual(self.switch.get_current_option(), self.enum.opt3)
        self.switch.handle_key(Keystroke('x'))
        self.assertEqual(self.switch.get_current_option(), self.enum.opt1)

        self.switch.handle_key(Keystroke('z'))
        self.assertEqual(self.switch.get_current_option(), self.enum.opt3)
        self.switch.handle_key(Keystroke('z'))
        self.assertEqual(self.switch.get_current_option(), self.enum.opt2)
        self.switch.handle_key(Keystroke('z'))
        self.assertEqual(self.switch.get_current_option(), self.enum.opt1)
