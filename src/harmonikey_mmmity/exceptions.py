class EndOfFile(Exception):
    '''
    Is used by FileTextGenerator to indicate end of file.
    '''


class WrongCharacter(Exception):
    '''
    Is thrown by TextOverseer when wrong character is provided
    if gamemode is DIE_ERRORS
    '''
