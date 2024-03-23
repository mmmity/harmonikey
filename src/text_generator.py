import abc
import typing
import random
import collections
import itertools

from src.exceptions import EndOfFile


class TextGenerator(abc.ABC):
    '''
    Abstract class for generating text for training.
    '''
    @abc.abstractmethod
    def next_word(self) -> str:
        '''
        Returns next word from generator.
        '''
        pass

    @abc.abstractmethod
    def words_before(self, num_words: int) -> str:
        '''
        Returns num_words before the current word
        in generator for proper visualization.
        '''
        pass

    @abc.abstractmethod
    def words_after(self, num_words: int) -> str:
        '''
        Returns num_words after the current word
        in generator for proper visualization.
        '''
        pass


class RandomTextGenerator(TextGenerator):
    '''
    Text generator that continuously generates random words.
    Vocabulary from file, words are separated by whitespace characters.
    Has a pool of randomly generated words.
    '''
    def __init__(self, filename: str, init_poolsize: int):
        '''
        Initializes the vocabulary with words from file.
        Initializes the pool with init_poolsize random words.
        '''
        with open(filename, 'r') as file:
            self.vocab = file.read().split()
        self.__poolsize = init_poolsize * 2 - 1
        self.__pool = collections.deque()

        for _ in range(init_poolsize):
            self.__pool.append(random.choice(self.vocab))

    def next_word(self) -> str:
        '''
        Returns next word from pool.
        Adds random word into pool.
        Removes first word from pool if len(pool) > poolsize.
        '''
        word_index = (self.__poolsize + 1) // 2
        out_word = self.__pool[-word_index]

        self.__pool.append(random.choice(self.vocab))
        if len(self.__pool) > self.__poolsize:
            self.__pool.popleft()

        return out_word

    def words_before(self, num_words: int) -> typing.List[str]:
        '''
        Returns num_words words from pool before current word.
        If num_words is greater than available amount, returns all.
        '''
        word_index = len(self.__pool) - (self.__poolsize + 1) // 2
        num_words = max(num_words, self.__poolsize // 2)
        return list(itertools.islice(self.__pool, word_index))

    def words_after(self, num_words: int) -> typing.List[str]:
        '''
        Returns num_words words from pool after current word.
        If num_words is greater than available amount, returns all.
        '''
        word_index = len(self.__pool) - (self.__poolsize + 1) // 2
        num_words = max(num_words, self.__poolsize // 2)
        return list(itertools.islice(self.__pool,
                                     word_index+1, len(self.__pool)))


class FileTextGenerator(TextGenerator):
    '''
    Text generator that returns continuous words from text file.
    When no more words are left, raises EndOfFile.
    '''
    def __init__(self, filename: str):
        '''
        Initializes text with text from file, split into words.
        '''
        with open(filename, 'r') as file:
            self.text = file.read().split()
        self.__index = 0

    def next_word(self):
        '''
        Returns word from text on position index.
        If index > len(text) raises EndOfFile.
        Increases index by 1.
        '''
        if self.__index >= len(self.text):
            raise EndOfFile
        out_word = self.text[self.__index]
        self.__index += 1

        return out_word

    def words_before(self, num_words: int) -> str:
        '''
        Returns num_words before index.
        If num_words is greater than available amount, returns all.
        '''
        num_words = max(num_words, self.__index)
        return list(itertools.islice(self.text,
                                     self.__index - num_words, self.__index))

    def words_after(self, num_words: int) -> str:
        '''
        Returns num_words after index.
        If num_words is greater than available amount, returns all.
        '''
        num_words = max(num_words, len(self.text) - self.__index - 1)
        return list(itertools.islice(self.text, self.__index + 1,
                                     self.__index + num_words + 1))
