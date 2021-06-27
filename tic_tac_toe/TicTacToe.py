import Players
from Board import Board
import TerminalView as View
from itertools import cycle
from typing import Dict


class TicTacToe():

    supported_bots = {agent.keys(): agent for agent in Players.valid_agents}

    def __init__(self, **kwargs) -> None:
        self.players = {}

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
        val = issubclass(player, Players.TicTacToe_Player)
        val &= (not issubclass(player, Players.User))
        return val

    def is_bot_instance(self, player: Players.TicTacToe_Player) -> bool:
        val = isinstance(player, Players.TicTacToe_Player)
        val &= (not isinstance(player, Players.User))
        return val

    def run_session(self) -> None:

        self.board.reset()
        player_iter = cycle(self.players.items())
        player_list = list(self.players.keys())

        while self.in_progress:

            marker, player = next(player_iter)

            View.player_turn(marker, bot_player=self.is_bot_instance(player))
            View.display_board(self.board)

            while True:
                try:
                    coords = player.move(self.board, players=player_list)
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

    def menu_new_game(self) -> Dict:

        options = {}

        View.new_game()

        # board size
        View.select_board_size()
        while True:
            user_input = self.process_input(input())

            if user_input.isnumeric():
                options['board_size'] = int(user_input)
                if (2 <= options['board_size'] <= 100):
                    break
            elif user_input == '':
                options['board_size'] = 3
                break
            View.invalid_input()

        # number of players
        View.select_human_players()
        while True:
            user_input = self.process_input(input())

            if user_input.isnumeric():
                options['n_humans'] = int(user_input)
                if (0 <= options['n_humans'] <= 10):
                    break
            View.invalid_input()

        # number of bots
        View.select_bot_players()
        while True:
            user_input = self.process_input(input())

            if user_input.isnumeric():
                options['n_bots'] = int(user_input)
                if (0 <= options['n_bots'] <= 10):
                    break
            View.invalid_input()

        # computer strategy
        if options['n_bots'] > 0:

            supported_agents = self.supported_bots.items()
            bots = {k: a for k, a in supported_agents if self.is_bot(a)}
            View.select_strategy(bots)
            while options.get('strategy') is None:
                user_input = self.process_input(input())

                for keys, agent in bots.items():
                    if user_input in (k.lower() for k in keys):
                        options['strategy'] = agent.keys()
                        break
                else:
                    View.invalid_input()

        else:
            options['strategy'] = ''

        # markers
        View.select_markers(options['n_humans'] + options['n_bots'])
        while True:
            user_input = input()
            markers = user_input.replace(' ', '').replace('\t', '')

            incorrect_number, repeats = False, False
            if len(markers) != (options['n_humans'] + options['n_bots']):
                incorrect_number = True
            if len(set(markers)) != len(markers):
                repeats = True

            if any((incorrect_number, repeats)):
                View.invalid_markers(incorrect_number=incorrect_number,
                                     repeats=repeats)
                continue
            else:
                break
        options['markers'] = markers

        return options

    def start(self) -> None:

        # Start
        View.start_screen()
        _ = input()

        initial_run = True
        reset = True
        while True:  # event loop

            # Menu
            View.menu(init=initial_run)
            while True:  # menu loop

                user_input = self.process_input(input())
                # menu branch
                if user_input in ('1', 'start', 's'):
                    break
                elif user_input in ('0', 'end', 'quit', 'q', 'exit'):
                    return None
                elif user_input in ('2', 'restart', 'reset', 're-run', 'r'):
                    reset = False
                    break
                View.invalid_input()

            # reset game state
            if reset or initial_run:
                self.players.clear()

                # New Game
                game_options = self.menu_new_game()

                if hasattr(self, 'board'):
                    if game_options['board_size'] != self.board.board_size:
                        del self.board
                        self.board = Board(n=game_options['board_size'])
                else:
                    self.board = Board(n=game_options['board_size'])

                #   assign players
                # bot = {'random': Players.BotRandom,
                #        'defensive': Players.BotDefensive,
                #        'maximumlikelihood': Players.BotMaxLikelihood,
                #        }

                for marker in game_options['markers']:
                    if game_options['n_humans']:
                        self.players[marker] = Players.User(marker)
                        game_options['n_humans'] -= 1
                    elif game_options['n_bots']:
                        agent = self.supported_bots[game_options['strategy']]
                        self.players[marker] = agent(marker)
                        game_options['n_bots'] -= 1

            # start
            self.run_session()
            initial_run = False
            reset = True


if __name__ == "__main__":
    game_session = TicTacToe()
    game_session.start()
