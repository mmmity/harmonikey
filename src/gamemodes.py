from enum import Enum


class Gamemode(Enum):
    NO_ERRORS = 0
    # Program will not let user type wrong characters

    DIE_ERRORS = 1
    # Training will finish on first error
    # No statistics saved

    FIX_ERRORS = 2
    # Wrong characters are stored in buffer
    # User can type Backspace to remove them
