from Players import BotRandom, BotDefensive, BotMinmax, User
from Board import Board
# from typing import List
import TerminalView as View
from itertools import cycle


class TicTacToe():
    def __init__(self, **kwargs) -> None:
        self.players = {}
        self.board = Board(n=kwargs.get('n', 3))

    @property
    def win(self) -> bool:

        n = self.board.board_size

        cases = []
        cases.extend(self.board.row(y) for y in range(n))
        cases.extend(self.board.column(x) for x in range(n))
        cases.append(self.board.diagonal())
        cases.append(self.board.reverse_diagonal())

        for m in self.players:
            if any(map(lambda case: case.count(m) == n, cases)):
                return True
        else:
            return False

    @property
    def in_progress(self) -> bool:
        return (not self.win) and (len(self.board.vacancies()) > 0)

    def run_session(self) -> None:

        self.board.reset()
        player_iter = cycle(self.players.items())

        while self.in_progress:

            marker, player = next(player_iter)

            View.player_turn(marker, bot_player=not isinstance(player, User))
            View.display_board(self.board)

            coords = player.move(self.board,
                                 players=set(self.players.keys()))

            self.board.set_elem(*coords, marker)

        View.game_over()
        View.display_board(self.board)
        if self.win:
            View.victory(marker)
        else:
            View.draw()

        return None

    @staticmethod
    def process_input(user_input) -> str:
        inp = user_input.strip()
        inp = inp.lower()
        return inp

    def menu_new_game(self) -> list[int, int, str, str]:

        # number of players
        View.select_human_players()
        while True:
            user_input = self.process_input(input())

            if user_input.isnumeric():
                n_humans = int(user_input)
                if (0 <= n_humans <= 10):
                    break
            View.invalid_input()

        # number of bots
        View.select_bot_players()
        while True:
            user_input = self.process_input(input())

            if user_input.isnumeric():
                n_bots = int(user_input)
                if (0 <= n_bots <= 10):
                    break
            View.invalid_input()

        # computer strategy
        if n_bots > 0:

            View.select_strategy()
            while True:
                user_input = self.process_input(input())

                if user_input in ('0', 'easy', 'random', 'r', 'e'):
                    strategy = 'random'
                    break
                elif user_input in ('1', 'medium', 'defensive', 'd', 'med'):
                    strategy = 'defensive'
                    break
                elif user_input in ('2', 'hard', 'minmax', 'min', 'max', 'h'):
                    strategy = 'minmax'
                    if n_bots <= 1:
                        break
                    View.invalid_configuration(n_bots=n_bots,
                                               strategy=strategy)
                    continue

                View.invalid_input()

        else:
            strategy = ''

        # markers
        View.select_markers(n_humans + n_bots)
        while True:
            user_input = input()
            markers = user_input.replace(' ', '').replace('\t', '')

            incorrect_number, repeats = False, False
            if len(markers) != (n_humans + n_bots):
                incorrect_number = True
            if len(set(markers)) != len(markers):
                repeats = True

            if any((incorrect_number, repeats)):
                View.invalid_markers(incorrect_number=incorrect_number,
                                     repeats=repeats)
                continue
            else:
                break

        return n_humans, n_bots, strategy, markers

    def start_game(self) -> None:

        # Start
        View.start_screen()
        _ = input()

        initial_run = True
        reset = True
        while True:

            # Menu
            View.menu(init=initial_run)
            while True:

                user_input = self.process_input(input())
                # menu branch
                if user_input in ('1', 'start', 's'):
                    break
                elif user_input in ('0', 'end', 'quit', 'q', 'exit'):
                    return None
                elif user_input in ('2', 'reset', 're-run', 'again', 'r'):
                    reset = False
                    break
                View.invalid_input()

            # reset game state
            if reset or initial_run:
                self.players.clear()

                # New Game
                n_humans, n_bots, strategy, markers = self.menu_new_game()

                #   assign players
                bot = {'random': BotRandom,
                       'defensive': BotDefensive,
                       'minmax': BotMinmax}
                for i, m in enumerate(markers):
                    if i < n_humans:
                        self.players[m] = User(m)
                    elif i >= n_humans:
                        self.players[m] = bot[strategy](m)

            # start
            self.run_session()
            initial_run = False
            reset = True


if __name__ == "__main__":
    game_session = TicTacToe(n=3)
    game_session.start_game()
    pass
