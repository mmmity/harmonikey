import unittest
from src.statistics import Statistics, FileStatistics
import time
import random
import os


class TestStatistics(unittest.TestCase):

    def test_add_word(self):
        stats = Statistics('mmmity', 'test_text', '')
        wordlist = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet']

        self.assertEqual(stats.word_count, 0)
        self.assertEqual(stats.character_count, 0)

        wordlen = [len(word) for word in wordlist]
        for i in range(5):
            stats.add_word(wordlist[i])
            self.assertEqual(stats.word_count, i + 1)
            self.assertEqual(stats.character_count, sum(wordlen[:i + 1]))

    def test_wpm(self):
        stats = Statistics('mmmity', 'test_text', '')
        wordlist = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet']
        for word in wordlist:
            stats.add_word(word)

        time.sleep(5.0)
        self.assertAlmostEqual(stats.get_wpm(), 60, delta=0.05)

    def test_cpm(self):
        stats = Statistics('mmmity', 'test_text', '')
        wordlist = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet']
        for word in wordlist:
            stats.add_word(word)

        time.sleep(5.0)
        self.assertAlmostEqual(stats.get_cpm(), 264, delta=0.05)

    def test_save(self):
        # Generating random filename so no collisions occur
        filename = random.randbytes(8).hex() + 'stats.csv'
        stats_1 = Statistics('mmmity', 'test_text', '')
        stats_2 = Statistics('rom4ik', 'RANDOM.test_vocab', 'err')
        wordlist = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet']

        for word in wordlist:
            stats_1.add_word(word)
            stats_2.add_word(word)
        time.sleep(5.0)
        stats_1.save_to_file(filename)
        time.sleep(5.0)
        stats_2.error_count += 3
        stats_2.save_to_file(filename)

        expected_1 = ['mmmity', 'test_text', '',
                      5, 22, 5000000000.0, 0]
        expected_2 = ['rom4ik', 'RANDOM.test_vocab', 'err',
                      5, 22, 10000000000.0, 3]
        with open(filename, 'r') as stats_file:
            real_1 = stats_file.readline().split(';')
            real_2 = stats_file.readline().split(';')
            for i in range(7):
                if type(expected_1[i]) is float:
                    self.assertAlmostEqual(expected_1[i], float(real_1[i]),
                                           delta=5000000)
                elif type(expected_1[i]) is int:
                    self.assertEqual(expected_1[i], int(real_1[i]))
                else:
                    self.assertEqual(expected_1[i], real_1[i])

                if type(expected_2[i]) is float:
                    self.assertAlmostEqual(expected_2[i], float(real_2[i]),
                                           delta=5000000)
                elif type(expected_2[i]) is int:
                    self.assertEqual(expected_2[i], int(real_2[i]))
                else:
                    self.assertEqual(expected_2[i], real_2[i])

            self.assertEqual(stats_file.read(), '')
        os.remove(filename)


class TestFileStatistics(unittest.TestCase):
    def create_files(self):
        self.file1_name = random.randbytes(8).hex() + 'stats.csv'
        self.file2_name = random.randbytes(8).hex() + 'stats.csv'

        stats = [Statistics('mmmity', 'test_text', ''),
                 Statistics('mmmity', 'test_text', 'err'),
                 Statistics('mmmity', 'good_text', 'err'),
                 Statistics('rom4ik', 'test_text', ''),
                 Statistics('rom4ik', 'good_text', 'err')]

        wordlist = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet']
        for s in stats:
            for w in wordlist:
                s.add_word(w)
        
        time.sleep(1)
        stats[1].save_to_file(self.file1_name)
        time.sleep(1)
        stats[0].save_to_file(self.file2_name)
        stats[2].save_to_file(self.file1_name)
        time.sleep(1)
        stats[3].save_to_file(self.file2_name)
        stats[4].save_to_file(self.file1_name)

    def clean_up(self):
        os.remove(self.file1_name)
        os.remove(self.file2_name)

    def test_add_file(self):
        self.create_files()
        fs = FileStatistics()

        self.assertEqual(len(fs.entries), 0)

        fs.add_file(self.file1_name)
        self.assertEqual(len(fs.entries), 3)
        self.assertEqual(len(fs.by_user.keys()), 2)
        self.assertEqual(len(fs.by_text_tag.keys()), 2)
        self.assertEqual(len(fs.by_user['mmmity']), 2)
        self.assertEqual(len(fs.by_user['rom4ik']), 1)
        self.assertEqual(len(fs.by_text_tag['good_text']), 2)
        self.assertEqual(len(fs.by_text_tag['test_text']), 1)

        fs.add_file(self.file2_name)
        self.assertEqual(len(fs.entries), 5)
        self.assertEqual(len(fs.by_user.keys()), 2)
        self.assertEqual(len(fs.by_text_tag.keys()), 2)
        self.assertEqual(len(fs.by_user['mmmity']), 3)
        self.assertEqual(len(fs.by_user['rom4ik']), 2)
        self.assertEqual(len(fs.by_text_tag['good_text']), 2)
        self.assertEqual(len(fs.by_text_tag['test_text']), 3)

        self.clean_up()

    def test_user_best_stats(self):
        self.create_files()
        fs = FileStatistics()
        fs.add_file(self.file1_name)
        fs.add_file(self.file2_name)

        mmmity_best = fs.user_best_stats('mmmity')
        rom4ik_best = fs.user_best_stats('rom4ik')
        leha_best = fs.user_best_stats('leha')

        self.assertDictEqual(leha_best, {})
        self.assertCountEqual(mmmity_best.keys(), ['good_text', 'test_text'])
        self.assertCountEqual(rom4ik_best.keys(), ['good_text', 'test_text'])
        self.assertAlmostEqual(mmmity_best['test_text'].time, 1000000000, delta=5000000)
        self.assertAlmostEqual(mmmity_best['good_text'].time, 2000000000, delta=5000000)
        self.assertAlmostEqual(rom4ik_best['test_text'].time, 3000000000, delta=5000000)
        self.assertAlmostEqual(rom4ik_best['good_text'].time, 3000000000, delta=5000000)

        self.clean_up()

    def test_text_best_stats(self):
        self.create_files()
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

        self.assertAlmostEqual(test_top1[0].time, 1000000000, delta=5000000)
        self.assertAlmostEqual(good_top1[0].time, 2000000000, delta=5000000)

        self.clean_up()
