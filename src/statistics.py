import time
from typing import NamedTuple, List, Dict
from src.gamemodes import Gamemode


class Statistics:
    '''
    Class for counting, saving and loading statistics in real time
    '''
    NANOSECONDS_IN_MINUTE = 60.0 * 1000000000.0
    NANOSECONDS_IN_SECOND = 1000000000.0

    def __init__(self, user: str, text_tag: str,
                 mode: Gamemode, timeout: float):
        '''
        Initialization for real-time statistics counting
        '''
        self.word_count: int = 0
        self.character_count: int = 0
        self.error_count: int = 0
        self.user: str = user
        self.start_timer: int = time.perf_counter_ns()
        self.text_tag: str = text_tag
        self.mode: Gamemode = mode
        self.timeout: float = timeout
        self.frozen: bool = False
        self.frozen_timer: int = 0

    def get_current_time(self) -> int:
        '''
        Returns time elapsed since the beginning of Training
        If training is over but self is still used,
        it should return time of Training end
        '''
        if self.frozen:
            return self.frozen_timer
        return time.perf_counter_ns()

    def freeze(self):
        '''
        Freezes timer. Is called when Training is ended.
        '''
        self.frozen_timer = self.get_current_time()
        self.frozen = True

    def add_word(self, word: str) -> None:
        '''
        Adding word, which was successfully typed by user
        '''
        self.word_count += 1
        self.character_count += len(word)

    def get_wpm(self) -> float:
        '''
        Return wpm (words per minute) for current Statistics
        '''
        elapsed = self.get_current_time() - self.start_timer
        return self.NANOSECONDS_IN_MINUTE * self.word_count / elapsed

    def get_cpm(self) -> float:
        '''
        Return cpm (characters per minute) for current Statistics
        '''
        elapsed = self.get_current_time() - self.start_timer
        return self.NANOSECONDS_IN_MINUTE * self.character_count / elapsed

    def get_elapsed_s(self) -> float:
        '''
        Returns time elapsed since initialization
        in seconds
        '''
        elapsed = self.get_current_time() - self.start_timer
        return elapsed / self.NANOSECONDS_IN_SECOND

    def __str__(self):
        '''
        String representation of statistics is csv row with all saved data.
        '''
        return ';'.join([
            str(self.user),
            str(self.text_tag),
            str(self.mode),
            str(self.word_count),
            str(self.character_count),
            str(self.get_current_time() - self.start_timer),
            str(self.timeout),
            str(self.error_count),
        ])

    def save_to_file(self, path: str) -> None:
        '''
        Appends stats to file.
        '''
        with open(path, 'a') as stats_file:
            stats_file.write(str(self) + '\n')


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
        timeout: float
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
                    entry = self.Entry(
                        user=splitted[0],
                        text_tag=splitted[1],
                        mode=splitted[2],
                        word_count=int(splitted[3]),
                        character_count=int(splitted[4]),
                        time=int(splitted[5]),
                        timeout=float(splitted[6]),
                        error_count=int(splitted[7])
                    )
                except (IndexError, TypeError, ValueError):
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
