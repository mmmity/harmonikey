from unittest import TestCase
from harmonikey_mmmity.text_generator import TextgenType
from harmonikey_mmmity.gamemodes import Gamemode
from harmonikey_mmmity.state import Training
from harmonikey_mmmity.exceptions import EndOfFile, WrongCharacter
from blessed.keyboard import Keystroke
import random
import os


class TestTextOverseer(TestCase):
    def create_text_file(self, text: str):
        # Adding random bytes to filename
        # so no collisions with existing files happen
        self.filename = random.randbytes(8).hex() + 'text.txt'
        with open(self.filename, 'w') as text_file:
            text_file.write(text)

    def clean_up(self):
        os.remove(self.filename)

    def setUp(self):
        self.create_text_file('Lorem ipsum')

    def tearDown(self):
        self.clean_up()

    def test_shifting(self):
        training = Training(
            program=None,
            gamemode=Gamemode.NO_ERRORS,
            train_filename=self.filename,
            user='mmmity',
            textgen_type=TextgenType.FILE,
            timeout=0.0
        )
        overseer = training.text_overseer

        self.assertEqual(overseer.current_word, 'Lorem')
        for c in 'Lorem':
            overseer.handle_char(Keystroke(c))

        self.assertEqual(overseer.input, '')
        self.assertEqual(overseer.current_word, ' ipsum')
        self.assertEqual(training.statistics.word_count, 1)

        for c in ' ipsu':
            overseer.handle_char(Keystroke(c))

        with self.assertRaises(EndOfFile):
            overseer.handle_char(Keystroke('m'))
        self.assertEqual(training.statistics.word_count, 2)

    def test_no_errors(self):
        training = Training(
            program=None,
            gamemode=Gamemode.NO_ERRORS,
            train_filename=self.filename,
            user='mmmity',
            textgen_type=TextgenType.FILE,
            timeout=0.0
        )
        overseer = training.text_overseer

        for c in 'Lor':
            overseer.handle_char(Keystroke(c))
        self.assertEqual(overseer.input, 'Lor')
        overseer.handle_char(Keystroke('E'))
        overseer.handle_char(Keystroke('\x08'))
        self.assertEqual(overseer.input, 'Lor')
        self.assertEqual(overseer.error, '')
        overseer.handle_char(Keystroke('e'))
        self.assertEqual(overseer.input, 'Lore')
        self.assertEqual(overseer.error, '')

    def test_fix_errors(self):
        training = Training(
            program=None,
            gamemode=Gamemode.FIX_ERRORS,
            train_filename=self.filename,
            user='mmmity',
            textgen_type=TextgenType.FILE,
            timeout=0.0
        )
        overseer = training.text_overseer

        for c in 'Lor':
            overseer.handle_char(Keystroke(c))
        overseer.handle_char(Keystroke('E'))
        self.assertEqual(overseer.input, 'Lor')
        self.assertEqual(overseer.error, 'E')
        overseer.handle_char(Keystroke('e'))
        self.assertEqual(overseer.error, 'Ee')
        overseer.handle_char(Keystroke(name='KEY_BACKSPACE'))
        self.assertEqual(overseer.error, 'E')
        overseer.handle_char(Keystroke(name='KEY_DELETE'))
        self.assertEqual(overseer.error, '')

    def test_die_errors(self):
        training = Training(
            program=None,
            gamemode=Gamemode.DIE_ERRORS,
            train_filename=self.filename,
            user='mmmity',
            textgen_type=TextgenType.FILE,
            timeout=0.0
        )
        overseer = training.text_overseer
        for c in 'Lor':
            overseer.handle_char(Keystroke(c))
        with self.assertRaises(WrongCharacter):
            overseer.handle_char(Keystroke('E'))
