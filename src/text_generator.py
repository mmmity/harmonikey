import abc
import typing
import random
from enum import Enum

from src.exceptions import EndOfFile


class TextgenType(Enum):
    RANDOM = 1
    # New word is chosen randomly from vocabulary

    FILE = 2
    # Words are consistently taken from text file


class TextGenerator(abc.ABC):
    '''
    Abstract class for generating text for training.
    '''
    @abc.abstractmethod
    def next_word(self) -> str:
        '''
        Returns next word from generator.
        '''

    @abc.abstractmethod
    def current_word(self) -> str:
        '''
        Returns current word from generator.
        '''

    @abc.abstractmethod
    def words_before(self, num_words: int) -> str:
        '''
        Returns num_words before the current word
        in generator for proper visualization.
        '''

    @abc.abstractmethod
    def words_after(self, num_words: int) -> str:
        '''
        Returns num_words after the current word
        in generator for proper visualization.
        '''


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
        self.__poolsize: int = init_poolsize * 2 - 1
        self.__pool: list = []

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
            self.__pool.pop(0)

        return out_word

    def current_word(self) -> str:
        '''
        Returns word from pool on active position.
        '''
        word_index = (self.__poolsize + 1) // 2
        return self.__pool[-word_index]

    def words_before(self, num_words: int) -> typing.List[str]:
        '''
        Returns num_words words from pool before current word.
        If num_words is greater than available amount, returns all.
        '''
        word_index = len(self.__pool) - (self.__poolsize + 1) // 2
        num_words = min(num_words, word_index)
        return self.__pool[word_index - num_words:word_index]

    def words_after(self, num_words: int) -> typing.List[str]:
        '''
        Returns num_words words from pool after current word.
        If num_words is greater than available amount, returns all.
        '''
        word_index = len(self.__pool) - (self.__poolsize + 1) // 2
        num_words = min(num_words, self.__poolsize // 2)
        return self.__pool[word_index+1:word_index+1+num_words]


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
            self.text: str = file.read().split()
        self.__index: int = 0

    def next_word(self) -> str:
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

    def current_word(self) -> str:
        '''
        Returns word from text on position index.
        Raises EndOfFile if end of file is reached.
        '''
        if self.__index >= len(self.text):
            raise EndOfFile
        return self.text[self.__index]

    def words_before(self, num_words: int) -> str:
        '''
        Returns num_words before index.
        If num_words is greater than available amount, returns all.
        '''
        num_words = min(num_words, self.__index)
        return self.text[self.__index - num_words:self.__index]

    def words_after(self, num_words: int) -> str:
        '''
        Returns num_words after index.
        If num_words is greater than available amount, returns all.
        '''
        num_words = min(num_words, len(self.text) - self.__index - 1)
        return self.text[self.__index+1:self.__index+num_words+1]
