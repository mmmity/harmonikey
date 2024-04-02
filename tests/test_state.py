import unittest
from unittest.mock import patch, MagicMock, Mock
from src.state import Exit, Training, AfterTraining, \
                      BeforeTraining, MainMenu, StatsScreen
from src.gamemodes import Gamemode
from src.text_generator import TextgenType
from blessed.keyboard import Keystroke
import random
import os
import time


class TestState(unittest.TestCase):

    @patch('src.program.Program')
    def test_switch(self, mockProgram):
        mp = mockProgram()
        state = Exit(mp)
        mp.state = state
        anotherState = Exit(mp)

        self.assertIs(mp.state, state)
        self.assertIsNot(mp.state, anotherState)
        state.switch(anotherState)
        self.assertIsNot(mp.state, state)
        self.assertIs(mp.state, anotherState)


class TestExit(unittest.TestCase):

    @patch('src.program.Program')
    def test_visualize(self, mockProgram):
        mp = mockProgram()
        exit = Exit(mp)
        mp.term = MagicMock()
        mp.term.home = MagicMock()
        mp.term.home.__add__ = Mock()
        mp.term.clear = MagicMock()
        exit.visualize()
        mp.term.home.__add__.assert_called_once_with(mp.term.clear)


class TestTraining(unittest.TestCase):

    def create_text_file(self, text: str):
        self.filename = random.randbytes(8).hex() + '.txt'
        with open(self.filename, 'w') as out_file:
            out_file.write(text)

    def clean_up(self):
        os.remove(self.filename)

    @patch('src.program.Program')
    @patch('src.program.Program')
    def setUp(self, mockProgram1, mockProgram2):
        self.create_text_file('a b')
        self.training1 = Training(
            mockProgram1,
            Gamemode.FIX_ERRORS,
            self.filename,
            'user',
            TextgenType.RANDOM,
            0.0
        )
        self.training2 = Training(
            mockProgram2,
            Gamemode.DIE_ERRORS,
            self.filename,
            'user',
            TextgenType.FILE,
            1.0
        )

    def tearDown(self):
        self.clean_up()

    def test_init(self):
        self.assertEqual(self.training1.statistics.text_tag, 'RANDOM.' + self.filename)

    def test_handle_key_fix_errors(self):
        self.training1.handle_key(Keystroke('c'))
        self.training1.handle_key(Keystroke('a'))
        self.training1.handle_key(Keystroke('b'))
        self.assertEqual(self.training1.text_overseer.error, 'cab')
        self.training1.handle_key(Keystroke(name='KEY_BACKSPACE'))
        self.assertEqual(self.training1.text_overseer.error, 'ca')

    def test_handle_key_die_errors(self):
        program = self.training2.program
        self.training2.handle_key(Keystroke('c'))
        self.assertIsInstance(program.state, AfterTraining)
        self.assertEqual(program.state.is_early, True)

    def test_handle_key_finish(self):
        self.training2.statistics = MagicMock()
        program = self.training2.program

        self.training2.handle_key(Keystroke('a'))
        self.training2.handle_key(Keystroke(' '))
        self.training2.handle_key(Keystroke('b'))

        self.assertIsInstance(program.state, AfterTraining)
        self.assertEqual(program.state.is_early, False)
        self.training2.statistics.save_to_file.assert_called_once()

    def test_updated_since(self):
        self.training1._Training__visualize_timer = Mock()
        self.training1._Training__visualize_words = Mock()
        self.training1.visualize()
        self.training1._Training__visualize_timer.assert_called()
        self.training1._Training__visualize_words.assert_called()
        self.training1.visualize()
        self.training1._Training__visualize_words.assert_called_once()
        self.training1.handle_key(Keystroke('a'))
        self.training1.visualize()
        self.training1._Training__visualize_words.assert_called()

    def test_visualize_timer(self):
        self.training1._Training__visualize_timer()
        self.training1.program.term.white.assert_called()
        callstr1 = self.training1.program.term.white.call_args_list[0]
        self.assertNotIn('/', str(callstr1))
        self.assertIn('.', str(callstr1))
        self.training2._Training__visualize_timer()
        self.training2.program.term.white.assert_called()
        callstr2 = self.training2.program.term.white.call_args_list[0]
        self.assertIn('/', str(callstr2))
        self.assertIn('.', str(callstr2))

    def test_check_time(self):
        time.sleep(1)
        self.training2._Training__check_time()
        self.assertIsInstance(self.training2.program.state, AfterTraining)

    def test_visualize_words(self):
        term = self.training2.program.term
        term.width = 10
        term.length = lambda x: 2
        self.training2._Training__visualize_words()
        term.move_xy().__add__.assert_called_with(
            term.gold3().__add__().__add__().__add__()
        )


