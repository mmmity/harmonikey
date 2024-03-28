from unittest import TestCase
from src.text_generator import FileTextGenerator, TextgenType
from src.text_overseer import TextOverseer
from src.gamemodes import Gamemode
from src.state import Training
from src.exceptions import EndOfFile, WrongCharacter
from blessed.keyboard import Keystroke
from src.program import Program
import random
import os


class TestTextOverseer(TestCase):
    def create_text_file(self, text: str):
        # Adding random bytes to filename
        # so no collisions with existing files happen
        self.filename = random.randbytes(8).hex() + 'text'
        with open(self.filename + '.txt', 'w') as text_file:
            text_file.write(text)

    def clean_up(self):
        os.remove(self.filename + '.txt')

    def setUp(self):
        self.create_text_file('Lorem ipsum')

    def tearDown(self):
        self.clean_up()

    def test_shifting(self):
        training = Training(None,
                            Gamemode.NO_ERRORS,
                            self.filename,
                            TextgenType.FILE)
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
        training = Training(None,
                            Gamemode.NO_ERRORS,
                            self.filename,
                            TextgenType.FILE)
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
