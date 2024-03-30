import unittest
from src.statistics import Statistics, FileStatistics
from src.gamemodes import Gamemode
import time
import random
import os


class TestStatistics(unittest.TestCase):
    NANOSECONDS_IN_SECOND = 1000000000.0

    def test_add_word(self):
        stats = Statistics('mmmity', 'test_text', Gamemode.NO_ERRORS, 0.0)
        wordlist = ['Lorem', ' ipsum', ' dolor', ' sit', ' amet']

        self.assertEqual(stats.word_count, 0)
        self.assertEqual(stats.character_count, 0)

        wordlen = [len(word) for word in wordlist]
        for i in range(5):
            stats.add_word(wordlist[i])
            self.assertEqual(stats.word_count, i + 1)
            self.assertEqual(stats.character_count, sum(wordlen[:i + 1]))

    def test_wpm(self):
        stats = Statistics('mmmity', 'test_text', Gamemode.NO_ERRORS, 0.0)
        wordlist = ['Lorem', ' ipsum', ' dolor', ' sit', ' amet']
        for word in wordlist:
            stats.add_word(word)

        time.sleep(5.0)
        self.assertAlmostEqual(stats.get_wpm(), 60, delta=0.05)

    def test_cpm(self):
        stats = Statistics('mmmity', 'test_text', Gamemode.NO_ERRORS, 0.0)
        wordlist = ['Lorem', ' ipsum', ' dolor', ' sit', ' amet']
        for word in wordlist:
            stats.add_word(word)

        time.sleep(5.0)
        self.assertAlmostEqual(stats.get_cpm(), 312, delta=0.05)

    def test_elapsed(self):
        stats = Statistics('mmmity', 'test_text', Gamemode.NO_ERRORS, 0.0)
        time.sleep(1.0)
        self.assertAlmostEqual(stats.get_elapsed_s(), 1.0, delta=0.05)

    def test_save(self):
        # Generating random filename so no collisions occur
        filename = random.randbytes(8).hex() + 'stats.csv'
        stats_1 = Statistics('mmmity', 'test_text',
                             Gamemode.NO_ERRORS, 0.0)
        stats_2 = Statistics('rom4ik', 'RANDOM.test_vocab',
                             Gamemode.FIX_ERRORS, 0.0)
        wordlist = ['Lorem', ' ipsum', ' dolor', ' sit', ' amet']

        for word in wordlist:
            stats_1.add_word(word)
            stats_2.add_word(word)
        time.sleep(5.0)
        stats_1.save_to_file(filename)
        time.sleep(5.0)
        stats_2.error_count += 3
        stats_2.save_to_file(filename)

        expected_1 = ['mmmity', 'test_text', 'Gamemode.NO_ERRORS',
                      5, 26, 5 * self.NANOSECONDS_IN_SECOND, 0.0, 0]
        # 5 words, 26 characters, 5 seconds, 0 errors

        expected_2 = ['rom4ik', 'RANDOM.test_vocab', 'Gamemode.FIX_ERRORS',
                      5, 26, 10 * self.NANOSECONDS_IN_SECOND, 0.0, 3]
        # 5 words, 26 characters, 10 seconds, 3 errors

        with open(filename, 'r') as stats_file:
            real_1 = stats_file.readline().split(';')
            real_2 = stats_file.readline().split(';')
            self.assertEqual(stats_file.read(), '')

        os.remove(filename)
        for i in range(7):
            if type(expected_1[i]) is float:
                self.assertAlmostEqual(expected_1[i], float(real_1[i]),
                                       delta=5e-3 * self.NANOSECONDS_IN_SECOND)
            elif type(expected_1[i]) is int:
                self.assertEqual(expected_1[i], int(real_1[i]))
            else:
                self.assertEqual(expected_1[i], real_1[i])

            if type(expected_2[i]) is float:
                self.assertAlmostEqual(expected_2[i], float(real_2[i]),
                                       delta=5e-3 * self.NANOSECONDS_IN_SECOND)
            elif type(expected_2[i]) is int:
                self.assertEqual(expected_2[i], int(real_2[i]))
            else:
                self.assertEqual(expected_2[i], real_2[i])

    def test_freeze(self):
        stats = Statistics('mmmity', 'test_text', Gamemode.NO_ERRORS, 0.0)
        stats.freeze()
        time.sleep(1)
        self.assertAlmostEqual(stats.get_elapsed_s(), 0,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)


