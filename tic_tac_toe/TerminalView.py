from typing import Dict, Tuple
from Board import Board
from Players import TicTacToe_Player
import os


def _clear() -> None:
    _ = os.system('cls' if os.name == 'nt' else 'clear')


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
    _clear()
    print('Tic-Tac-Toe\n',
          'Type any key and press "Enter" to start a new game...\n',
          '-----------------------------------------------------\n',
          sep='\n')


def menu(init: bool = True) -> None:
    _clear()
    print('Main Menu:\n',
          '("1", or "Start"): Start a New Game', sep='\n')
    if not init:
        print('("2", or "Restart"): Play Again')
    print('("0", or "End"/"Quit): End Application\n',)


def new_game() -> None:
    _clear()
    print('New Game\n')


def select_human_players() -> None:
    print('\nEnter number of human players (0:10)\n')


def select_board_size() -> None:
    print('\nEnter a board width (2-100)',
          'Omit to play with width = 3\n', sep='\n')


def select_bot_players() -> None:
    print('\nEnter number of computer players (0:10)\n')


def select_strategy(valid_agents: Dict[Tuple, TicTacToe_Player]) -> None:

    pad = "\n\t\t"
    print('\nChoose computer strategy:\n')
    for keys, agent in valid_agents.items():
        print(f'\t{keys}\n\t\t{pad.join(agent.description)}\n')


def select_markers(total_players: int) -> None:
    print('\nEnter a set of markers to use to mark each players space',
          'Markers can be any non-whitespace ASCII character (case'
          ' sensitive), but should not repeat and the number of unique'
          ' markers should match the total number of players'
          f' ({total_players})\n', sep='\n')


def player_turn(marker: str, bot_player: bool) -> None:
    _clear()
    print(f'Current Turn: {marker} '
          f'({"Bot" if bot_player else "User"})')
    if not bot_player:
        print('Enter Coordinates...')


def game_over() -> None:
    _clear()
    print('Game Over')


def final_result(marker: str, win: bool) -> None:
    if win:
        print(f'{marker} Wins')
    else:
        print('Draw')
    print('Press Enter to return to the Main Menu...')


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


def invalid_move() -> None:
    print('Invalid move')


def close() -> None:
    _clear()


if __name__ == '__main__':
    pass
