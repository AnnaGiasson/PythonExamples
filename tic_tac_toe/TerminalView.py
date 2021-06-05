from Board import Board


def display_board(board: Board, **kwargs) -> None:

    # options
    fill_val = str(kwargs.get('fill_val', '.'))

    # build assets
    boarder = fill_val*(board.board_size*6 + 1) + '\n'

    empty_row = fill_val.join([' '*5]*board.board_size)
    empty_row = f'{fill_val}{empty_row}{fill_val}\n'

    val_row = fill_val.join(['  {}  ']*board.board_size)
    val_row = f'{fill_val}{val_row}{fill_val}\n'

    # construct template
    template = [empty_row + val_row + empty_row]*board.board_size
    template = boarder.join(template)
    template = boarder + template + boarder

    # display
    print(template.format(*[m if m is not None else ' ' for m in board]))


def start_screen() -> None:
    print('\nTic-Tac-Toe\n',
          'Type any key and press "Enter" to start a new game...\n',
          '-----------------------------------------------------',
          sep='\n')


def menu(init: bool = True) -> None:
    print('\nMain Menu:\n',
          '("1", or "Start"): Start a New Game', sep='\n')
    if not init:
        print('("2", or "Restart"): Play Again')
    print('("0", or "End"/"Quit): End Application\n',)


def select_human_players() -> None:
    print('\nEnter number of human players (0:10)')


def select_bot_players() -> None:
    print('\nEnter number of computer players (0:10)')


def select_strategy() -> None:

    not_imp = ' (Not Implemented)'

    print('\nChoose computer strategy:\n',

          '\t("0", "Easy", "Random"): Chooses a free space at random',

          '\t("1", "Medium", "Defensive"): Will try to block another'
          ' player from winning, otherwise chooses randomly' + not_imp,

          '\t("2", "Hard", "Minimax"): uses a MinMax strategy to pick a'
          ' space that results in the highest likelihood of winning, plays'
          ' against itself recursively to determine the odds. Only'
          ' availible when using 1 computer player in order to limit'
          ' computation time' + not_imp,
          sep='\n')


def select_markers(total_players: int) -> None:
    print('\nEnter a set of markers to use to mark each players space',
          'Markers can be any non-whitespace ASCII character (case'
          ' sensitive), but should not repeat and the number of unique'
          ' markers should match the total number of players\n'
          f' ({total_players})', sep='\n')


def player_turn(marker: str, bot_player: bool) -> None:
    print(f'Current Turn: {marker} '
          f'({"Bot" if bot_player else "User"})')


def game_over() -> None:
    print('Game Over')


def victory(marker: str) -> None:
    print(f'{marker} Wins')


def draw() -> None:
    print('Draw')


def invalid_markers(incorrect_number: bool, repeats: bool) -> None:
    if incorrect_number:
        print('- Number of markers needs to match number of total players')
    if repeats:
        print('- Set of markers contains repeating characters')


def invalid_configuration(**kwargs) -> None:
    print('Invalid Configuration', end='')
    if kwargs:
        print(':')
        for var, value in kwargs.items():
            print(f'\t{var} : {value}')
    else:
        print('', end='\n')


def invalid_input() -> None:
    print('Invalid input')


if __name__ == '__main__':
    pass
