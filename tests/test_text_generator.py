import unittest
from src.text_generator import RandomTextGenerator, FileTextGenerator
from src.exceptions import EndOfFile
import os
import random


class TestRandomTextGenerator(unittest.TestCase):

    def create_vocab_file(self, vocab: list) -> str:
        # Adding random bytes to filename
        # so no collisions with existing files happen
        self.filename = random.randbytes(8).hex() + 'vocabulary.txt'
        with open(self.filename, 'w') as vocab_file:
            vocab_file.write('\n'.join(vocab))

    def clean_up(self):
        os.remove(self.filename)

    def test_open(self):
        self.create_vocab_file(['a'])
        gen = RandomTextGenerator(self.filename, 4)
        self.clean_up()

        self.assertCountEqual(gen.vocab, ['a'])

    def test_generation(self):
        self.create_vocab_file(['a', 'b', 'c', 'd'])
        gen = RandomTextGenerator(self.filename, 4)
        self.clean_up()

        for _ in range(60):
            self.assertIn(gen.next_word(), ['a', 'b', 'c', 'd'])

    def test_words_before(self):
        self.create_vocab_file(['a', 'b', 'c', 'd'])
        gen = RandomTextGenerator(self.filename, 4)
        self.clean_up()

        self.assertEqual(gen.words_before(3), [])
        prev_words = [gen.next_word()]
        self.assertEqual(gen.words_before(3), prev_words)
        prev_words.append(gen.next_word())
        self.assertEqual(gen.words_before(3), prev_words)
        prev_words.append(gen.next_word())
        self.assertEqual(gen.words_before(3), prev_words)

        befores = []
        words = []
        for _ in range(60):
            words.append(gen.next_word())
            befores.append(gen.words_before(3))
            self.assertEqual(len(befores[-1]), 3)

        for i in range(1, 60):
            self.assertEqual(befores[i-1][1], befores[i][0])
            self.assertEqual(befores[i-1][2], befores[i][1])
            self.assertEqual(words[i], befores[i][2])

    def test_words_after(self):
        self.create_vocab_file(['a', 'b', 'c', 'd'])
        gen = RandomTextGenerator(self.filename, 4)
        self.clean_up()

        afters = []
        words = []
        for _ in range(60):
            afters.append(gen.words_after(3))
            words.append(gen.next_word())
            self.assertEqual(len(afters[-1]), 3)

        for i in range(59):
            self.assertEqual(afters[i][1], afters[i+1][0])
            self.assertEqual(afters[i][2], afters[i+1][1])
            self.assertEqual(words[i + 1], afters[i][0])

    def test_words_before_number(self):
        self.create_vocab_file(['a', 'b', 'c', 'd'])
        gen = RandomTextGenerator(self.filename, 4)
        self.clean_up()

        for i in range(3):
            self.assertEqual(len(gen.words_before(3)), i)
            self.assertEqual(len(gen.words_before(1000-7)), i)
            gen.next_word()

        for _ in range(60):
            self.assertEqual(len(gen.words_before(3)), 3)
            self.assertEqual(len(gen.words_before(1000-7)), 3)
            self.assertEqual(len(gen.words_before(2)), 2)
            gen.next_word()

    def test_words_after_number(self):
        self.create_vocab_file(['a', 'b', 'c', 'd'])
        gen = RandomTextGenerator(self.filename, 4)
        self.clean_up()

        for _ in range(60):
            self.assertEqual(len(gen.words_after(3)), 3)
            self.assertEqual(len(gen.words_after(1000-7)), 3)
            self.assertEqual(len(gen.words_after(2)), 2)
            gen.next_word()


class TestFileTextGenerator(unittest.TestCase):
    def create_text_file(self, text: str):
        # Adding random bytes to filename
        # so no collisions with existing files happen
        self.filename = random.randbytes(8).hex() + 'text.txt'
        with open(self.filename, 'w') as text_file:
            text_file.write(text)

    def clean_up(self):
        os.remove(self.filename)

    def test_open(self):
        self.create_text_file('A b C d')
        gen = FileTextGenerator(self.filename)
        self.clean_up()

        self.assertEqual(gen.text, ['A', 'b', 'C', 'd'])

    def test_generation(self):
        test_text = 'A b C d E; f G3, стопицот'
        self.create_text_file(test_text)
        gen = FileTextGenerator(self.filename)
        self.clean_up()

        output = []
        for _ in range(len(test_text.split())):
            output.append(gen.next_word())
        self.assertEqual(gen.text, test_text.split())

        with self.assertRaises(EndOfFile):
            gen.next_word()

    def test_words_before(self):
        test_text = ' '.join([random.choice(['a', 'b', 'c']) 
                              for _ in range(60)])
        self.create_text_file(test_text)
        gen = FileTextGenerator(self.filename)
        self.clean_up()

        for i in range(3):
            self.assertEqual(len(gen.words_before(3)), i)
            gen.next_word()

        befores = []
        words = []
        for _ in range(57):
            words.append(gen.next_word())
            befores.append(gen.words_before(3))
            self.assertEqual(len(befores[-1]), 3)

        for i in range(1, 57):
            self.assertEqual(befores[i-1][1], befores[i][0])
            self.assertEqual(befores[i-1][2], befores[i][1])
            self.assertEqual(words[i], befores[i][2])

    def test_words_after(self):
        test_text = ' '.join([random.choice(['a', 'b', 'c']) 
                              for _ in range(60)])
        self.create_text_file(test_text)
        gen = FileTextGenerator(self.filename)
        self.clean_up()

        afters = []
        words = []
        for _ in range(57):
            afters.append(gen.words_after(3))
            words.append(gen.next_word())
            self.assertEqual(len(afters[-1]), 3)

        for i in range(56):
            self.assertEqual(afters[i][1], afters[i+1][0])
            self.assertEqual(afters[i][2], afters[i+1][1])
            self.assertEqual(words[i + 1], afters[i][0])

    def test_words_before_number(self):
        test_text = ' '.join([random.choice(['a', 'b', 'c']) 
                              for _ in range(60)])
        self.create_text_file(test_text)
        gen = FileTextGenerator(self.filename)
        self.clean_up()

        for index_pos in range(60):
            self.assertEqual(len(gen.words_before(1000-7)), index_pos)
            self.assertEqual(len(gen.words_before(15)), min(15, index_pos))
            gen.next_word()

    def test_words_after_number(self):
        test_text = ' '.join([random.choice(['a', 'b', 'c']) 
                              for _ in range(60)])
        self.create_text_file(test_text)
        gen = FileTextGenerator(self.filename)
        self.clean_up()

        for index_pos in range(60):
            self.assertEqual(len(gen.words_after(1000-7)), 59 - index_pos)
            self.assertEqual(len(gen.words_after(15)), min(15, 59 - index_pos))
            gen.next_word()
