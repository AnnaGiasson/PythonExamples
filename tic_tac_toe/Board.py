from typing import Union
from abc import ABC, abstractmethod


class Abstract_Board(ABC):

    @abstractmethod
    def reset() -> None:
        pass

    @abstractmethod
    def set_elem(x: int, y: int, m: str) -> None:
        pass

    @abstractmethod
    def get_elem() -> Union[str, None]:
        pass

    @abstractmethod
    def vacancies() -> list:
        pass

    @abstractmethod
    def row(y: int) -> tuple:
        pass

    @abstractmethod
    def column(x: int) -> tuple:
        pass

    @abstractmethod
    def diagonal() -> tuple:
        pass

    @abstractmethod
    def reverse_diagonal() -> tuple:
        pass


class OccupiedError(Exception):
    pass


class BoardIterator():
    def __init__(self, board: Abstract_Board) -> None:
        self._board = board

        self._x, self._y = -1, 0
        self._size = self._board.board_size

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if (self._x == (self._size - 1)) and (self._y == (self._size - 1)):
            raise StopIteration
        else:
            if self._x == (self._size - 1):
                self._y += 1
                self._x = 0
            else:
                self._x += 1
            return self._board.get_elem(self._x, self._y)


class Board(Abstract_Board):

    def __init__(self, **kwargs) -> None:
        self.board_size = kwargs.get('n', 3)

        idx = tuple(range(self.board_size))
        self.field = [[None for _ in idx] for _ in idx]

    def __iter__(self) -> BoardIterator:
        return BoardIterator(self)

    def reset(self) -> None:
        idx = tuple(range(self.board_size))
        self.field = [[None for _ in idx] for _ in idx]

    def set_elem(self, x: int, y: int, m: str) -> None:
        if self.field[y][x] is not None:
            raise OccupiedError(f'Position {x, y} is already occupied')
        self.field[y][x] = m

    def get_elem(self, x: int, y: int) -> Union[str, None]:
        return self.field[y][x]

    def vacancies(self) -> list:

        coords = []
        for y, row in enumerate(self.field):
            for x, elem in enumerate(row):
                if elem is None:
                    coords.append((x, y))
        return coords

    def row(self, y: int) -> tuple:
        return tuple(self.get_elem(x, y) for x in range(self.board_size))

    def column(self, x: int) -> tuple:
        return tuple(self.get_elem(x, y) for y in range(self.board_size))

    def diagonal(self) -> tuple:
        return tuple(self.get_elem(i, i) for i in range(self.board_size))

    def reverse_diagonal(self) -> tuple:
        n = self.board_size
        return tuple(self.get_elem(i, n - 1 - i) for i in range(n))


if __name__ == '__main__':
    pass
