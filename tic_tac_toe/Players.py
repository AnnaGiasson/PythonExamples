import random
from abc import ABC, abstractmethod, abstractproperty, abstractstaticmethod
from itertools import product, cycle
from typing import Iterable, Union, Tuple
from Board import Board
import re


class TicTacToe_Player(ABC):

    description: Tuple[str]

    def __init__(self, marker) -> None:
        self.marker = marker

    @abstractproperty
    def strategy():
        pass

    @abstractstaticmethod
    def keys() -> Tuple[str]:
        return

    @abstractmethod
    def move(board: Board, players: dict) -> tuple:
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

    description = (
                   'Relies on the intelligence of a Human or other',
                   'intelligent agent to determine the best move'
                   )

    @property
    def strategy(self):
        return 'human'

    @staticmethod
    def keys() -> Tuple[str]:
        return ("3", 'Human', 'General Intelligence', 'Agent', 'AI')

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

    def move(self, board: Board, players: dict) -> tuple:

        user_input = input().strip().lower()

        self._user_commands(user_input, board)
        x, y = self._get_coordinates(user_input)
        self._check_coordinates(x, y, board)

        return self._coord_xfmr(x, y, board.board_size)


class BotRandom(TicTacToe_Player):

    description = ('Chooses a free space at random.',)

    @property
    def strategy(self) -> str:
        return 'random'

    @staticmethod
    def keys() -> Tuple[str]:
        return ("0", "Easy", "Random")

    def move(self, board: Board, players: list) -> tuple:
        return random.choice(board.vacancies())


class BotDefensive(TicTacToe_Player):

    description = (
                   'Will try to block another player from winning, otherwise',
                   'chooses randomly.'
                   )

    @property
    def strategy(self):
        return 'Defensive'

    @staticmethod
    def keys() -> Tuple[str]:
        return ("1", "Medium", "Defensive")

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

    def move(self, board: Board, players: list) -> tuple:
        for marker in players:
            coords = self.winning_move(board, marker)

            if isinstance(coords, tuple):  # winning move found
                if marker == self.marker:
                    return coords  # bot wins
                else:
                    break  # opponent wins
        else:
            # only runs if no win was found (no break or return hit)
            return random.choice(board.vacancies())  # if nobody will win guess

        return coords  # block opponent


class BotMaxLikelihood(TicTacToe_Player):

    SCORE_WIN = 1000
    SCORE_LOSS = -1000
    SCORE_DRAW = 100
    SCORE_PER_TURN = -1

    description = (
                   'selects its next move by choosing the move which yields',
                   'the maximum likelihood of winning based on a heuristic',
                   'scoring function. This Bot plays against itself',
                   'recursively to determine the likelihood of winning for',
                   'all possible future moves and is, therefore, more memory',
                   'and is more computationally expensize. May have long',
                   'run-times on large boards.',
                  )

    @property
    def strategy(self):
        return 'Minmax'

    @staticmethod
    def keys() -> Tuple[str]:
        return ("2", "Hard", "Maximum Likelihood", "Heuristic")

    @staticmethod
    def is_victory(board: Board, players: set) -> bool:

        n = board.board_size

        cases = []
        cases.extend(board.row(y) for y in range(n))
        cases.extend(board.column(x) for x in range(n))
        cases.append(board.diagonal())
        cases.append(board.reverse_diagonal())

        for m in players:
            if any(map(lambda case: case.count(m) == n, cases)):
                return True
        return False

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

    @staticmethod
    def copy_board(board: Board) -> Board:
        N = board.board_size
        board_copy = Board(n=N)
        for x, y in product(range(N), range(N)):
            board_copy.set_elem(x, y, board.get_elem(x, y))
        return board_copy

    @staticmethod
    def iterate_players(set_marker: str, players: list) -> cycle:

        if set_marker not in players:
            raise ValueError('Can not set the turn to a non-existent player')

        # determine the marker that occurs before "set_marker" so the iterator
        # can be stopped so the "set_marker" will be the next value.
        preceeding_marker = players[players.index(set_marker) - 1]

        # create player turn iterator
        player_iter = cycle(players)

        # advance iter to the correct state (set_marker)
        while next(player_iter)[0] != preceeding_marker:
            pass

        return player_iter

    @staticmethod
    def average(values: Iterable) -> float:
        N = len(values)
        return sum(values)/N

    def walk_move_tree(self, coordinates: tuple, board: Board,
                       player_iter: cycle, player_set: set) -> int:

        # make a move
        marker = next(player_iter)
        board.set_elem(*coordinates, marker)

        if self.is_victory(board, player_set):  # win or lose
            if (marker == self.marker):
                return self.SCORE_WIN
            else:
                return self.SCORE_LOSS

        if len(board.vacancies()) == 0:  # draw
            return self.SCORE_DRAW

        child_node_scores = []
        for coord in board.vacancies():
            new_iter = self.iterate_players(marker, player_set)
            _ = next(new_iter)
            score = self.walk_move_tree(coord,
                                        self.copy_board(board), new_iter,
                                        player_set)
            child_node_scores.append(score - self.SCORE_PER_TURN)

        return self.average(child_node_scores)

    def move(self, board: Board, players: list) -> tuple:

        # generate heuristics for each possible move at this turn
        heuristics = {}
        for coords in board.vacancies():

            # create player turn iterator
            player_iter = self.iterate_players(self.marker, players)

            # copy of the current board state
            temp_board = self.copy_board(board)

            score = self.walk_move_tree(coords, temp_board, player_iter,
                                        players)
            if score not in heuristics:
                heuristics[score] = coords

        # choose the move the yields the highest score
        return heuristics[max(heuristics)]


valid_agents = (BotRandom, BotDefensive, BotMaxLikelihood, User)


if __name__ == '__main__':
    pass
