import random
from Bots import Bot_Easy, Bot_Medium, Bot_Hard


class TicTacToe():
    def __init__(self, **kwargs) -> None:
        self.move, self.game_state = 'X', ''
        self.players = {'X': None, 'O': None}
        self.board = [list('   ') for _ in range(3)]
        random.seed(kwargs.get('random_seed', 0))

    def print_board(self):
        print('---------\n'
              '| {} {} {} |\n'
              '| {} {} {} |\n'
              '| {} {} {} |\n'
              '---------'.format(*self.board[0],
                                 *self.board[1],
                                 *self.board[2]))
        return None

    def three_matchs(self, elems):
        if (len(set(elems)) == 1) and (set(elems).pop() in ['X', 'O']):
            return True
        return False

    def check_victory(self):

        for row in self.board:
            if self.three_matchs(row):
                return True  # winning row
        for col in range(len(self.board[0])):
            if self.three_matchs([row[col] for row in self.board]):
                return True  # winning column

        if self.three_matchs([self.board[x][x] for x in [0, 1, 2]]):
            return True  # winning diagonal
        if self.three_matchs([self.board[x][2 - x] for x in [0, 1, 2]]):
            return True  # winning reverse diagonal
        return False

    def remaining_moves(self):
        i = [0, 1, 2]
        return [[x, y] for x in i for y in i if not self.is_occupied([x, y])]

    def validiate_user_input(self, user_input):

        if user_input.replace(' ', '').isnumeric():
            coords = [int(num) for num in user_input.split()]

            if any(coord not in [1, 2, 3] for coord in coords):
                print('Coordinates should be from 1 to 3!')
                return False
            else:
                coords = [coords[0] - 1, 2 - coords[1] + 1]
                if coords not in self.remaining_moves():
                    print('This cell is occupied! Choose another one!')
                    return False
                return True

        print('You should enter numbers!')
        return False

    def is_occupied(self, coords):
        return not (self.board[coords[1]][coords[0]] == ' ')

    def user_move(self):
        while True:
            user_input = input('Enter the coordinates: ')
            if self.validiate_user_input(user_input):
                coords = [int(num) for num in user_input.split()]
                coords = [coords[0] - 1, 2 - coords[1] + 1]
                return coords
        return None

    def run_session(self):
        self.print_board()

        while self.game_state == "":
            if self.players[self.move] == 'user':
                coords = self.user_move()
            else:
                coords = self.players[self.move].make_move(self.board)

            self.board[coords[1]][coords[0]] = self.move
            self.print_board()

            if self.check_victory():
                self.game_state = f'{self.move} wins'
            elif len(self.remaining_moves()) == 0:
                self.game_state = "Draw"

            print(self.game_state)
            self.move = 'O' if (self.move == 'X') else 'X'  # for next turn
        self.__init__()  # for next game
        return None

    def check_input_command(self, user_input):
        words = user_input.split()
        options = ['user', 'easy', 'medium', 'hard']
        if len(words) != 3:
            return False
        if words[0] != 'start':
            return False
        if (words[1] not in options) or (words[2] not in options):
            return False
        return True

    def start_game(self):

        while True:
            user_input = input('Input command: ')
            if self.check_input_command(user_input):
                break
            print('Bad parameters!')

        self.players['X'], self.players['O'] = user_input.split()[1:]

        for mark in self.players:
            if self.players[mark] == 'easy':
                self.players[mark] = Bot_Easy()
            elif self.players[mark] == 'medium':
                self.players[mark] = Bot_Medium(mark)
            elif self.players[mark] == 'hard':
                self.players[mark] = Bot_Hard(mark)

        self.run_session()
        return None


if __name__ == "__main__":
    game_session = TicTacToe()
    game_session.start_game()
