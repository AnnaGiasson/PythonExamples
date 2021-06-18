import random
from abc import ABC, abstractmethod, abstractproperty
from typing import Union, Tuple
from Board import Board
import re


class TicTacToe_Player(ABC):

    def __init__(self, marker) -> None:
        self.marker = marker

    @abstractproperty
    def strategy():
        pass

    @abstractmethod
    def move(board: Board, players: set) -> tuple:
        pass


class UserExit(Exception):
    pass


class UserHelp(Exception):
    pass


class UserInvalidCommand(Exception):
    pass


class UserInvalidMove(Exception):
    pass


class User(TicTacToe_Player):

    @property
    def strategy(self):
        return 'human'

    @staticmethod
    def _coord_xfmr(x: int, y: int, board_size: int,
                    reverse: bool = False) -> Tuple[int, int]:
        if reverse:
            return (x + 1, board_size - y)
        else:
            return (x - 1, board_size - y)

    @staticmethod
    def _get_coordinates(user_input: str) -> Tuple[int, int]:

        coord_pattern = r'[\(\ \n]*(\d+)[,\-\ ]+(\d+)[\)\ \n]*'
        match = re.match(coord_pattern, user_input)

        if match is None:
            raise UserInvalidCommand('Unrecognized coordinate format')
        else:
            coords = tuple(map(int, match.groups()))

        return coords

    def _check_coordinates(self, x: int, y: int, board: Board) -> None:
        if any(not (1 <= i <= board.board_size) for i in (x, y)):
            raise UserInvalidMove('Coordinates are not on the board')
        if self._coord_xfmr(x, y, board.board_size) not in board.vacancies():
            raise UserInvalidMove('Space is already Occupied')

    def _user_commands(self, user_input: str, board: Board) -> None:

        # process possible user commands
        if user_input in ('end', 'exit', 'stop'):
            raise UserExit('"Exit" command issued by user')
        elif user_input == 'help':
            raise UserHelp('"Help" command issued by user')

    def move(self, board: Board, players: set) -> tuple:

        user_input = input().strip().lower()

        self._user_commands(user_input, board)
        x, y = self._get_coordinates(user_input)
        self._check_coordinates(x, y, board)

        return self._coord_xfmr(x, y, board.board_size)


class BotRandom(TicTacToe_Player):

    @property
    def strategy(self):
        return 'random'

    def move(self, board: Board, players: set) -> tuple:
        return random.choice(board.vacancies())


class BotDefensive(TicTacToe_Player):

    @property
    def strategy(self):
        return 'Defensive'

    @staticmethod
    def is_run(sequence: tuple, marker: str) -> bool:
        char_set = set(sequence)

        # set of len 2 containing marker+None, with None only occuring once
        return (char_set == {marker, None}) and (sequence.count(None) == 1)

    def winning_move(self, board: Board, marker) -> Union[Tuple, None]:

        N = board.board_size

        for n in range(N):  # check rows and cols

            row = board.row(n)
            col = board.column(n)

            if self.is_run(row, marker):
                x = row.index(None)
                y = n
                return (x, y)

            elif self.is_run(col, marker):
                x = n
                y = col.index(None)
                return (x, y)

        # check diagonals
        dia = board.diagonal()
        if self.is_run(dia, marker):
            n = dia.index(None)
            return (n, n)

        r_dia = board.reverse_diagonal()
        if self.is_run(r_dia, marker):
            n = r_dia.index(None)
            return (n, (N-1) - n)

        return None

    def move(self, board: Board, players: set) -> tuple:
        for marker in players:
            move = self.winning_move(board, marker)

            if isinstance(move, tuple):  # winning move found
                if marker == self.marker:
                    return move  # bot wins
                else:
                    break  # opponent wins
        else:
            # only runs if no win was found (no break or return hit)
            return random.choice(board.vacancies())  # if nobody will win guess

        return move  # block opponent


class BotMinmax(TicTacToe_Player):

    def index_board(self, board):
        for y, row in enumerate(board):
            for x, elem in enumerate(row):
                yield (x, y), elem

    @property
    def strategy(self):
        return 'Minmax'

    def evaluate_state(self, board):

        board_spots = list(self.index_board(board))

        # check if a player won
        for move in ['X', 'O']:
            all_marks = list(filter(lambda pos: pos[1] == move, board_spots))

            for y in range(len(board)):  # check rows
                if [coord[1] for coord, _ in all_marks].count(y) == 3:
                    return ('win', move)

            for x in range(len(board[0])):  # check columns
                if [coord[0] for coord, _ in all_marks].count(x) == 3:
                    return ('win', move)

            # check main diagonal
            if [co[0] == co[1] for co, _ in all_marks].count(True) == 3:
                return ('win', move)
            # check reverse diagonal
            if [co[0] == 2 - co[1] for co, _ in all_marks].count(True) == 3:
                return ('win', move)

        # check if a draw
        empty_spots = [coords for coords, mark in board_spots if mark == ' ']
        if not empty_spots:
            return ('draw', '')
        else:
            return ('', '')  # game still in progress

    def minimax(self, board, turn, mode):

        state = self.evaluate_state(board)

        if state[0] == 'win':
            return 10 if state[1] == self.marker else -10
        if state[0] == 'draw':
            return 0

        board_spots = self.index_board(board)
        empty_spots = [coords for coords, mark in board_spots if mark == ' ']
        move_scores = {}

        for move in empty_spots:
            temp_board = [row.copy() for row in board]
            temp_board[move[1]][move[0]] = turn
            move_scores[move] = self.minimax(temp_board,
                                             'O' if turn == 'X' else 'X',
                                             'min' if mode == 'max' else 'max')
        if mode == 'max':
            return max(move_scores.values())
        elif mode == 'min':
            return min(move_scores.values())

    def move(self, board: Board, players: set) -> tuple:

        board_spots = self.index_board(board)
        empty_spots = [coords for coords, mark in board_spots if mark == ' ']
        move_scores = {}

        for move in empty_spots:
            temp_board = [row.copy() for row in board]
            temp_board[move[1]][move[0]] = self.marker
            move_scores[move] = self.minimax(temp_board,
                                             'O' if self.marker == 'X' else 'X',
                                             'min')

        target_score = max(move_scores.values())
        for move, score in move_scores.items():
            if score == target_score:
                return move


if __name__ == '__main__':
    pass