class TestAfterTraining(unittest.TestCase):

    def create_text_file(self, text: str):
        self.filename = random.randbytes(8).hex() + '.txt'
        with open(self.filename, 'w') as out_file:
            out_file.write(text)

    def clean_up(self):
        os.remove(self.filename)

    @patch('src.program.Program')
    @patch('src.statistics.Statistics')
    def setUp(self, mockProgram, mockStats):
        self.at1 = AfterTraining(mockProgram, mockStats, True)
        self.at2 = AfterTraining(mockProgram, mockStats, False)
        self.create_text_file('a b')

    def tearDown(self):
        self.clean_up()

    def test_restart(self):
        self.at1.program.state = self.at1
        self.at1.stats.text_tag = 'RANDOM.' + self.filename
        self.at1._AfterTraining__restart()
        self.assertIsInstance(self.at1.program.state, Training)

    def test_visualize(self):
        self.at1.stats.get_wpm = lambda: 0
        self.at2.stats.get_cpm = lambda: 0
        self.at1.stats.get_wpm = lambda: 0
        self.at2.stats.get_cpm = lambda: 0
        self.at1.stats.get_elapsed_s = lambda: 0
        self.at2.stats.get_elapsed_s = lambda: 0
        self.at1.visualize()
        self.at2.visualize()
        self.at1.program.term.move_y.assert_any_call(self.at1.program.term.height // 2 - 3)
        self.at1.program.term.move_y.assert_any_call(self.at1.program.term.height - 2)
        self.at2.program.term.move_y.assert_any_call(self.at1.program.term.height // 2 - 3)
        self.at2.program.term.move_y.assert_any_call(self.at1.program.term.height - 2)

    def test_handle_key(self):
        self.at1.widgets = [1, 2, 2]
        self.assertEqual(self.at1.active_widget, 0)
        self.at1.handle_key(Keystroke(name='KEY_LEFT'))
        self.assertEqual(self.at1.active_widget, 2)
        self.at1.handle_key(Keystroke(name='KEY_LEFT'))
        self.assertEqual(self.at1.active_widget, 1)
        self.at1.handle_key(Keystroke(name='KEY_LEFT'))
        self.assertEqual(self.at1.active_widget, 0)

        self.at1.handle_key(Keystroke(name='KEY_RIGHT'))
        self.assertEqual(self.at1.active_widget, 1)
        self.at1.handle_key(Keystroke(name='KEY_RIGHT'))
        self.assertEqual(self.at1.active_widget, 2)
        self.at1.handle_key(Keystroke(name='KEY_RIGHT'))
        self.assertEqual(self.at1.active_widget, 0)


class TestBeforeTraining(unittest.TestCase):

    @patch('src.program.Program')
    def setUp(self, mockProgram):
        self.bt = BeforeTraining(mockProgram)
        self.bt.program.state = self.bt

    def test_begin(self):
        self.bt.filename = random.randbytes(8).hex()
        self.bt.textgentype_switch.get_current_option = lambda: TextgenType.FILE
        self.bt._BeforeTraining__begin_training()
        self.assertEqual(self.bt.program.state, self.bt)

    def test_visualize(self):
        self.bt.player_name = Mock()
        self.bt.gamemode_switch = Mock()
        self.bt.text_filepath = Mock()
        self.bt.textgentype_switch = Mock()
        self.bt.timeout = Mock()
        self.bt.begin_button = Mock()
        self.bt.return_button = Mock()

        self.bt.visualize()

        self.bt.player_name.visualize_str.assert_called()
        self.bt.gamemode_switch.visualize_str.assert_called()
        self.bt.text_filepath.visualize_str.assert_called()
        self.bt.textgentype_switch.visualize_str.assert_called()
        self.bt.timeout.visualize_str.assert_called()
        self.bt.begin_button.visualize_str.assert_called()
        self.bt.return_button.visualize_str.assert_called()

        self.bt.program.term.clear.__add__.assert_called()

    def test_handle_key(self):
        self.assertEqual(self.bt.active_widget_x, 0)

        for i in range(1, 3):
            self.bt.handle_key(Keystroke(name='KEY_RIGHT'))
            self.assertEqual(self.bt.active_widget_x, i % 2)

        for i in range(1, -1):
            self.bt.handle_key(Keystroke(name='KEY_LEFT'))
            self.assertEqual(self.bt.active_widget_x, i)

        self.assertEqual(self.bt.active_widget_y, 0)

        for i in range(1, 5):
            self.bt.handle_key(Keystroke(name='KEY_DOWN'))
            self.assertEqual(self.bt.active_widget_y, i % 4)

        for i in range(4, -1):
            self.bt.handle_key(Keystroke(name='KEY_UP'))
            self.assertEqual(self.bt.active_widget_y, i)


class TestMainMenu(unittest.TestCase):

    @patch('src.program.Program')
    def setUp(self, mockProgram):
        self.mm = MainMenu(mockProgram)

    def test_visualize(self):
        self.mm.program.term.center = Mock(return_value='')
        self.mm.visualize()
        self.mm.program.term.center.assert_called()

    def test_handle_key(self):
        self.assertEqual(self.mm.active_button, 0)

        for i in range(1, 3):
            self.mm.handle_key(Keystroke(name='KEY_RIGHT'))
            self.assertEqual(self.mm.active_button, i % 3)

        for i in range(2, -1):
            self.mm.handle_key(Keystroke(name='KEY_RIGHT'))
            self.assertEqual(self.mm.active_button, i)


class TestStatsScreen(unittest.TestCase):

    @patch('src.program.Program')
    def setUp(self, mockProgram):
        self.ss = StatsScreen(mockProgram)

    def test_handle_key(self):

        self.assertEqual(self.ss._StatsScreen__active_widget_x, 0)

        for i in range(1, 3):
            self.ss.handle_key(Keystroke(name='KEY_RIGHT'))
            self.assertEqual(self.ss._StatsScreen__active_widget_x, i % 2)

        for i in range(1, -1):
            self.ss.handle_key(Keystroke(name='KEY_LEFT'))
            self.assertEqual(self.ss._StatsScreen__active_widget_x, i)

        self.assertEqual(self.ss._StatsScreen__active_widget_y, 0)

        for i in range(1, 4):
            self.ss.handle_key(Keystroke(name='KEY_DOWN'))
            self.assertEqual(self.ss._StatsScreen__active_widget_y, i % 3)

        for i in range(2, -1):
            self.ss.handle_key(Keystroke(name='KEY_UP'))
            self.assertEqual(self.ss._StatsScreen__active_widget_y, i)
