import random


class Bot_Easy():

    def index_board(self, board):
        for y, row in enumerate(board):
            for x, elem in enumerate(row):
                yield (x, y), elem

    def random_vacancy(self, board):
        board_spots = self.index_board(board)
        empty_spots = [coords for coords, mark in board_spots if mark == ' ']
        return random.choice(empty_spots)  # coords

    def make_move(self, board):
        print('Making move level "easy"')
        return self.random_vacancy(board)


class Bot_Medium(Bot_Easy):

    def __init__(self, mark):
        self.mark = mark
        return None

    def get_winning_move(self, board, move):

        board_spots = list(self.index_board(board))
        empty_spots = [coords for coords, mark in board_spots if mark == ' ']
        all_marks = list(filter(lambda pos: pos[1] == move, board_spots))

        for y in range(len(board)):  # check rows
            if [coord[1] for coord, _ in all_marks].count(y) == 2:
                if list(filter(lambda c: c[1] == y, empty_spots)):
                    return list(filter(lambda c: c[1] == y, empty_spots))[0]

        for x in range(len(board[0])):  # check columns
            if [coord[0] for coord, _ in all_marks].count(x) == 2:
                if list(filter(lambda c: c[0] == x, empty_spots)):
                    return list(filter(lambda c: c[0] == x, empty_spots))[0]

        # check main diagonal
        if [co[0] == co[1] for co, _ in all_marks].count(True) == 2:
            if list(filter(lambda c: c[0] == c[1], empty_spots)):
                return list(filter(lambda c: c[0] == c[1], empty_spots))[0]
        # check reverse diagonal
        if [co[0] == 2 - co[1] for co, _ in all_marks].count(True) == 2:
            if list(filter(lambda c: c[0] == 2 - c[1], empty_spots)):
                return list(filter(lambda c: c[0] == 2 - c[1], empty_spots))[0]
        return []

    def make_move(self, board):
        print('Making move level "medium"')
        comp_wins = self.get_winning_move(board, self.mark)
        if comp_wins:
            return comp_wins

        opp_will_win = self.get_winning_move(board,
                                             'X' if self.mark == 'O' else 'O')
        if opp_will_win:
            return opp_will_win

        return self.random_vacancy(board)


class Bot_Hard(Bot_Medium):

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
            return 10 if state[1] == self.mark else -10
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

    def make_move(self, board):
        print('Making move level "hard"')

        board_spots = self.index_board(board)
        empty_spots = [coords for coords, mark in board_spots if mark == ' ']
        move_scores = {}

        for move in empty_spots:
            temp_board = [row.copy() for row in board]
            temp_board[move[1]][move[0]] = self.mark
            move_scores[move] = self.minimax(temp_board,
                                             'O' if self.mark == 'X' else 'X',
                                             'min')

        target_score = max(move_scores.values())
        for move, score in move_scores.items():
            if score == target_score:
                return move


if __name__ == '__main__':
    pass
