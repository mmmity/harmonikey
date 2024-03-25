class EndOfFile(Exception):
    '''
    Is used by FileTextGenerator to indicate end of file.
    '''
    pass


class WrongCharacter(Exception):
    '''
    Is thrown by TextOverseer when wrong character is provided
    if gamemode is DIE_ERRORS
    '''
    pass
