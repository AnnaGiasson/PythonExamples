import Players
from Board import Board
# from typing import List
import TerminalView as View
from itertools import cycle


class TicTacToe():
    def __init__(self, **kwargs) -> None:
        self.players = {}
        self.board = Board(n=kwargs.get('n', 3))

    def __del__(self) -> None:
        View.close()

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
        return False

    @property
    def in_progress(self) -> bool:
        return (not self.win) and (len(self.board.vacancies()) > 0)

    def is_bot(self, player: Players.TicTacToe_Player) -> bool:
        return not isinstance(player, Players.User)

    def run_session(self) -> None:

        self.board.reset()
        player_iter = cycle(self.players.items())

        while self.in_progress:

            marker, player = next(player_iter)

            View.player_turn(marker, bot_player=self.is_bot(player))
            View.display_board(self.board)

            while True:
                try:
                    coords = player.move(self.board,
                                         players=set(self.players.keys()))
                    break
                except Players.UserExit:
                    pass
                except Players.UserHelp:
                    pass
                except Players.UserInvalidCommand:
                    View.invalid_input()
                    continue
                except Players.UserInvalidMove:
                    View.invalid_move()
                    continue

            self.board.set_elem(*coords, marker)

        View.game_over()
        View.display_board(self.board)
        View.final_result(marker, win=self.win)
        _ = input()

    @staticmethod
    def process_input(user_input) -> str:
        inp = user_input.strip()
        inp = inp.lower()
        return inp

    def menu_new_game(self) -> tuple[int, int, str, str]:

        View.new_game()

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

    def start(self) -> None:

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
                bot = {'random': Players.BotRandom,
                       'defensive': Players.BotDefensive,
                       'minmax': Players.BotMinmax}

                for m in markers:
                    if n_humans:
                        self.players[m] = Players.User(m)
                        n_humans -= 1
                    elif n_bots:
                        self.players[m] = bot[strategy](m)
                        n_bots -= 1

            # start
            self.run_session()
            initial_run = False
            reset = True


if __name__ == "__main__":
    game_session = TicTacToe(n=3)
    game_session.start()
    pass