class TestFileStatistics(unittest.TestCase):
    NANOSECONDS_IN_SECOND = 1000000000.0

    def create_files(self):
        self.file1_name = random.randbytes(8).hex() + 'stats.csv'
        self.file2_name = random.randbytes(8).hex() + 'stats.csv'
        self.badfile_name = random.randbytes(8).hex() + 'badstats.csv'

        stats = [Statistics('mmmity', 'test_text', Gamemode.NO_ERRORS, 0.0),
                 Statistics('mmmity', 'test_text', Gamemode.FIX_ERRORS, 0.0),
                 Statistics('mmmity', 'good_text', Gamemode.FIX_ERRORS, 0.0),
                 Statistics('rom4ik', 'test_text', Gamemode.NO_ERRORS, 0.0),
                 Statistics('rom4ik', 'good_text', Gamemode.FIX_ERRORS, 0.0)]

        wordlist = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet']
        for s in stats:
            for w in wordlist:
                s.add_word(w)

        time.sleep(1)
        stats[1].freeze()
        time.sleep(1)
        stats[0].freeze()
        stats[2].freeze()
        time.sleep(1)
        stats[3].freeze()
        stats[4].freeze()

        stats[3].save_to_file(self.file2_name)
        stats[4].save_to_file(self.file1_name)
        stats[2].save_to_file(self.file1_name)
        stats[0].save_to_file(self.file1_name)
        stats[1].save_to_file(self.file1_name)

        with open(self.badfile_name, 'w') as badfile:
            badfile.write(';;;;;;;;;;;;;;')

    def clean_up(self):
        os.remove(self.file1_name)
        os.remove(self.file2_name)
        os.remove(self.badfile_name)

    def setUp(self):
        self.create_files()

    def tearDown(self):
        self.clean_up()

    def test_add_file(self):
        fs = FileStatistics()

        self.assertEqual(len(fs.entries), 0)

        fs.add_file(self.file1_name)
        self.assertEqual(len(fs.entries), 4)
        self.assertEqual(len(fs.by_user.keys()), 2)
        self.assertEqual(len(fs.by_text_tag.keys()), 2)
        self.assertEqual(len(fs.by_user['mmmity']), 3)
        self.assertEqual(len(fs.by_user['rom4ik']), 1)
        self.assertEqual(len(fs.by_text_tag['good_text']), 2)
        self.assertEqual(len(fs.by_text_tag['test_text']), 2)

        fs.add_file(self.file2_name)
        self.assertEqual(len(fs.entries), 5)
        self.assertEqual(len(fs.by_user.keys()), 2)
        self.assertEqual(len(fs.by_text_tag.keys()), 2)
        self.assertEqual(len(fs.by_user['mmmity']), 3)
        self.assertEqual(len(fs.by_user['rom4ik']), 2)
        self.assertEqual(len(fs.by_text_tag['good_text']), 2)
        self.assertEqual(len(fs.by_text_tag['test_text']), 3)

        with self.assertRaises(TypeError):
            fs.add_file(self.badfile_name)

    def test_user_best_stats(self):
        fs = FileStatistics()
        fs.add_file(self.file1_name)
        fs.add_file(self.file2_name)

        mmmity_best = fs.user_best_stats('mmmity')
        rom4ik_best = fs.user_best_stats('rom4ik')
        leha_best = fs.user_best_stats('leha')

        self.assertDictEqual(leha_best, {})
        self.assertCountEqual(mmmity_best.keys(),
                              ['good_text', 'test_text'])
        self.assertCountEqual(rom4ik_best.keys(),
                              ['good_text', 'test_text'])
        self.assertAlmostEqual(mmmity_best['test_text'].time,
                               1 * self.NANOSECONDS_IN_SECOND,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)
        # mmmity's best time on test_text should be approx. 1 second

        self.assertAlmostEqual(mmmity_best['good_text'].time,
                               2 * self.NANOSECONDS_IN_SECOND,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)
        # mmmity's best time on good_text should be approx. 2 seconds

        self.assertAlmostEqual(rom4ik_best['test_text'].time,
                               3 * self.NANOSECONDS_IN_SECOND,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)
        # rom4ik's best time on test_text should be approx. 3 seconds

        self.assertAlmostEqual(rom4ik_best['good_text'].time,
                               3 * self.NANOSECONDS_IN_SECOND,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)
        # rom4ik's best time on good_text should be approx. 3 seconds

    def test_text_best_stats(self):

        fs = FileStatistics()
        fs.add_file(self.file1_name)
        fs.add_file(self.file2_name)

        test_top5 = fs.text_best_stats('test_text', 5)
        test_top1 = fs.text_best_stats('test_text', 1)
        good_top5 = fs.text_best_stats('good_text', 5)
        good_top1 = fs.text_best_stats('good_text', 1)

        self.assertEqual(len(test_top5), 3)
        self.assertEqual(len(test_top1), 1)
        self.assertEqual(len(good_top5), 2)
        self.assertEqual(len(good_top1), 1)

        self.assertEqual(test_top1[0].user, 'mmmity')
        self.assertEqual(test_top5[0].user, 'mmmity')
        self.assertEqual(test_top5[1].user, 'mmmity')
        self.assertEqual(test_top5[2].user, 'rom4ik')

        self.assertAlmostEqual(test_top1[0].time,
                               1 * self.NANOSECONDS_IN_SECOND,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)
        # Top1's time on test_text should be approx. 1 second

        self.assertAlmostEqual(good_top1[0].time,
                               2 * self.NANOSECONDS_IN_SECOND,
                               delta=5e-3 * self.NANOSECONDS_IN_SECOND)
        # Top1's time on good_text should be approx. 2 seconds

        nonexistent_top1 = fs.text_best_stats('nonexistent', 1)
        self.assertEqual(len(nonexistent_top1), 0)
