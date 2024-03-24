import time
from typing import NamedTuple, List, Dict


class Statistics:
    '''
    Class for counting, saving and loading statistics in real time
    '''
    def __init__(self, user: str, text_tag: str, mode: str):
        '''
        Initialization for real-time statistics counting
        '''
        self.word_count = 0
        self.character_count = 0
        self.error_count = 0
        self.user = user
        self.start_timer = time.perf_counter_ns()
        self.text_tag = text_tag
        self.mode = mode

    def add_word(self, word: str):
        '''
        Adding word, which was successfully typed by user
        '''
        self.word_count += 1
        self.character_count += len(word)

    def get_wpm(self) -> float:
        '''
        Return wpm (words per minute) for current Statistics
        '''
        elapsed = time.perf_counter_ns() - self.start_timer
        return 60.0 * 1000000000.0 * self.word_count / elapsed

    def get_cpm(self) -> float:
        '''
        Return cpm (characters per minute) for current Statistics
        '''
        elapsed = time.perf_counter_ns() - self.start_timer
        return 60.0 * 1000000000.0 * self.character_count / elapsed

    def save_to_file(self, path: str):
        to_write = ';'.join([self.user,
                             self.text_tag,
                             self.mode,
                             str(self.word_count),
                             str(self.character_count),
                             str(time.perf_counter_ns() - self.start_timer),
                             str(self.error_count)])
        to_write += '\n'

        with open(path, 'a') as stats_file:
            stats_file.write(to_write)


class FileStatistics:
    '''
    Class for loading and analyzing different statistics from file.
    Contains two dictionaries:
        self.by_user has all stats grouped by user
        self.by_text_tag has all stats grouped by exercise
    Also contains list of all loaded entries in self.entries
    Entry is a namedtuple with fields:
        user, text_tag, mode, word_count, character_count, time, error_count
    '''

    class Entry(NamedTuple):
        '''
        Contains all parameters from stats file entry
        '''
        user: str
        text_tag: str
        mode: str
        word_count: int
        character_count: int
        time: int
        error_count: int

    def __init__(self):
        '''
        Initializes all containers with empty ones.
        '''
        self.entries: List[self.Entry] = []
        self.by_user: Dict[str, List[self.Entry]] = dict()
        self.by_text_tag: Dict[str, List[self.Entry]] = dict()

    def add_file(self, filename: str):
        '''
        Appends all entries from filename to containers.
        If file is malformed (e. g. wrong line format), raises TypeError.
        '''
        new_entries = []
        with open(filename, 'r') as stats_file:
            for line in stats_file.readlines():
                splitted = line.rstrip().split(';')
                try:
                    entry = self.Entry(splitted[0], splitted[1], splitted[2],
                                       int(splitted[3]), int(splitted[4]),
                                       int(splitted[5]), int(splitted[6]))
                except (IndexError, TypeError):
                    raise TypeError("Wrong file format")
                new_entries.append(entry)

        self.entries += new_entries
        for entry in new_entries:
            if entry.user not in self.by_user.keys():
                self.by_user[entry.user] = []
            self.by_user[entry.user].append(entry)

            if entry.text_tag not in self.by_text_tag.keys():
                self.by_text_tag[entry.text_tag] = []
            self.by_text_tag[entry.text_tag].append(entry)

        for text_tag_runs in self.by_text_tag.values():
            text_tag_runs.sort(key=lambda entry:
                               -(entry.word_count / entry.time))

    def user_best_stats(self, user: str) -> Dict[str, Entry]:
        '''
        Returns dictionary with best stats by wpm (words per minute)
        For every text_tag with certain user.
        '''
        out = dict()
        if user not in self.by_user.keys():
            return out

        for entry in self.by_user[user]:
            if entry.text_tag not in out.keys():
                out[entry.text_tag] = entry
            new_wpm = entry.word_count / entry.time
            wpm = out[entry.text_tag].word_count / out[entry.text_tag].time
            if new_wpm > wpm:
                out[entry.text_tag] = entry

        return out

    def text_best_stats(self, tag: str, n_entries: int = 10) -> List[Entry]:
        '''
        Returns list of n_entries best by wpm (words per minute) entries
        For certain tag.
        '''
        if tag not in self.by_text_tag.keys():
            return []
        return self.by_text_tag[tag][:n_entries]
